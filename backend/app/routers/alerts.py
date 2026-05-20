from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlertHistory
from app.schemas import AlertHistoryResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/history", response_model=list[AlertHistoryResponse])
def alert_history(db: Session = Depends(get_db)):
    return db.query(AlertHistory).order_by(AlertHistory.sent_at.desc()).limit(200).all()
