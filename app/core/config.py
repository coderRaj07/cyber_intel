import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

REDIS_URL = os.getenv("REDIS_URL")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
