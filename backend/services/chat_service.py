# Business logic for processing user chat messages

from api.openwebui_client import send_chat_completion
from utils.logger import logger
import config

def process_user_message(user_message: str, file_ids: list = None) -> str:
    logger.info(f"Processing user message: {user_message} with files {file_ids}")
    # Build the message list for RAG
    messages = [
        {"role": "system", "content": "You are the University AI Assistant. Answer based on facts."},
        {"role": "user", "content": user_message}
    ]
    # Call OpenWebUI and get answer
    try:
        answer = send_chat_completion(messages, model=config.DEFAULT_MODEL, file_ids=file_ids)
        logger.info(f"Received answer: {answer}")
        return answer
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        return "⚠️ Sorry, I couldn't process your request right now."
