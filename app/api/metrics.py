from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Metric

router = APIRouter()

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return db.query(Metric).all()