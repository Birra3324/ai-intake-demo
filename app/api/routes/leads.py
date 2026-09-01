"""Lead list / detail / patch."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.db.database import get_db
from app.models.schemas import LeadOut, LeadUpdate
from app.services.database_service import get_lead, list_leads, update_lead

router = APIRouter(
    prefix="/api/v1/leads",
    tags=["leads"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[LeadOut])
def get_leads(
    db: Session = Depends(get_db),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[LeadOut]:
    rows = list_leads(db, status=status_filter, limit=limit, offset=offset)
    return [LeadOut.model_validate(r) for r in rows]


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead_by_id(lead_id: str, db: Session = Depends(get_db)) -> LeadOut:
    lead = get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return LeadOut.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadOut)
def patch_lead(lead_id: str, payload: LeadUpdate, db: Session = Depends(get_db)) -> LeadOut:
    lead = get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    lead = update_lead(db, lead, payload)
    return LeadOut.model_validate(lead)
