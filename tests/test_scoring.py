from app.models.schemas import IntakeCreate
from app.services.lead_scoring import department_for_score, heuristic_score, urgency_for_score


def _intake(**kwargs) -> IntakeCreate:
    base = dict(
        customer_name="Pat Kim",
        email="pat@example.com",
        project_description="Please automate our weekly invoicing.",
    )
    base.update(kwargs)
    return IntakeCreate(**base)


def test_lead_scoring_complete_high_value():
    intake = _intake(
        company="Globex Enterprise",
        phone="555-0100",
        service_requested="Invoice automation",
        budget="$120k",
        deadline="2026-10-01",
        project_description=(
            "Urgent: we need enterprise invoice automation immediately. "
            "Fortune 500 supplier network, nationwide rollout, six-figure budget already approved. "
            "Please include Slack alerts and a dashboard. Leadership wants this as soon as possible."
        ),
    )
    score = heuristic_score(intake)
    assert score >= 80
    assert department_for_score(score) == "enterprise_sales"


def test_lead_scoring_sparse_lead_is_nurture():
    intake = _intake(project_description="hi can you help with a thing")
    score = heuristic_score(intake)
    assert score < 50
    assert department_for_score(score) == "nurture"
    assert urgency_for_score(score) == "low"


def test_lead_scoring_mid_range():
    intake = _intake(
        company="Local Bakery",
        phone="555-0199",
        service_requested="Website form",
        budget="$8k",
        deadline="Q4",
        project_description="We would like a contact form that emails new catering requests to the owner.",
    )
    score = heuristic_score(intake)
    assert 50 <= score < 80
    assert department_for_score(score) == "sales"
