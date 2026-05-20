from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Incident, RCAReport

SERVICE_DEPENDENCIES = {
    "api-gateway": ["auth-service", "payments-service"],
    "payments-service": ["database", "cache"],
    "auth-service": ["database", "identity-provider"],
    "worker": ["queue", "database"],
}


def simulate_rca(db: Session, incident: Incident) -> RCAReport:
    dependencies = SERVICE_DEPENDENCIES.get(incident.service, ["database", "cache"])
    timeline = [
        {"time": incident.first_seen.isoformat(), "event": "Initial anomaly detected"},
        {"time": incident.last_seen.isoformat(), "event": f"Incident escalated as {incident.severity.value}"},
        {"time": datetime.utcnow().isoformat(), "event": "RCA simulation completed"},
    ]
    bottleneck = dependencies[0]
    summary = (
        f"Likely root cause traced to {bottleneck}. "
        f"{incident.service} depends on {', '.join(dependencies)} and observed symptom was: {incident.description[:160]}"
    )

    report = RCAReport(
        incident_id=incident.id,
        summary=summary,
        timeline=timeline,
        bottleneck=bottleneck,
        dependencies=[{"service": incident.service, "depends_on": dep} for dep in dependencies],
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
