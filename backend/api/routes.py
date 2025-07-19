# Import FastAPI router and dependencies
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.chat_service import process_user_message
from services.document_service import upload_document

router = APIRouter()

# Chat endpoint
@router.post("/chat")
def chat_endpoint(payload: dict):
    # Validate payload has 'message' key
    if 'message' not in payload:
        raise HTTPException(status_code=400, detail="Missing 'message'")
    message = payload['message']
    file_ids = payload.get('files', [])
    # Delegate to service
    answer = process_user_message(message, file_ids)
    return {"answer": answer}

# File upload endpoint
@router.post("/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    # Validate file content-type if desired
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    # Delegate to service
    file_id = upload_document(file)
    return {"file_id": file_id}
