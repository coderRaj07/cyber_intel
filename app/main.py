from fastapi import FastAPI
from app.database import Base, engine
from app.api import upload, metrics, export

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cyber Metric Extractor")

app.include_router(upload.router)
app.include_router(metrics.router)
app.include_router(export.router)