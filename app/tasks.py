from app.core.celery_app import celery_app
from app.services.pipeline_service import run_pipeline

@celery_app.task
def process_pdf(path, document_id):
    run_pipeline(path, document_id)
