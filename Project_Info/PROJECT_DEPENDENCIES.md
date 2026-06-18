# TRINETRA AI - Complete Dependencies & Setup Guide

## 📦 PART 1: PROJECT DEPENDENCIES

### Backend Dependencies (Python)

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Computer Vision & ML
torch==2.1.2
torchvision==0.16.2
ultralytics==8.0.234          # YOLOv8/v11
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.1.0
scikit-image==0.22.0

# OCR
paddleocr==2.7.0.3
easyocr==1.7.0                # Fallback

# Tracking
filterpy==1.4.2               # For ByteTrack
scikit-learn==1.3.2

# Predictive Analytics & Risk Scoring
lightgbm==4.1.0
xgboost==2.0.0
pandas==2.1.3
scipy==1.11.4

# Database & ORM
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9       # PostgreSQL driver
geoalchemy2==0.14.1          # PostGIS support
redis==5.0.1

# Data Processing
pillow==10.1.0
shapely==2.0.2               # Geometry for zone/congestion
geopy==2.4.0                 # Geo utilities

# API & Auth
python-jose==3.3.0           # JWT
passlib==1.7.4               # Password hashing
python-multipart==0.0.6      # Form data
cryptography==41.0.7

# Cloud & Storage
boto3==1.29.7                # AWS S3 (optional, for production)
minio==7.2.0                 # MinIO (S3-compatible, for demo)

# Observability
python-json-logger==2.0.7
tenacity==8.2.3              # Retry logic

# Testing & Development
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.12.0
flake8==6.1.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0
aiofiles==23.2.1
