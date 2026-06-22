"""Database session and connection management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models import Base

# Prepare database URL and arguments dynamically
db_url = settings.database_url
engine_kwargs = {
    "echo": False,
}
connect_args = {}

if "sqlite" not in db_url:
    engine_kwargs["pool_pre_ping"] = True

if db_url.startswith("mysql://") or db_url.startswith("mysql+pymysql://"):
    # Translate mysql:// to mysql+pymysql://
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
    
    # Check for ssl-mode or ssl_mode in query string
    import re
    pattern = re.compile(r'[?&]ssl[-_]mode=[a-zA-Z]+', re.IGNORECASE)
    has_ssl = bool(pattern.search(db_url))
    db_url = pattern.sub('', db_url)
    
    # Clean up trailing ? or double query separators if they occur
    if db_url.endswith('?'):
        db_url = db_url[:-1]
    db_url = db_url.replace('?&', '?')
    
    # Configure SSL args for PyMySQL
    if has_ssl:
        connect_args["ssl"] = {"ssl_mode": "REQUIRED"}

if connect_args:
    engine_kwargs["connect_args"] = connect_args

# Create engine
engine = create_engine(db_url, **engine_kwargs)

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
