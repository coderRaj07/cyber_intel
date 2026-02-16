from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Metric
from app.services.pdf_parser import parse_pdf
from app.services.recursive_parser import recursive_parse_blocks
from app.config import USE_CELERY
from app.workers.tasks import process_pdf_task
from app.utils.file_utils import save_upload_file, delete_file
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("upload")

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = save_upload_file(file)

    logger.info(f"File saved at {file_path}")

    if USE_CELERY:
        process_pdf_task.delay(file_path, file.filename)
        return {"status": "Processing in background"}

    blocks = parse_pdf(file_path)
    metrics = recursive_parse_blocks(blocks, file.filename)

    for m in metrics:
        db.add(Metric(**m))

    db.commit()
    delete_file(file_path)

    logger.info(f"Extraction completed. Metrics: {len(metrics)}")

    return {
        "status": "Completed",
        "metrics_extracted": len(metrics)
    }