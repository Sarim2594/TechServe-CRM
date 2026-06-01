import asyncio
import logging
import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from ..models import NotificationLog, Ticket

load_dotenv()

logger = logging.getLogger(__name__)

SUPPORTED_EVENTS = {
    "ticket_created": "New ticket created",
    "ticket_resolved": "Ticket resolved",
    "ticket_critical": "Ticket escalated to Critical",
    "ticket_test": "Test email notification",
}
SMTP_SETTING_NAMES = (
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "SMTP_FROM_EMAIL",
    "SMTP_TO_EMAIL",
)


@dataclass
class NotificationResult:
    notification: NotificationLog
    event_type: str
    recipient: str | None


def _is_enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _settings() -> dict[str, str]:
    settings = {name: os.getenv(name, "").strip() for name in SMTP_SETTING_NAMES}
    settings["SMTP_PORT"] = settings["SMTP_PORT"] or "587"
    return settings


def _format_email(ticket: Ticket, event_type: str) -> tuple[str, str]:
    event_label = SUPPORTED_EVENTS.get(event_type, event_type.replace("_", " ").title())
    customer = ticket.customer.full_name if ticket.customer else "Unknown customer"
    assigned_agent = ticket.assigned_agent.name if ticket.assigned_agent else "Unassigned"
    category = ticket.category or ticket.ai_category or "General"
    subject = f"[TechServe CRM] {event_label}: Ticket #{ticket.id}"
    body = "\n".join(
        (
            event_label,
            "",
            f"Ticket ID: {ticket.id}",
            f"Title: {ticket.title}",
            f"Customer: {customer}",
            f"Priority: {ticket.priority}",
            f"Status: {ticket.status}",
            f"Category: {category}",
            f"Assigned agent: {assigned_agent}",
            f"Event type: {event_type}",
        )
    )
    return subject, body


def _send_smtp(settings: dict[str, str], subject: str, body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings["SMTP_FROM_EMAIL"]
    message["To"] = settings["SMTP_TO_EMAIL"]
    message.set_content(body)

    with smtplib.SMTP(settings["SMTP_HOST"], int(settings["SMTP_PORT"]), timeout=10) as server:
        if _is_enabled("SMTP_USE_TLS", "true"):
            server.starttls()
        server.login(settings["SMTP_USERNAME"], settings["SMTP_PASSWORD"])
        server.send_message(message)


async def send_ticket_notification(
    db: Session, ticket: Ticket, event_type: str
) -> NotificationResult:
    subject, body = _format_email(ticket, event_type)
    settings = _settings()
    recipient = settings["SMTP_TO_EMAIL"] or None
    stored_message = f"Subject: {subject}\n\n{body}"
    status = "logged"

    if not _is_enabled("ENABLE_MESSAGING"):
        logger.info("SMTP messaging is disabled. Notification logged for ticket #%s.", ticket.id)
    elif os.getenv("MESSAGING_PLATFORM", "smtp").strip().lower() != "smtp":
        status = "skipped"
        logger.warning("Messaging platform is not SMTP. Notification skipped for ticket #%s.", ticket.id)
    elif missing_settings := [name for name, value in settings.items() if not value]:
        status = "skipped"
        logger.warning(
            "SMTP settings are incomplete. Notification skipped for ticket #%s. Missing: %s",
            ticket.id,
            ", ".join(missing_settings),
        )
    else:
        try:
            await asyncio.to_thread(_send_smtp, settings, subject, body)
            status = "sent"
        except (OSError, smtplib.SMTPException, ValueError) as exc:
            status = "failed"
            stored_message += f"\n\nDelivery error: {type(exc).__name__}"
            logger.warning("SMTP notification failed for ticket #%s: %s", ticket.id, exc)

    notification = NotificationLog(
        ticket_id=ticket.id,
        platform="smtp",
        message=stored_message,
        status=status,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return NotificationResult(notification=notification, event_type=event_type, recipient=recipient)
