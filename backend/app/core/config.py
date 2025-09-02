from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI-Powered Multilingual Survey Platform"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/ai_survey_db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS / Hosts
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI Services
    GOOGLE_AI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Voice Services
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Google Cloud Services
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = [
        "en", "hi", "bn", "te", "mr", "ta", "gu", "kn", "ml", "pa"
    ]
    
    # Language Names
    LANGUAGE_NAMES: dict = {
        "en": "English",
        "hi": "Hindi",
        "bn": "Bengali",
        "te": "Telugu",
        "mr": "Marathi",
        "ta": "Tamil",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi"
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Normalize CORS_ORIGINS when provided as a comma-separated string or JSON string
if isinstance(settings.CORS_ORIGINS, str):
    import json
    try:
        parsed = json.loads(settings.CORS_ORIGINS)
        if isinstance(parsed, list):
            settings.CORS_ORIGINS = parsed
        else:
            settings.CORS_ORIGINS = [settings.CORS_ORIGINS]
    except Exception:
        settings.CORS_ORIGINS = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
