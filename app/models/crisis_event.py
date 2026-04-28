import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, Boolean, ForeignKey, func, JSON, CheckConstraint
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CrisisEvent(Base):
    __tablename__ = "crisis_events"
    __table_args__ = (
        CheckConstraint("severity IN ('LOW','MEDIUM','HIGH','CRITICAL')", name="ck_crisis_severity"),
    )

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True
    )
    message_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("messages.id"), nullable=True
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    keywords_matched: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="crisis_events")  # type: ignore[name-defined]
    message: Mapped["Message | None"] = relationship(back_populates="crisis_event")  # type: ignore[name-defined]
