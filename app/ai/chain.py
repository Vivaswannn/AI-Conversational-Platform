import logging
from collections.abc import AsyncIterator

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.ai.prompts import CONTEXT_TEMPLATE, SYSTEM_PROMPT
from app.config import get_settings

logger = logging.getLogger(__name__)


def _has_usable_openai_key(api_key: str) -> bool:
    key = (api_key or "").strip().lower()
    return bool(key) and "placeholder" not in key and key != "sk-..."


def _fallback_response(user_message: str) -> str:
    return (
        "I can still help with supportive guidance even without an AI provider key. "
        f"You said: \"{user_message}\". "
        "A practical next step is to break this into one small action you can do in 10 minutes, "
        "then reassess how you feel."
    )


def build_chain_input(
    history: list[BaseMessage],
    context_chunks: list[str],
    user_message: str,
) -> dict:
    context = "\n\n".join(context_chunks) if context_chunks else ""
    return {
        "history": history,
        "context": context,
        "user_message": user_message,
    }


def _build_messages(history: list[BaseMessage], context: str, user_message: str) -> list[BaseMessage]:
    system_content = SYSTEM_PROMPT
    if context:
        system_content += "\n\n" + CONTEXT_TEMPLATE.format(context=context)

    messages: list[BaseMessage] = [SystemMessage(content=system_content)]
    messages.extend(history)
    messages.append(HumanMessage(content=user_message))
    return messages


async def stream_response(
    history: list[BaseMessage],
    context_chunks: list[str],
    user_message: str,
) -> AsyncIterator[str]:
    settings = get_settings()
    if not _has_usable_openai_key(settings.OPENAI_API_KEY):
        # Resume-project friendly fallback mode when no valid provider key is configured.
        yield _fallback_response(user_message)
        return

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        streaming=True,
        temperature=0.7,
        max_tokens=1024,
    )

    chain_input = build_chain_input(history, context_chunks, user_message)
    messages = _build_messages(
        chain_input["history"],
        chain_input["context"],
        chain_input["user_message"],
    )

    try:
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content
    except Exception:
        logger.exception("LLM streaming error")
        raise


async def get_full_response(
    history: list[BaseMessage],
    context_chunks: list[str],
    user_message: str,
) -> str:
    tokens: list[str] = []
    async for token in stream_response(history, context_chunks, user_message):
        tokens.append(token)
    return "".join(tokens)
