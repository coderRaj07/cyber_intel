from fastapi import APIRouter
from app.db.database import SessionLocal
from app.db.models import Metric
import pandas as pd

router = APIRouter()

@router.get("/dashboard/metrics")
def get_metrics():
    db = SessionLocal()
    metrics = db.query(Metric).all()
    db.close()
    return [m.__dict__ for m in metrics]


@router.get("/dashboard/longitudinal")
def get_longitudinal():

    db = SessionLocal()
    metrics = db.query(Metric).all()
    db.close()

    df = pd.DataFrame([m.__dict__ for m in metrics])

    if df.empty:
        return []

    df = df.groupby(
        ["metric_key", "year", "unit"],
        as_index=False
    ).agg({
        "value": "sum",
        "confidence_score": "mean"
    })

    return df.to_dict(orient="records")


@router.get("/dashboard/export-csv")
def export_csv():

    db = SessionLocal()
    metrics = db.query(Metric).all()
    db.close()

    df = pd.DataFrame([m.__dict__ for m in metrics])

    return df.to_csv(index=False)
