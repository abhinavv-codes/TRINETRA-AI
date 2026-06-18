"""Database session and connection management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models import Base

# Create engine (with SQLite-specific settings if needed)
engine_kwargs = {
    "echo": settings.debug,
    "pool_pre_ping": True,
}

# For SQLite, disable pool settings
if "sqlite" in settings.database_url:
    engine = create_engine(settings.database_url, **{k: v for k, v in engine_kwargs.items() if k != "pool_pre_ping"})
else:
    engine = create_engine(settings.database_url, **engine_kwargs)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database schema"""
    Base.metadata.create_all(bind=engine)
