"""Initialize database and create tables"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import init_db
from app.db.models import Base, engine

print("🗄️  Initializing database...")

try:
    init_db()
    print("✅ Database initialized successfully!")
    print("📊 Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"   - {table.name}")
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    sys.exit(1)
