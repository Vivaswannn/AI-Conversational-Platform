from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationOut
from app.schemas.message import ChatRequest, ChatResponse
from app.services import conversation_service, chat_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await conversation_service.create_conversation(db, current_user.id, body.title)


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await conversation_service.get_conversations(db, current_user.id)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await conversation_service.get_conversation(db, conversation_id, current_user.id)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await conversation_service.delete_conversation(db, conversation_id, current_user.id)


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: str,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Non-streaming REST endpoint — returns user message and AI response."""
    await conversation_service.get_conversation(db, conversation_id, current_user.id)
    user_msg, ai_msg = await chat_service.process_message(
        db, current_user.id, conversation_id, body.content
    )
    return ChatResponse(message=user_msg, response=ai_msg)
