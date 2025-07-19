# Bulk ingests 10k+ PDFs into OpenWebUI

import os
from tqdm import tqdm
from api.openwebui_client import upload_file
import config

PDF_DIR = "/absolute/path/to/knowledge_base_pdfs/"

def ingest_all_pdfs(root_dir):
    # Traverse directories
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if not fname.lower().endswith(".pdf"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                with open(path, "rb") as f:
                    file_bytes = f.read()
                # Upload via client
                file_id = upload_file(file_bytes, fname)
                print(f"✅ {fname} uploaded as {file_id}")
            except Exception as e:
                print(f"❌ Error uploading {fname}: {e}")

if __name__ == "__main__":
    print("Starting bulk ingestion of PDFs...")
    ingest_all_pdfs(PDF_DIR)
    print("Done! 😊")
