"""LLM intake analysis. Ollama default, OpenAI optional. Pydantic-validated JSON."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_request_id
from app.models.schemas import AIAnalysis, IntakeCreate

log = logging.getLogger("intake.ai")

JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.I)

SYSTEM_PROMPT = """You are an operations intake analyst for a software/automation agency.
Return ONLY valid JSON (no markdown) matching this schema:
{
  "summary": "2-3 sentence restatement of the request",
  "category": "short category e.g. automation, web, data, integration, consulting",
  "urgency": "low|medium|high|critical",
  "lead_score": 0-100 integer,
  "sentiment": "positive|neutral|negative|mixed",
  "recommended_action": "what the team should do next",
  "assigned_department": "enterprise_sales|sales|nurture|engineering|support",
  "follow_up_message": "a short professional reply the team could send",
  "missing_information": ["list of gaps"],
  "risk_flags": ["list of risks or empty"]
}
Score higher for clear budget, deadline, decision-maker, and enterprise scope.
Flag risks like unrealistic timeline, missing budget, or vague scope.
"""


def build_user_prompt(intake: IntakeCreate) -> str:
    return (
        f"Customer: {intake.customer_name}\n"
        f"Company: {intake.company or 'n/a'}\n"
        f"Email: {intake.email}\n"
        f"Phone: {intake.phone or 'n/a'}\n"
        f"Service requested: {intake.service_requested or 'n/a'}\n"
        f"Budget: {intake.budget or 'n/a'}\n"
        f"Deadline: {intake.deadline or 'n/a'}\n"
        f"Source: {intake.source}\n"
        f"Project description:\n{intake.project_description}\n"
    )


def parse_ai_json(text: str) -> AIAnalysis:
    """Extract JSON from model text and validate against AIAnalysis."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("empty model response")
    fence = JSON_FENCE.search(raw)
    if fence:
        raw = fence.group(1).strip()
    else:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            raw = raw[start : end + 1]
    data: Any = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("model JSON was not an object")
    return AIAnalysis.model_validate(data)


def _sleep(attempt: int) -> None:
    if get_settings().is_test:
        return
    time.sleep(0.35 * attempt)


def _post_with_retries(url: str, **kwargs: Any) -> httpx.Response:
    settings = get_settings()
    last: Exception | None = None
    attempts = max(1, settings.ai_max_retries)
    for attempt in range(1, attempts + 1):
        try:
            response = httpx.post(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as exc:  # noqa: BLE001
            last = exc
            log.warning(
                "AI HTTP attempt %s/%s failed: %s",
                attempt,
                attempts,
                exc,
            )
            if attempt < attempts:
                _sleep(attempt)
    raise RuntimeError(f"AI HTTP failed after {attempts} attempts: {last}") from last


def _call_ollama(prompt: str) -> str:
    settings = get_settings()
    url = f"{settings.ollama_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
        "stream": False,
        "format": "json",
    }
    response = _post_with_retries(url, json=payload, timeout=settings.ai_timeout_seconds)
    text = (response.json().get("response") or "").strip()
    if not text:
        raise RuntimeError("empty Ollama response")
    return text


def _call_openai(prompt: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openai_model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    response = _post_with_retries(
        url, json=payload, headers=headers, timeout=settings.ai_timeout_seconds
    )
    body = response.json()
    text = (
        body.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        or ""
    ).strip()
    if not text:
        raise RuntimeError("empty OpenAI response")
    return text


def analyze_intake(intake: IntakeCreate) -> AIAnalysis | None:
    """Return validated AI analysis, or None so the caller can store needs_review."""
    settings = get_settings()
    prompt = build_user_prompt(intake)
    log.info(
        "analyzing intake provider=%s request_id=%s",
        settings.ai_provider,
        get_request_id(),
    )
    try:
        if settings.ai_provider == "openai":
            text = _call_openai(prompt)
        else:
            text = _call_ollama(prompt)
        return parse_ai_json(text)
    except Exception as exc:  # noqa: BLE001
        log.error("AI analysis failed: %s", exc)
        return None
