from app.workers.celery_app import celery
from app.services.pdf_parser import parse_pdf
from app.services.recursive_parser import recursive_parse_blocks
from app.database import SessionLocal
from app.models import Metric
from app.utils.file_utils import delete_file
from app.utils.logger import get_logger

logger = get_logger("celery_task")


@celery.task
def process_pdf_task(file_path: str, report_name: str):

    db = SessionLocal()

    try:
        logger.info(f"Processing file: {file_path}")

        # 🔁 Parse PDF into structured blocks
        blocks = parse_pdf(file_path)

        # 🔁 Recursive token-safe extraction
        metrics = recursive_parse_blocks(blocks, report_name)

        # 💾 Save to DB
        for m in metrics:
            db.add(Metric(**m))

        db.commit()

        logger.info(f"Extraction complete. Metrics saved: {len(metrics)}")

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        db.rollback()
        raise

    finally:
        db.close()
        delete_file(file_path)