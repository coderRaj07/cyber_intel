# ------------Pipeline Call via Celery-----------
# from fastapi import APIRouter, UploadFile, File
# from hashlib import sha256
# import os
# from app.core.config import UPLOAD_DIR
# from app.tasks import process_pdf

# router = APIRouter()

# os.makedirs(UPLOAD_DIR, exist_ok=True)

# @router.post("/upload")
# async def upload(file: UploadFile = File(...)):
#     content = await file.read()
#     doc_hash = sha256(content).hexdigest()

#     path = os.path.join(UPLOAD_DIR, f"{doc_hash}.pdf")

#     with open(path, "wb") as f:
#         f.write(content)

#     process_pdf.delay(path, doc_hash)

#     return {"document_id": doc_hash}

# ---------------Direct Pipeline Call (No Celery)-----------------
from fastapi import APIRouter, UploadFile, File
from hashlib import sha256
import os
from app.core.config import UPLOAD_DIR
from app.services.pipeline_service import run_pipeline  # ✅ changed

router = APIRouter()

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    doc_hash = sha256(content).hexdigest()

    path = os.path.join(UPLOAD_DIR, f"{doc_hash}.pdf")

    with open(path, "wb") as f:
        f.write(content)

    # ✅ Direct call (no celery)
    run_pipeline(path, doc_hash)

    return {"document_id": doc_hash}
