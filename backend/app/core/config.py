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
    }
    
    # App
    app_name: str = "TRINETRA AI"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./trinetra.db"  # SQLite for development (change to PostgreSQL for production)
    redis_url: str = "redis://localhost:6379/0"
    
    # Object Storage (MinIO)
    minio_url: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "trinetra-evidence"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # ML Models
    model_path: str = "./yolov8n.pt"
    device: str = "cpu"  # or 'cuda'
    
    # Frontend
    frontend_url: str = "http://localhost:5173"
    
    # Paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = False


# Create settings instance
settings = Settings()
