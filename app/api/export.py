import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Metric

router = APIRouter()

@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    metrics = db.query(Metric).all()

    df = pd.DataFrame([
        {
            "metric_name": m.metric_name,
            "value": m.value,
            "unit": m.unit,
            "year": m.year,
            "page_number": m.page_number,
            "confidence_score": m.confidence_score
        }
        for m in metrics
    ])

    file_path = "export.csv"
    df.to_csv(file_path, index=False)

    return {"file": file_path}