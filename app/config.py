import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
USE_CELERY = os.getenv("USE_CELERY", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL")

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama-3.1-70b")