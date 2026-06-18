"""Application constants"""

from enum import Enum


class ViolationType(str, Enum):
    """Traffic violation types"""
    NO_HELMET = "NO_HELMET"
    TRIPLE_RIDING = "TRIPLE_RIDING"
    NO_SEATBELT = "NO_SEATBELT"
    RED_LIGHT = "RED_LIGHT"
    STOP_LINE = "STOP_LINE"
    WRONG_SIDE = "WRONG_SIDE"
    ILLEGAL_PARKING = "ILLEGAL_PARKING"


class RiskBand(str, Enum):
    """Risk score bands"""
    LOW = "LOW"           # 0-30
    MEDIUM = "MEDIUM"     # 30-60
    HIGH = "HIGH"         # 60-80
    CRITICAL = "CRITICAL"  # 80-100


class ViolationStatus(str, Enum):
    """Violation event status"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    ISSUED = "ISSUED"


class UserRole(str, Enum):
    """User roles for authorization"""
    ADMIN = "ADMIN"
    OFFICER = "OFFICER"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


# Violation severity mapping (0-1)
VIOLATION_SEVERITY = {
    ViolationType.RED_LIGHT: 1.0,
    ViolationType.WRONG_SIDE: 0.9,
    ViolationType.TRIPLE_RIDING: 0.75,
    ViolationType.NO_HELMET: 0.65,
    ViolationType.STOP_LINE: 0.55,
    ViolationType.NO_SEATBELT: 0.50,
    ViolationType.ILLEGAL_PARKING: 0.40,
}

# Risk scoring weights
RISK_WEIGHTS = {
    'severity': 0.30,
    'pedestrians': 0.20,
    'speed': 0.15,
    'school_zone': 0.12,
    'density': 0.10,
    'junction': 0.08,
    'time': 0.05,
}
