"""Pydantic schemas for API validation and documentation"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ViolationRequest(BaseModel):
    """Violation detection request"""
    image_uri: Optional[str] = None
    camera_id: str = "J17-N"


class ViolationResponse(BaseModel):
    """Violation detection response"""
    violation_id: str
    vehicle_plate: str
    violations: List[str]
    risk_score: int
    risk_band: str
    camera_id: str
    timestamp: str
    status: str = "PENDING"


class ViolationDetailResponse(ViolationResponse):
    """Detailed violation information"""
    evidence_uri: Optional[str] = None
    report: Optional[str] = None
    factors: Optional[dict] = None


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    role: str


class HotspotResponse(BaseModel):
    """Hotspot data"""
    location: dict  # GeoJSON Point
    intensity: float
    violation_count: int
    corridor: str
