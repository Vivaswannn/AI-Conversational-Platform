import logging
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chain import stream_response
from app.ai.memory import build_chat_history
from app.ai.rag import get_rag_engine
from app.models.message import Message
from app.models.crisis_event import CrisisEvent
from app.services.conversation_service import save_message, get_recent_messages
from app.services.crisis_service import CrisisDetector, CrisisSeverity

logger = logging.getLogger(__name__)
_crisis_detector = CrisisDetector()


async def _log_crisis_event(
    db: AsyncSession,
    user_id: str,
    message_id: str,
    severity: CrisisSeverity,
    keywords: list[str],
) -> None:
    event = CrisisEvent(
        user_id=user_id,
        message_id=message_id,
        severity=severity.value,
        keywords_matched=keywords if keywords else None,
    )
    db.add(event)
    await db.commit()
    logger.warning("Crisis event logged: user=%s severity=%s", user_id, severity)


async def process_message_streaming(
    db: AsyncSession,
    user_id: str,
    conversation_id: str,
    user_content: str,
) -> AsyncIterator[str]:
    """
    Orchestrate the full pipeline for a user message.
    Yields tokens. The final AI message is saved to DB after iteration completes.
    Caller must exhaust the iterator to ensure the message is saved.
    """
    # 1. Save user message
    user_msg: Message = await save_message(db, conversation_id, "user", user_content)

    # 2. Crisis detection
    severity, matched_keywords = await _crisis_detector.detect(user_content)

    if severity in (CrisisSeverity.CRITICAL, CrisisSeverity.HIGH, CrisisSeverity.MEDIUM):
        safety_text = _crisis_detector.get_safety_response(severity)
        await save_message(db, conversation_id, "assistant", safety_text)
        await _log_crisis_event(db, user_id, user_msg.id, severity, matched_keywords)
        yield safety_text
        return

    # 3. Load conversation history (last 10 messages)
    recent = await get_recent_messages(db, conversation_id, n=10)
    history = build_chat_history(recent)

    # 4. RAG retrieval
    try:
        rag = get_rag_engine()
        context_chunks = rag.query(user_content)
    except Exception:
        logger.exception("RAG retrieval failed; proceeding without context")
        context_chunks = []

    # 5. Stream LLM response
    tokens: list[str] = []
    try:
        async for token in stream_response(history, context_chunks, user_content):
            tokens.append(token)
            yield token
    except Exception:
        logger.exception("LLM error during streaming")
        error_msg = "I'm sorry, I'm having trouble responding right now. Please try again in a moment."
        await save_message(db, conversation_id, "assistant", error_msg)
        yield error_msg
        return

    # 6. Save AI response
    full_response = "".join(tokens)
    await save_message(db, conversation_id, "assistant", full_response)

    # 7. Log LOW severity events (non-blocking)
    if severity == CrisisSeverity.LOW:
        await _log_crisis_event(db, user_id, user_msg.id, severity, matched_keywords)


async def process_message(
    db: AsyncSession,
    user_id: str,
    conversation_id: str,
    user_content: str,
) -> tuple:
    """Non-streaming variant — collects all tokens and returns (user_msg, ai_msg)."""
    from app.models.message import Message as _Message

    tokens: list[str] = []

    # Save user message first so we can track it
    user_msg_obj: _Message = await save_message(db, conversation_id, "user", user_content)
    saved_user_msg = user_msg_obj

    severity, matched_keywords = await _crisis_detector.detect(user_content)

    if severity in (CrisisSeverity.CRITICAL, CrisisSeverity.HIGH, CrisisSeverity.MEDIUM):
        safety_text = _crisis_detector.get_safety_response(severity)
        ai_msg_obj = await save_message(db, conversation_id, "assistant", safety_text)
        await _log_crisis_event(db, user_id, saved_user_msg.id, severity, matched_keywords)
        return saved_user_msg, ai_msg_obj

    recent = await get_recent_messages(db, conversation_id, n=10)
    history = build_chat_history(recent)
    try:
        rag = get_rag_engine()
        context_chunks = rag.query(user_content)
    except Exception:
        logger.exception("RAG retrieval failed; proceeding without context")
        context_chunks = []

    try:
        async for token in stream_response(history, context_chunks, user_content):
            tokens.append(token)
    except Exception:
        logger.exception("LLM error")
        error_msg = "I'm sorry, I'm having trouble responding right now. Please try again in a moment."
        ai_msg_obj = await save_message(db, conversation_id, "assistant", error_msg)
        return saved_user_msg, ai_msg_obj

    full_response = "".join(tokens)
    ai_msg_obj = await save_message(db, conversation_id, "assistant", full_response)

    if severity == CrisisSeverity.LOW:
        await _log_crisis_event(db, user_id, saved_user_msg.id, severity, matched_keywords)

    return saved_user_msg, ai_msg_obj
