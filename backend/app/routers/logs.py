from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LogEntry
from app.schemas import LogEntryResponse, LogIngestRequest
from app.services.alert_service import send_incident_email_alert
from app.services.incident_service import upsert_incident
from app.services.log_parser import detect_incidents, parse_log_line

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/upload", response_model=dict)
async def upload_logs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    content = (await file.read()).decode("utf-8", errors="ignore")
    lines = [line for line in content.splitlines() if line.strip()]
    return ingest_lines(lines, db)


@router.post("/stream", response_model=dict)
def stream_logs(payload: LogIngestRequest, db: Session = Depends(get_db)):
    return ingest_lines(payload.lines, db, payload.custom_rules)


@router.get("", response_model=list[LogEntryResponse])
def list_logs(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(limit).all()


def ingest_lines(lines: list[str], db: Session, custom_rules: list[dict] | None = None) -> dict:
    incidents_created = 0
    for line in lines:
        parsed = parse_log_line(line)
        if not parsed:
            continue

        log_entry = LogEntry(
            timestamp=parsed.timestamp,
            service=parsed.service,
            level=parsed.level,
            message=parsed.message,
            raw_line=parsed.raw_line,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        detected = detect_incidents(parsed, custom_rules)
        for incident in detected:
            incident_model = upsert_incident(db, incident, source_log_id=log_entry.id)
            send_incident_email_alert(db, incident_model)
            incidents_created += 1

    return {"processed_lines": len(lines), "incident_events": incidents_created}
