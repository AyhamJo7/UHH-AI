# Handles low-level HTTP calls to OpenWebUI

import requests
import config

# Common header with API key
HEADERS = {
    "Authorization": f"Bearer {config.OPENWEBUI_API_KEY}"
}

def send_chat_completion(messages: list, model: str = None, file_ids: list = None):
    # Build request payload
    payload = {
        "model": model or config.DEFAULT_MODEL,
        "messages": messages
    }
    # If files provided, attach them
    if file_ids:
        payload["files"] = [{"type": "file", "id": fid} for fid in file_ids]
    # Call OpenWebUI chat API
    resp = requests.post(
        f"{config.OPENWEBUI_URL}/api/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=120
    )
    resp.raise_for_status()
    data = resp.json()
    # Extract assistant content
    return data["choices"][0]["message"]["content"]

def upload_file(file_bytes: bytes, filename: str):
    # Multipart upload to OpenWebUI
    files = {"file": (filename, file_bytes, "application/pdf")}
    resp = requests.post(
        f"{config.OPENWEBUI_URL}/api/v1/files/",
        headers=HEADERS,
        files=files
    )
    resp.raise_for_status()
    data = resp.json()
    return data["id"]
