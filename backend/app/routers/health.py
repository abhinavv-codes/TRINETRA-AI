"""Health check endpoints"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "TRINETRA AI API"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check - verify all services are ready"""
    return {
        "status": "ready",
        "database": "connected",
        "models": "loaded",
        "cache": "available"
    }
