"""Public health check, including database ping."""

from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter

from app.core.config import get_settings
from app.db.database import db_healthy
from app.models.schemas import HealthOut

log = logging.getLogger("intake.health")
router = APIRouter(tags=["health"])


def _ollama_up() -> bool:
    settings = get_settings()
    try:
        r = httpx.get(f"{settings.ollama_url.rstrip('/')}/api/tags", timeout=2.0)
        return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    settings = get_settings()
    db_ok = db_healthy()
    ollama = None
    if settings.ai_provider == "ollama":
        ollama = _ollama_up()
    status = "ok" if db_ok else "degraded"
    if not db_ok:
        log.error("health: database unreachable")
    return HealthOut(
        ok=db_ok,
        status=status,
        db=db_ok,
        ai_provider=settings.ai_provider,
        model=settings.ollama_model if settings.ai_provider == "ollama" else settings.openai_model,
        ollama=ollama,
    )
