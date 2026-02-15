from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.dashboard import router as dashboard_router
from app.db.database import Base, engine
import app.db.models

app = FastAPI(title="Cyber Intelligence Pipeline")

Base.metadata.create_all(bind=engine)

app.include_router(upload_router)
app.include_router(dashboard_router)
