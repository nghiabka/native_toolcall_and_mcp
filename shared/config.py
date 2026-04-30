"""Application configuration — loads environment variables."""

import os
from dotenv import load_dotenv

# Load .env file từ thư mục project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash")

if not GOOGLE_API_KEY:
    print("⚠️  GOOGLE_API_KEY chưa được set! Hãy tạo file .env từ .env.example")
