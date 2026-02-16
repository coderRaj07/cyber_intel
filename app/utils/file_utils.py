import os
import uuid

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def save_upload_file(upload_file):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{upload_file.filename}")

    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return file_path


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)