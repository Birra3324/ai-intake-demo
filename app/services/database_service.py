"""Lead persistence and intake processing (AI → score → store → notify)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.schemas import IntakeCreate, LeadUpdate
from app.services.ai_service import analyze_intake
from app.services.lead_scoring import department_for_score, heuristic_score, urgency_for_score
from app.services.notification_service import notify_high_value

log = logging.getLogger("intake.db")


def create_lead_from_intake(db: Session, intake: IntakeCreate) -> Lead:
    ai = analyze_intake(intake)
    heuristic = heuristic_score(intake)

    if ai is not None:
        status = "processed"
        score = ai.lead_score
        department = ai.assigned_department
        urgency = ai.urgency
        summary = ai.summary
        ai_dump: dict | None = ai.model_dump()
        log.info("AI analysis accepted score=%s category=%s", score, ai.category)
    else:
        status = "needs_review"
        score = heuristic
        department = department_for_score(heuristic)
        urgency = urgency_for_score(heuristic)
        summary = None
        ai_dump = None
        log.warning("AI unavailable; storing needs_review heuristic_score=%s", heuristic)

    lead = Lead(
        customer_name=intake.customer_name,
        company=intake.company,
        email=str(intake.email),
        phone=intake.phone,
        service_requested=intake.service_requested,
        budget=intake.budget,
        project_description=intake.project_description,
        deadline=intake.deadline,
        source=intake.source,
        summary=summary if ai else None,
        category=ai.category if ai else None,
        urgency=urgency,
        lead_score=score,
        sentiment=ai.sentiment if ai else None,
        recommended_action=ai.recommended_action if ai else None,
        assigned_department=department,
        follow_up_message=ai.follow_up_message if ai else None,
        missing_information=ai.missing_information if ai else [],
        risk_flags=ai.risk_flags if ai else [],
        raw_intake=intake.model_dump(mode="json"),
        ai_response=ai_dump,
        status=status,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    log.info("lead stored id=%s status=%s score=%s", lead.id, lead.status, lead.lead_score)

    try:
        notify_high_value(lead)
    except Exception as exc:  # noqa: BLE001
        log.error("notification failed after persist: %s", exc)

    return lead


def list_leads(db: Session, *, status: str | None = None, limit: int = 50, offset: int = 0) -> list[Lead]:
    q = db.query(Lead).order_by(Lead.created_at.desc())
    if status:
        q = q.filter(Lead.status == status)
    return q.offset(offset).limit(min(limit, 200)).all()


def get_lead(db: Session, lead_id: str) -> Lead | None:
    return db.get(Lead, lead_id)


def update_lead(db: Session, lead: Lead, patch: LeadUpdate) -> Lead:
    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(lead, key, value)
    lead.updated_at = datetime.now(timezone.utc)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
