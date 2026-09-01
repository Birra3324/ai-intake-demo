from unittest.mock import patch

from app.models.schemas import AIAnalysis
from tests.conftest import AUTH, MOCK_AI_JSON, VALID_INTAKE


def test_auth_failure_missing_key(client):
    r = client.post("/api/v1/intake", json=VALID_INTAKE)
    assert r.status_code == 401
    assert r.json()["error"] == "Invalid or missing API key"


def test_auth_failure_wrong_key(client):
    r = client.post("/api/v1/intake", json=VALID_INTAKE, headers={"X-API-Key": "nope"})
    assert r.status_code == 401


def test_leads_get_requires_key(client):
    r = client.get("/api/v1/leads")
    assert r.status_code == 401


def test_patch_requires_key(client):
    with patch(
        "app.services.database_service.analyze_intake",
        return_value=AIAnalysis.model_validate(MOCK_AI_JSON),
    ):
        created = client.post("/api/v1/intake", json=VALID_INTAKE, headers=AUTH)
    lead_id = created.json()["id"]
    r = client.patch(f"/api/v1/leads/{lead_id}", json={"status": "closed"})
    assert r.status_code == 401
