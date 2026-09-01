"""Intake endpoints: /api/v1/intake plus legacy /webhook/intake alias."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.logging import get_request_id
from app.core.security import require_api_key
from app.db.database import get_db
from app.models.schemas import IntakeCreate, IntakeResponse, LegacyIntakeIn
from app.services.database_service import create_lead_from_intake

log = logging.getLogger("intake.api")
router = APIRouter(tags=["intake"])


def _respond(lead, request: Request) -> IntakeResponse:
    rid = getattr(request.state, "request_id", None) or get_request_id()
    return IntakeResponse(
        id=lead.id,
        status=lead.status,
        lead_score=lead.lead_score,
        urgency=lead.urgency,
        assigned_department=lead.assigned_department,
        summary=lead.summary,
        recommended_action=lead.recommended_action,
        request_id=rid,
    )


@router.post(
    "/api/v1/intake",
    response_model=IntakeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_intake(
    payload: IntakeCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> IntakeResponse:
    log.info(
        "intake received customer=%s company=%s source=%s",
        payload.customer_name,
        payload.company,
        payload.source,
    )
    lead = create_lead_from_intake(db, payload)
    return _respond(lead, request)


@router.post(
    "/webhook/intake",
    response_model=IntakeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
    summary="Legacy webhook alias (phase-1 payload: name, email, message, source)",
)
def legacy_webhook_intake(
    payload: LegacyIntakeIn,
    request: Request,
    db: Session = Depends(get_db),
) -> IntakeResponse:
    log.info("legacy webhook intake name=%s source=%s", payload.name, payload.source)
    lead = create_lead_from_intake(db, payload.to_intake())
    return _respond(lead, request)
