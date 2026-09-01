"""Application factory. Keep this module importable as `app.main:app`."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.routes import health, intake, leads
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import RequestIdMiddleware, setup_logging
from app.db.database import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)
    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Webhook intake → LLM structured analysis → lead scoring → routing.",
        lifespan=lifespan,
    )
    application.add_middleware(RequestIdMiddleware)
    register_exception_handlers(application)
    application.include_router(health.router)
    application.include_router(intake.router)
    application.include_router(leads.router)
    return application


app = create_app()
