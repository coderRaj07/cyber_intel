from fastapi import APIRouter, UploadFile, File, Query
from hashlib import sha256
import os
from app.core.config import UPLOAD_DIR
from app.services.pipeline_service import run_pipeline
from app.tasks import process_pdf  # celery task

router = APIRouter()

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    celery: bool = Query(False, description="Run pipeline via Celery")
):
    content = await file.read()
    doc_hash = sha256(content).hexdigest()

    path = os.path.join(UPLOAD_DIR, f"{doc_hash}.pdf")

    with open(path, "wb") as f:
        f.write(content)

    if celery:
        # 🔹 Async background execution
        process_pdf.delay(path, doc_hash)
        return {
            "document_id": doc_hash,
            "mode": "celery",
            "status": "processing in background"
        }
    else:
        # 🔹 Direct synchronous execution
        run_pipeline(path, doc_hash)
        return {
            "document_id": doc_hash,
            "mode": "sync",
            "status": "completed"
        }
