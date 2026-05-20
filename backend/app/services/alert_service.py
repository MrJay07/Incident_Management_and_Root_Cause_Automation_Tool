import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.config import settings
from app.models import AlertHistory, Incident


def _is_throttled(db: Session, incident_id: int) -> bool:
    recent = (
        db.query(AlertHistory)
        .filter(AlertHistory.incident_id == incident_id)
        .order_by(AlertHistory.sent_at.desc())
        .first()
    )
    if not recent:
        return False
    return recent.sent_at >= datetime.utcnow() - timedelta(seconds=settings.alert_throttle_seconds)


def send_incident_email_alert(db: Session, incident: Incident) -> AlertHistory:
    if _is_throttled(db, incident.id):
        alert = AlertHistory(
            incident_id=incident.id,
            channel="email",
            recipient=settings.alert_recipient,
            status="throttled",
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    msg = EmailMessage()
    msg["Subject"] = f"[{incident.severity.value}] Incident #{incident.id}: {incident.title}"
    msg["From"] = settings.smtp_sender
    msg["To"] = settings.alert_recipient
    msg.set_content(
        f"Service: {incident.service}\n"
        f"Severity: {incident.severity.value}\n"
        f"Status: {incident.status.value}\n"
        f"Occurrences: {incident.occurrences}\n"
        f"Description: {incident.description}\n"
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.send_message(msg)
        status = "sent"
        error_message = None
    except Exception as exc:  # noqa: BLE001
        status = "failed"
        error_message = str(exc)

    alert = AlertHistory(
        incident_id=incident.id,
        channel="email",
        recipient=settings.alert_recipient,
        status=status,
        error_message=error_message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
