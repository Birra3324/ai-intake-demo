from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch
import logging
import pytest
from fastapi.testclient import TestClient
from app.core.config import get_settings
from app.main import app
from app.db.database import get_session_factory
from app.models.lead import Lead
from app.services.database_service import create_lead_from_intake
from app.models.schemas import IntakeCreate
from tests.conftest import AUTH, VALID_INTAKE


def test_missing_configuration_fails_closed(client, monkeypatch):
    monkeypatch.setattr(get_settings(), 'api_key', '')
    assert client.get('/api/v1/leads', headers=AUTH).status_code == 503
    with pytest.raises(RuntimeError, match='API_KEY'):
        with TestClient(app):
            pass


def test_replay_and_conflict(client):
    headers = {**AUTH, 'Idempotency-Key': 'event-1'}
    with patch('app.services.database_service.analyze_intake', return_value=None) as ai, patch('app.services.database_service.notify_high_value') as notify:
        first = client.post('/api/v1/intake', json=VALID_INTAKE, headers=headers)
        again = client.post('/api/v1/intake', json=VALID_INTAKE, headers=headers)
        conflict = client.post('/api/v1/intake', json={**VALID_INTAKE,'budget':'different'}, headers=headers)
    assert first.status_code == again.status_code == 201
    assert first.json()['id'] == again.json()['id']
    assert conflict.status_code == 409
    assert ai.call_count == notify.call_count == 1


def test_concurrent_replay_single_record_and_notification():
    barrier = Barrier(2)
    def analyze(_):
        barrier.wait(timeout=5)
        return None
    def run():
        with get_session_factory()() as db:
            return create_lead_from_intake(db, IntakeCreate.model_validate(VALID_INTAKE), 'parallel-event').id
    with patch('app.services.database_service.analyze_intake', side_effect=analyze), patch('app.services.database_service.notify_high_value') as notify:
        with ThreadPoolExecutor(max_workers=2) as pool:
            ids = list(pool.map(lambda _:run(), range(2)))
        assert ids[0] == ids[1]
        assert notify.call_count == 1
    with get_session_factory()() as db:
        assert db.query(Lead).count() == 1


def test_logs_exclude_customer_fields(client, caplog):
    caplog.set_level(logging.INFO)
    with patch('app.services.database_service.analyze_intake', return_value=None):
        assert client.post('/api/v1/intake', json=VALID_INTAKE, headers=AUTH).status_code == 201
    for field in ('email','customer_name','company','project_description'):
        assert VALID_INTAKE[field] not in caplog.text

@pytest.mark.parametrize('status_code,expected_calls', [(401,1),(429,3),(503,3)])
def test_selective_provider_retries(status_code, expected_calls):
    import httpx
    from app.services.ai_service import _post_with_retries
    response = httpx.Response(status_code, request=httpx.Request('POST','https://example.test/model'))
    with patch('app.services.ai_service.httpx.post', return_value=response) as post:
        with pytest.raises((RuntimeError,httpx.HTTPStatusError)):
            _post_with_retries('https://example.test/model')
    assert post.call_count == expected_calls
