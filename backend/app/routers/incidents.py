from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident
from app.schemas import DashboardMetrics, IncidentResponse, IncidentStatusUpdate
from app.services.incident_service import build_dashboard_metrics, update_incident_status

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.last_seen.desc()).all()


@router.patch("/{incident_id}", response_model=IncidentResponse)
def patch_incident_status(incident_id: int, payload: IncidentStatusUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return update_incident_status(db, incident, payload.status)


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def dashboard_metrics(db: Session = Depends(get_db)):
    return build_dashboard_metrics(db)
