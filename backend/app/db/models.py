"""SQLAlchemy ORM models"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ARRAY, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

Base = declarative_base()


class Vehicle(Base):
    """Vehicle records"""
    __tablename__ = "vehicles"
    
    vehicle_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_text = Column(String(16), index=True, nullable=False)
    vehicle_type = Column(String(50))  # car, motorcycle, bus, truck, auto
    owner_name = Column(String(200), nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow, index=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    violation_count = Column(Integer, default=0)


class Violation(Base):
    """Violation detection events"""
    __tablename__ = "violations"
    
    violation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.vehicle_id'), nullable=True)
    camera_id = Column(String(50), index=True, nullable=False)
    violation_types = Column(ARRAY(String), default=[])  # e.g., ["NO_HELMET", "TRIPLE"]
    detected_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    
    risk_score = Column(Integer, nullable=True)  # 0-100
    risk_band = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    
    status = Column(String(20), default="PENDING", index=True)  # PENDING, VERIFIED, REJECTED, ISSUED
    
    # Context
    speed_kmph = Column(Float, nullable=True)
    ped_count = Column(Integer, default=0)
    zones = Column(ARRAY(String), default=[])  # SCHOOL_ZONE, JUNCTION, etc.
    traffic_density = Column(Float, default=0.5)
    
    location = Column(String(100), nullable=True)  # GeoJSON: {"lat": 12.97, "lon": 77.59}
    
    # Report and metadata
    report_text = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    
    # Audit
    verified_by = Column(String(100), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)


class Evidence(Base):
    """Tamper-evident evidence images"""
    __tablename__ = "evidence"
    
    evidence_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), ForeignKey('violations.violation_id'), index=True, nullable=False)
    
    image_uri = Column(String(500), nullable=False)  # S3/MinIO path
    sha256 = Column(String(64), nullable=False)  # Tamper-evident hash
    prev_hash = Column(String(64), nullable=True)  # Hash chain
    
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base):
    """System users (officers, admins, auditors)"""
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    role = Column(String(20), default="VIEWER", index=True)  # ADMIN, OFFICER, AUDITOR, VIEWER
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class Hotspot(Base):
    """Aggregated violation hotspots"""
    __tablename__ = "hotspots"
    
    hotspot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    location = Column(String(100), nullable=False)  # GeoJSON point
    corridor = Column(String(100), index=True)
    
    period = Column(String(50))  # e.g., "2026-06-18" or "08:00-09:00"
    
    violation_count = Column(Integer, default=0)
    risk_weighted_sum = Column(Float, default=0.0)
    avg_risk_score = Column(Float, default=0.0)
    
    computed_at = Column(DateTime, default=datetime.utcnow)


class Analytics(Base):
    """Time-series analytics data"""
    __tablename__ = "analytics"
    
    analytics_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    metric_type = Column(String(50), index=True)  # predicted_count, avg_risk, etc.
    dimension = Column(JSONB)  # {location, hour, dow, violation_type}
    value = Column(Float, nullable=False)
    
    computed_at = Column(DateTime, default=datetime.utcnow, index=True)


class AuditLog(Base):
    """Immutable audit trail"""
    __tablename__ = "audit_log"
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    action = Column(String(100), nullable=False)  # VERIFY, REJECT, ISSUE, LOGIN, etc.
    
    resource_type = Column(String(50))  # VIOLATION, EVIDENCE, USER, etc.
    resource_id = Column(String(50))  # ID of the resource
    
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    
    details = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
