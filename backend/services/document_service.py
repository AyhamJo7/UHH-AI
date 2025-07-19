# Business logic for handling document uploads

from api.openwebui_client import upload_file
from utils.logger import logger

def upload_document(file) -> str:
    # Read file bytes
    file_bytes = file.file.read()
    filename = file.filename
    logger.info(f"Uploading document: {filename}")
    try:
        file_id = upload_file(file_bytes, filename)
        logger.info(f"Uploaded document with ID: {file_id}")
        return file_id
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise
