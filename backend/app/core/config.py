"""Application Configuration"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    model_config = {
        "protected_namespaces": ("settings_",),
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }
    
    # App
    app_name: str = "TRINETRA AI"
    app_version: str = "1.2.0"
    debug: bool = False
    
    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./trinetra.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Object Storage (MinIO)
    minio_url: str = os.getenv("MINIO_URL", "http://localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket: str = os.getenv("MINIO_BUCKET", "trinetra-evidence")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # ML Models
    model_path: str = os.getenv("MODEL_PATH", "./yolov8n.pt")
    device: str = os.getenv("DEVICE", "cpu")  # or 'cuda'
    
    # Frontend
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = False


# Create settings instance
settings = Settings()
