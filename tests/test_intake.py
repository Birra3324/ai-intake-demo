from unittest.mock import patch

from app.models.schemas import AIAnalysis
from tests.conftest import AUTH, MOCK_AI_JSON, VALID_INTAKE


def _ai():
    return AIAnalysis.model_validate(MOCK_AI_JSON)


def test_successful_intake_mocked_ai(client):
    with patch("app.services.database_service.analyze_intake", return_value=_ai()):
        r = client.post("/api/v1/intake", json=VALID_INTAKE, headers=AUTH)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "processed"
    assert body["lead_score"] == 86
    assert body["urgency"] == "high"
    assert body["assigned_department"] == "enterprise_sales"
    assert body["summary"]
    assert body["id"]
    assert body["request_id"]


def test_legacy_webhook_alias(client):
    payload = {
        "name": "Sam Lee",
        "email": "sam@example.com",
        "message": "Need a Zapier replacement for invoice routing.",
        "source": "webhook",
    }
    with patch("app.services.database_service.analyze_intake", return_value=_ai()):
        r = client.post("/webhook/intake", json=payload, headers=AUTH)
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "processed"


def test_invalid_payload(client):
    r = client.post(
        "/api/v1/intake",
        json={"customer_name": "", "email": "bad", "project_description": "x"},
        headers=AUTH,
    )
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "Validation failed"
    assert "request_id" in body


def test_failed_ai_still_stores_needs_review(client):
    with patch("app.services.database_service.analyze_intake", return_value=None):
        r = client.post("/api/v1/intake", json=VALID_INTAKE, headers=AUTH)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "needs_review"
    assert body["lead_score"] is not None
    assert 0 <= body["lead_score"] <= 100
    assert body["summary"] is None

    listed = client.get("/api/v1/leads", headers=AUTH)
    assert listed.status_code == 200
    rows = listed.json()
    assert len(rows) == 1
    assert rows[0]["status"] == "needs_review"
    assert rows[0]["id"] == body["id"]


def test_database_persistence(client):
    with patch("app.services.database_service.analyze_intake", return_value=_ai()):
        created = client.post("/api/v1/intake", json=VALID_INTAKE, headers=AUTH)
    assert created.status_code == 201
    lead_id = created.json()["id"]

    fetched = client.get(f"/api/v1/leads/{lead_id}", headers=AUTH)
    assert fetched.status_code == 200
    row = fetched.json()
    assert row["customer_name"] == VALID_INTAKE["customer_name"]
    assert row["email"] == VALID_INTAKE["email"]
    assert row["lead_score"] == 86
    assert row["ai_response"] if False else row["summary"]  # summary persisted
    assert row["raw_intake"] if False else row["project_description"] == VALID_INTAKE["project_description"]

    patched = client.patch(
        f"/api/v1/leads/{lead_id}",
        json={"status": "contacted"},
        headers=AUTH,
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "contacted"

    missing = client.get("/api/v1/leads/does-not-exist", headers=AUTH)
    assert missing.status_code == 404
