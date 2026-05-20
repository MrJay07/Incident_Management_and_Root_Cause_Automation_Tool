from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Incident, IncidentStatus, RCAReport
from app.services.log_parser import DetectedIncident


def upsert_incident(db: Session, detected: DetectedIncident, source_log_id: int | None = None) -> Incident:
    existing = (
        db.query(Incident)
        .filter(
            Incident.title == detected.title,
            Incident.service == detected.service,
            Incident.status != IncidentStatus.RESOLVED,
        )
        .first()
    )
    if existing:
        existing.occurrences += 1
        existing.last_seen = datetime.utcnow()
        if detected.severity.value == "CRITICAL":
            existing.severity = detected.severity
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    incident = Incident(
        title=detected.title,
        description=detected.description,
        severity=detected.severity,
        status=IncidentStatus.OPEN,
        service=detected.service,
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        source_log_id=source_log_id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def update_incident_status(db: Session, incident: Incident, status: IncidentStatus) -> Incident:
    incident.status = status
    incident.last_seen = datetime.utcnow()
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def build_dashboard_metrics(db: Session) -> dict:
    incident_rows = db.query(Incident).all()
    trend_counter = Counter(incident.first_seen.strftime("%Y-%m-%d") for incident in incident_rows)
    incident_trends = dict(sorted(trend_counter.items(), reverse=True)[:14])

    recovery_rows = (
        db.query(Incident)
        .filter(Incident.status == IncidentStatus.RESOLVED)
        .order_by(Incident.last_seen.desc())
        .limit(50)
        .all()
    )
    if recovery_rows:
        avg_recovery = sum((r.last_seen - r.first_seen).total_seconds() for r in recovery_rows) / (len(recovery_rows) * 60)
    else:
        avg_recovery = 0.0

    failure_frequency_by_service = dict(Counter(incident.service for incident in incident_rows))

    active_cutoff = datetime.utcnow() - timedelta(minutes=15)
    service_health = {}
    latest_per_service: dict[str, datetime] = {}
    for incident in incident_rows:
        if incident.service not in latest_per_service or incident.last_seen > latest_per_service[incident.service]:
            latest_per_service[incident.service] = incident.last_seen
    for service, last_seen in latest_per_service.items():
        service_health[service] = "degraded" if last_seen >= active_cutoff else "healthy"

    recent_activity = [
        {
            "type": "rca",
            "incident_id": report.incident_id,
            "summary": report.summary,
            "created_at": report.created_at.isoformat(),
        }
        for report in db.query(RCAReport).order_by(RCAReport.created_at.desc()).limit(10).all()
    ]

    return {
        "incident_trends": incident_trends,
        "average_recovery_minutes": round(avg_recovery, 2),
        "failure_frequency_by_service": failure_frequency_by_service,
        "service_health": service_health,
        "recent_activity": recent_activity,
    }
