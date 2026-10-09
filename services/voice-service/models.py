import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class VoiceSession(Base):
    __tablename__ = "voice_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    conversation_id = Column(UUID(as_uuid=True), nullable=True)
    device_id = Column(String(255), nullable=False)
    speaker_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="active")  # active | ended | interrupted
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
