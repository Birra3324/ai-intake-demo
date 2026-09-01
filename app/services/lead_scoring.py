"""Deterministic heuristic scoring used as fallback and as a floor check."""

from __future__ import annotations

import re

from app.models.schemas import IntakeCreate

HIGH_BUDGET_HINTS = re.compile(
    r"\b(\d{2,3}\s*k|\$?\s*(5\d{4,}|[1-9]\d{5,})|enterprise|six.?figure)\b",
    re.I,
)
URGENCY_WORDS = (
    "urgent",
    "asap",
    "immediately",
    "critical",
    "this week",
    "end of week",
    "as soon as",
    "right away",
)
ENTERPRISE_WORDS = ("enterprise", "series", "fortune", "global", "nationwide")


def heuristic_score(intake: IntakeCreate) -> int:
    score = 35
    if intake.company:
        score += 8
    if intake.phone:
        score += 6
    if intake.service_requested:
        score += 6
    if intake.deadline:
        score += 5
    if intake.budget:
        score += 10
        if HIGH_BUDGET_HINTS.search(intake.budget):
            score += 15
    desc = (intake.project_description or "").lower()
    company = (intake.company or "").lower()
    if any(w in desc for w in URGENCY_WORDS):
        score += 15
    if any(w in desc or w in company for w in ENTERPRISE_WORDS):
        score += 8
    length = len(intake.project_description)
    if length > 400:
        score += 5
    elif length < 40:
        score -= 8
    return max(0, min(100, score))


def department_for_score(score: int) -> str:
    if score >= 80:
        return "enterprise_sales"
    if score >= 50:
        return "sales"
    return "nurture"


def urgency_for_score(score: int) -> str:
    if score >= 90:
        return "critical"
    if score >= 80:
        return "high"
    if score >= 50:
        return "medium"
    return "low"
