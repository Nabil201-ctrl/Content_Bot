try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from typing import Optional
import os
from pathlib import Path

# Load .env explicitly
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class Settings(BaseSettings):
    app: str = "Content Bot"
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "content_bot"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    GEMINI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Debug: print if GEMINI_API_KEY is loaded
if settings.GEMINI_API_KEY:
    print(f"✓ GEMINI_API_KEY loaded: {settings.GEMINI_API_KEY[:20]}...")
else:
    print("✗ GEMINI_API_KEY not found")