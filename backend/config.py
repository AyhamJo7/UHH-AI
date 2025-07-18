# Load environment variables for configuration
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file

# Base URLs
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://localhost:3000")
TIKA_URL      = os.getenv("TIKA_URL", "http://localhost:9998")

# Authentication
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "")

# Backend server settings
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 5000))

# Default AI model (optional override)
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama2:13b")
