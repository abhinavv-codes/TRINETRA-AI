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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers and services
from app.routers import violations, analytics, auth, health
from app.core.config import settings
from app.inference.model_loader import load_models
from app.db.session import init_db


# Lifespan: load models at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting TRINETRA AI Backend...")
    logger.info("Loading AI models...")
    try:
        load_models()
        logger.info("✅ Models loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")
    
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",      # Alternative frontend
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
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
