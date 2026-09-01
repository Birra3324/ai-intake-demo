"""Slack webhook + optional SMTP. If unset, log the payload so tests still cover it."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import TYPE_CHECKING

import httpx

from app.core.config import get_settings
from app.core.logging import get_request_id

if TYPE_CHECKING:
    from app.models.lead import Lead

log = logging.getLogger("intake.notify")


def _payload(lead: Lead) -> dict:
    return {
        "customer": lead.customer_name,
        "company": lead.company,
        "email": lead.email,
        "score": lead.lead_score,
        "urgency": lead.urgency,
        "service": lead.service_requested,
        "request": (lead.project_description or "")[:400],
        "recommended_action": lead.recommended_action,
        "department": lead.assigned_department,
        "status": lead.status,
        "lead_id": lead.id,
        "request_id": get_request_id(),
    }


def _slack_text(lead: Lead) -> str:
    company = lead.company or "n/a"
    lines = [
        f"*High-value intake* `{lead.id}`",
        f"• Customer: {lead.customer_name} ({company})",
        f"• Score: {lead.lead_score}  Urgency: {lead.urgency}",
        f"• Service: {lead.service_requested or 'n/a'}",
        f"• Action: {lead.recommended_action or 'review manually'}",
        f"• Email: {lead.email}",
    ]
    return "\n".join(lines)


def send_slack(lead: Lead) -> bool:
    settings = get_settings()
    body = {"text": _slack_text(lead)}
    url = (settings.slack_webhook_url or "").strip()
    if not url:
        log.info("slack skipped (SLACK_WEBHOOK_URL unset) payload=%s", _payload(lead))
        return False
    try:
        r = httpx.post(url, json=body, timeout=8.0)
        r.raise_for_status()
        log.info("slack notification sent lead_id=%s", lead.id)
        return True
    except Exception as exc:  # noqa: BLE001
        log.error("slack notification failed: %s", exc)
        return False


def send_email(lead: Lead) -> bool:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_to or not settings.smtp_from:
        log.info("email skipped (SMTP not configured) lead_id=%s", lead.id)
        return False
    msg = EmailMessage()
    msg["Subject"] = (
        f"[Intake {lead.lead_score}] {lead.customer_name} — {lead.company or 'no company'}"
    )
    msg["From"] = settings.smtp_from
    msg["To"] = settings.smtp_to
    payload = _payload(lead)
    msg.set_content("\n".join(f"{k}: {v}" for k, v in payload.items()))
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=8) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
        log.info("email notification sent lead_id=%s", lead.id)
        return True
    except Exception as exc:  # noqa: BLE001
        log.error("email notification failed: %s", exc)
        return False


def notify_high_value(lead: Lead) -> None:
    settings = get_settings()
    score = lead.lead_score or 0
    urgent = (lead.urgency or "") in {"high", "critical"}
    if score < settings.high_value_score and not urgent:
        log.info(
            "notification skipped (not high-value) lead_id=%s score=%s",
            lead.id,
            score,
        )
        return
    send_slack(lead)
    send_email(lead)
