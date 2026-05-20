from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident, RCAReport
from app.schemas import RCAReportResponse
from app.services.rca_service import simulate_rca

router = APIRouter(prefix="/rca", tags=["rca"])


@router.post("/{incident_id}/simulate", response_model=RCAReportResponse)
def run_rca(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return simulate_rca(db, incident)


@router.get("", response_model=list[RCAReportResponse])
def list_rca_reports(db: Session = Depends(get_db)):
    return db.query(RCAReport).order_by(RCAReport.created_at.desc()).all()
