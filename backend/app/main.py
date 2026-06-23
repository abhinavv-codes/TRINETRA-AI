"""
FastAPI Application Entry Point
TRINETRA AI - Traffic Violation Detection & Risk Analytics Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

import warnings
# Suppress Pydantic namespace conflict warnings (from models with conflicting prefixes)
warnings.filterwarnings("ignore", message=".*protected namespace.*")
warnings.filterwarnings("ignore", message=".*model_kwargs.*")
# Suppress requests version dependency version mismatch warnings
warnings.filterwarnings("ignore", message=".*urllib3.*")
# Suppress passlib bcrypt version incompatibility warnings
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress excessive SQLAlchemy queries and other verbose engines logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("ppocr").setLevel(logging.WARNING)

# Import routers and services
from app.routers import violations, analytics, auth, health
from app.core.config import settings
from app.db.session import init_db


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting TRINETRA AI Backend...")
    
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    
    logger.info("✅ TRINETRA AI API ready!")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TRINETRA AI...")


# Create FastAPI app
app = FastAPI(
    title="TRINETRA AI API",
    description="Intelligent Traffic Violation Detection, Evidence Generation & Risk Analytics Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Mount static files for local storage fallback
os.makedirs("data", exist_ok=True)
app.mount("/static", StaticFiles(directory="data"), name="static")

# Mount evidence files for direct relative serving
os.makedirs("evidence", exist_ok=True)
app.mount("/evidence", StaticFiles(directory="evidence"), name="evidence")

# CORS middleware
origins = [
    "http://localhost:5173",      # Vite dev server
    "http://localhost:3000",      # Alternative frontend
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
if settings.frontend_url:
    clean_url = settings.frontend_url.rstrip("/")
    if clean_url == "*":
        origins = ["*"]
    elif clean_url not in origins:
        origins.append(clean_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(violations.router, prefix="/api/v1/violations", tags=["violations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "TRINETRA AI",
        "version": "1.0.0",
        "description": "Traffic Violation Detection & Risk Analytics Platform",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/api/v1")
async def api_root():
    """API v1 root"""
    return {
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "auth": "/api/v1/auth",
            "violations": "/api/v1/violations",
            "analytics": "/api/v1/analytics",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
