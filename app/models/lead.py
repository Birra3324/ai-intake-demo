"""SQLAlchemy Lead model. UUID ids, raw intake + AI JSON, timestamps."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    service_requested: Mapped[str | None] = mapped_column(String(200), nullable=True)
    budget: Mapped[str | None] = mapped_column(String(80), nullable=True)
    project_description: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="api")

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_department: Mapped[str | None] = mapped_column(String(80), nullable=True)
    follow_up_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_information: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risk_flags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    raw_intake: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(40), nullable=False, default="received", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=True
    )


class IntakeEvent(Base):
    """Replay ledger; separate table preserves existing lead schemas."""

    __tablename__ = "intake_events"
    key: Mapped[str] = mapped_column(String(200), primary_key=True)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
