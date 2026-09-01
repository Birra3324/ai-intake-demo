"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

Urgency = Literal["low", "medium", "high", "critical"]
LeadStatus = Literal[
    "received",
    "processed",
    "needs_review",
    "contacted",
    "qualified",
    "closed",
    "rejected",
]


class IntakeCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    company: str | None = Field(default=None, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    service_requested: str | None = Field(default=None, max_length=200)
    budget: str | None = Field(default=None, max_length=80)
    project_description: str = Field(min_length=3, max_length=8000)
    deadline: str | None = Field(default=None, max_length=80)
    source: str = Field(default="api", max_length=80)

    @field_validator("customer_name", "project_description")
    @classmethod
    def strip_required(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("company", "phone", "service_requested", "budget", "deadline")
    @classmethod
    def empty_to_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None


class LegacyIntakeIn(BaseModel):
    """Phase-1 webhook shape. Mapped onto IntakeCreate."""

    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    message: str = Field(min_length=3, max_length=8000)
    source: str = Field(default="webhook", max_length=80)
    company: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=40)
    service_requested: str | None = Field(default=None, max_length=200)
    budget: str | None = Field(default=None, max_length=80)
    deadline: str | None = Field(default=None, max_length=80)

    def to_intake(self) -> IntakeCreate:
        return IntakeCreate(
            customer_name=self.name,
            company=self.company,
            email=self.email,
            phone=self.phone,
            service_requested=self.service_requested,
            budget=self.budget,
            project_description=self.message,
            deadline=self.deadline,
            source=self.source or "webhook",
        )


class AIAnalysis(BaseModel):
    summary: str = Field(min_length=1, max_length=4000)
    category: str = Field(min_length=1, max_length=80)
    urgency: Urgency
    lead_score: int = Field(ge=0, le=100)
    sentiment: str = Field(min_length=1, max_length=40)
    recommended_action: str = Field(min_length=1, max_length=2000)
    assigned_department: str = Field(min_length=1, max_length=80)
    follow_up_message: str = Field(min_length=1, max_length=4000)
    missing_information: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class LeadUpdate(BaseModel):
    status: LeadStatus | None = None
    assigned_department: str | None = Field(default=None, max_length=80)
    follow_up_message: str | None = Field(default=None, max_length=4000)


class LeadOut(BaseModel):
    id: str
    customer_name: str
    company: str | None
    email: str
    phone: str | None
    service_requested: str | None
    budget: str | None
    project_description: str
    deadline: str | None
    source: str
    summary: str | None
    category: str | None
    urgency: str | None
    lead_score: int | None
    sentiment: str | None
    recommended_action: str | None
    assigned_department: str | None
    follow_up_message: str | None
    missing_information: list[str] | None
    risk_flags: list[str] | None
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class IntakeResponse(BaseModel):
    id: str
    status: str
    lead_score: int | None
    urgency: str | None
    assigned_department: str | None
    summary: str | None
    recommended_action: str | None
    request_id: str


class HealthOut(BaseModel):
    ok: bool
    status: str
    db: bool
    ai_provider: str
    model: str
    ollama: bool | None = None
