from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sa_update
from fastapi import HTTPException, status

from app.models.conversation import Conversation
from app.models.message import Message


async def create_conversation(db: AsyncSession, user_id: str, title: str = "New Conversation") -> Conversation:
    convo = Conversation(user_id=user_id, title=title)
    db.add(convo)
    await db.commit()
    await db.refresh(convo)
    return convo


async def get_conversations(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_conversation(db: AsyncSession, conversation_id: str, user_id: str) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return convo


async def delete_conversation(db: AsyncSession, conversation_id: str, user_id: str) -> None:
    convo = await get_conversation(db, conversation_id, user_id)
    await db.delete(convo)
    await db.commit()


async def save_message(
    db: AsyncSession,
    conversation_id: str,
    role: str,
    content: str,
    tokens_used: int = 0,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tokens_used=tokens_used,
    )
    db.add(msg)
    # Update conversation activity timestamp
    await db.execute(
        sa_update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(updated_at=datetime.now(timezone.utc))
    )
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_messages(
    db: AsyncSession,
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_recent_messages(db: AsyncSession, conversation_id: str, n: int = 10) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(n)
    )
    messages = list(result.scalars().all())
    return list(reversed(messages))  # chronological order
