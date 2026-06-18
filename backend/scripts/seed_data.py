"""Seed database with mock data for testing"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import Vehicle, Violation, User
from app.core.security import get_password_hash

print("🌱 Seeding database with mock data...")

db = SessionLocal()

try:
    # Create mock vehicles
    vehicles = [
        Vehicle(
            plate_text="KA-05-AB-1234",
            vehicle_type="motorcycle",
            owner_name="John Doe"
        ),
        Vehicle(
            plate_text="KA-05-XY-5678",
            vehicle_type="car",
            owner_name="Jane Smith"
        ),
        Vehicle(
            plate_text="KA-05-MN-9012",
            vehicle_type="auto",
            owner_name="Bob Wilson"
        ),
    ]
    
    for vehicle in vehicles:
        db.add(vehicle)
    
    # Create mock violations
    base_time = datetime.utcnow()
    violations = [
        Violation(
            vehicle_id=vehicles[0].vehicle_id,
            camera_id="J17-N",
            violation_types=["NO_HELMET", "TRIPLE_RIDING"],
            risk_score=87,
            risk_band="HIGH",
            status="PENDING",
            speed_kmph=54,
            ped_count=3,
            zones=["SCHOOL_ZONE"],
            traffic_density=0.7,
            detected_at=base_time - timedelta(hours=2),
            report_text="Motorcycle detected without helmet in school zone"
        ),
        Violation(
            vehicle_id=vehicles[1].vehicle_id,
            camera_id="J17-N",
            violation_types=["RED_LIGHT"],
            risk_score=78,
            risk_band="HIGH",
            status="PENDING",
            speed_kmph=65,
            ped_count=5,
            zones=["JUNCTION"],
            traffic_density=0.8,
            detected_at=base_time - timedelta(hours=1),
            report_text="Vehicle jumped red light at junction"
        ),
    ]
    
    for violation in violations:
        db.add(violation)
    
    # Create demo users
    users = [
        User(
            username="demo",
            email="demo@trinetra.ai",
            password_hash=get_password_hash("demo123"),
            first_name="Demo",
            last_name="Officer",
            role="OFFICER",
            is_active=True
        ),
        User(
            username="admin",
            email="admin@trinetra.ai",
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role="ADMIN",
            is_active=True
        ),
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    
    print("✅ Mock data seeded successfully!")
    print(f"   - {len(vehicles)} vehicles created")
    print(f"   - {len(violations)} violations created")
    print(f"   - {len(users)} users created")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error seeding database: {e}")
    sys.exit(1)
finally:
    db.close()
