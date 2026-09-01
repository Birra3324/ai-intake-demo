"""Test env must be set before app imports so settings/engine pick up SQLite + API key."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

_TMP = Path(tempfile.mkdtemp(prefix="intake-test-"))
_DB = _TMP / "test.db"

os.environ["APP_ENV"] = "test"
os.environ["API_KEY"] = "test-api-key"
os.environ["AI_PROVIDER"] = "ollama"
os.environ["OLLAMA_URL"] = "http://127.0.0.1:11434"
os.environ["OLLAMA_MODEL"] = "llama3.2"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB}"
os.environ["SLACK_WEBHOOK_URL"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["LOG_LEVEL"] = "WARNING"

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import reset_settings  # noqa: E402
from app.db.database import Base, get_engine, init_db, reset_engine  # noqa: E402
from app.main import app  # noqa: E402

reset_settings()
reset_engine()
init_db()

AUTH = {"X-API-Key": "test-api-key"}

VALID_INTAKE = {
    "customer_name": "Amina Hassan",
    "company": "Northwind Logistics",
    "email": "amina@northwind.example",
    "phone": "+1-206-555-0142",
    "service_requested": "Ops reporting automation",
    "budget": "$80k",
    "project_description": (
        "We need a weekly operations report automated from our warehouse "
        "spreadsheets into Slack and a dashboard. Urgent — leadership wants "
        "this live by the end of the month."
    ),
    "deadline": "2026-09-30",
    "source": "website",
}

MOCK_AI_JSON = {
    "summary": "Northwind wants weekly warehouse ops reports automated into Slack and a dashboard this month.",
    "category": "automation",
    "urgency": "high",
    "lead_score": 86,
    "sentiment": "positive",
    "recommended_action": "Book a 30-minute discovery call this week and send a sample dashboard.",
    "assigned_department": "enterprise_sales",
    "follow_up_message": "Thanks Amina — we can automate that reporting pipeline. Are you free Thursday?",
    "missing_information": ["current tools besides spreadsheets"],
    "risk_flags": ["tight deadline"],
}


@pytest.fixture(autouse=True)
def _fresh_db():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    return dict(AUTH)
