import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from app.models.schemas import AIAnalysis, IntakeCreate
from app.services.ai_service import analyze_intake, parse_ai_json
from tests.conftest import MOCK_AI_JSON, VALID_INTAKE


def test_ai_response_validation_accepts_valid_json():
    parsed = parse_ai_json(json.dumps(MOCK_AI_JSON))
    assert parsed.lead_score == 86
    assert parsed.urgency == "high"


def test_ai_response_validation_strips_fences():
    blob = "```json\n" + json.dumps(MOCK_AI_JSON) + "\n```"
    parsed = parse_ai_json(blob)
    assert parsed.category == "automation"


def test_ai_response_validation_rejects_bad_urgency():
    bad = dict(MOCK_AI_JSON, urgency="super-duper")
    with pytest.raises(ValidationError):
        AIAnalysis.model_validate(bad)


def test_ai_response_validation_rejects_score_out_of_range():
    bad = dict(MOCK_AI_JSON, lead_score=140)
    with pytest.raises(ValidationError):
        AIAnalysis.model_validate(bad)


def test_analyze_intake_returns_none_on_invalid_model_json():
    fake = MagicMock()
    fake.json.return_value = {"response": "not-json"}
    fake.raise_for_status = MagicMock()
    with patch("app.services.ai_service._post_with_retries", return_value=fake):
        result = analyze_intake(IntakeCreate(**VALID_INTAKE))
    assert result is None


def test_analyze_intake_returns_none_on_http_failure():
    with patch("app.services.ai_service._post_with_retries", side_effect=RuntimeError("boom")):
        result = analyze_intake(IntakeCreate(**VALID_INTAKE))
    assert result is None


def test_analyze_intake_parses_good_http_response():
    fake = MagicMock()
    fake.json.return_value = {"response": json.dumps(MOCK_AI_JSON)}
    fake.raise_for_status = MagicMock()
    with patch("app.services.ai_service._post_with_retries", return_value=fake):
        result = analyze_intake(IntakeCreate(**VALID_INTAKE))
    assert result is not None
    assert result.lead_score == 86
