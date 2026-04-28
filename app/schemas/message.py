from datetime import datetime
from pydantic import BaseModel, field_validator


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    tokens_used: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        v = v.replace("\x00", "")  # strip null bytes before length check
        if not v:
            raise ValueError("Message content cannot be empty")
        if len(v) > 4000:
            raise ValueError("Message content exceeds 4000 character limit")
        return v


class ChatResponse(BaseModel):
    message: MessageOut
    response: MessageOut
