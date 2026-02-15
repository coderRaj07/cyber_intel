from celery import Celery
from app.core.config import REDIS_URL

celery_app = Celery(
    "cyber_intel",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# 🔥 IMPORTANT
celery_app.autodiscover_tasks(["app"])