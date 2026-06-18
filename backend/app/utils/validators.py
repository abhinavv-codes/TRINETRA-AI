"""Input validators"""

def validate_plate(plate: str) -> bool:
    """Validate license plate format"""
    # Indian plate format: KA-05-AB-1234
    import re
    pattern = r'^[A-Z]{2}-\d{2}-[A-Z]{2}-\d{4}$'
    return bool(re.match(pattern, plate))


def validate_camera_id(camera_id: str) -> bool:
    """Validate camera ID"""
    return len(camera_id) > 0 and len(camera_id) <= 50


def validate_risk_score(score: int) -> bool:
    """Validate risk score 0-100"""
    return 0 <= score <= 100
