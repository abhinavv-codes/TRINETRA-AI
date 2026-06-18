# TRINETRA AI - Complete Build & Setup Guide

## 🚀 PART 2: HOW TO BUILD THE PROJECT

### Phase 1: Local Development Setup (Hours 0-3)

#### Step 1: Environment Setup

**Windows:**
```powershell
# Clone/initialize repo
cd d:\GRIDLOCK

# Create Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Create Node environment
cd frontend
npm init -y
cd ..
```

**Linux/Mac:**
```bash
cd ~/GRIDLOCK

# Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Node setup
cd frontend
npm init -y
cd ..
```

#### Step 2: Install Backend Dependencies

```bash
# From root directory, with venv activated
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install fastapi uvicorn pydantic torch torchvision
pip install ultralytics opencv-python numpy Pillow

# Install CV/ML packages
pip install paddleocr easyocr scikit-learn
pip install lightgbm xgboost pandas scipy

# Install database packages
pip install sqlalchemy alembic psycopg2-binary geoalchemy2 redis

# Install utilities
pip install python-jose passlib cryptography python-dotenv

# Install development tools
pip install pytest pytest-asyncio httpx black flake8

# Freeze to requirements.txt
pip freeze > backend/requirements.txt
```

#### Step 3: Install Frontend Dependencies

```bash
cd frontend

npm install \
  react@18.2.0 \
  react-dom@18.2.0 \
  react-router-dom@6.20.0 \
  axios@1.6.2 \
  @tanstack/react-query@5.25.0 \
  tailwindcss@3.3.6 \
  autoprefixer@10.4.16 \
  postcss@8.4.32 \
  recharts@2.10.3 \
  react-leaflet@4.2.1 \
  leaflet@1.9.4 \
  @mantine/hooks@7.2.2 \
  clsx@2.0.0 \
  date-fns@2.30.0

# Dev dependencies
npm install -D \
  vite@5.0.8 \
  @vitejs/plugin-react@4.2.1 \
  eslint@8.56.0 \
  eslint-plugin-react@7.33.2

# Create package.json scripts
cd ..
```

#### Step 4: Setup Databases (Docker)

```bash
# Install Docker Desktop (if not already installed)
# Windows: https://www.docker.com/products/docker-desktop
# Mac/Linux: https://docs.docker.com/install/

# Create docker-compose.yml in root
# See docker-compose configuration below

# Start PostgreSQL + Redis
docker-compose up -d postgres redis
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    container_name: trinetra_postgres
    environment:
      POSTGRES_USER: trinetra_user
      POSTGRES_PASSWORD: trinetra_password
      POSTGRES_DB: trinetra_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trinetra_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: trinetra_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: trinetra_minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/minio_data
    command: server /minio_data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

#### Step 5: Initialize Backend Configuration

Create `.env` file in root:
```env
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=true

# Database
DATABASE_URL=postgresql://trinetra_user:trinetra_password@localhost:5432/trinetra_db
REDIS_URL=redis://localhost:6379/0

# Object Storage
MINIO_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=trinetra-evidence

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Models
MODEL_PATH=backend/models/best.pt
DEVICE=cuda  # or 'cpu' if no GPU

# Frontend
FRONTEND_URL=http://localhost:5173
```

---

### Phase 2: Model Training (Hours 3-9) - Google Colab

Create `notebooks/train_yolo.ipynb`:

```python
# Cell 1: Install dependencies
!pip install -q ultralytics opencv-python roboflow

# Cell 2: Download dataset from Roboflow (replace with your key)
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_ROBOFLOW_KEY")
project = rf.workspace("").project("traffic-violations")
dataset = project.version(1).download("yolov8")

# Cell 3: Train YOLO
from ultralytics import YOLO

model = YOLO('yolov8s.pt')  # small model for speed
results = model.train(
    data='path/to/data.yaml',
    epochs=50,
    imgsz=640,
    device=0,  # GPU ID
    patience=10,
    save=True,
    conf=0.5
)

# Cell 4: Validate
metrics = model.val()

# Cell 5: Export
model.export(format='onnx')  # or 'torchscript'

# Cell 6: Download best.pt
from google.colab import files
files.download('runs/detect/train/weights/best.pt')
```

Move `best.pt` to `backend/models/best.pt`

---

### Phase 3: Backend API Development (Hours 9-18)

#### Step 6: Create Backend Main Entry Point

Create `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import routers
from app.routers import violations, analytics, auth, health
from app.core.config import settings
from app.inference.model_loader import load_models
from app.db.session import init_db

logger = logging.getLogger(__name__)

# Lifespan: load models at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Loading models...")
    load_models()
    init_db()
    logger.info("Models loaded. API ready.")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="TRINETRA AI API",
    description="Traffic Violation Detection & Risk Analytics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(violations.router, prefix="/api/v1/violations", tags=["violations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "TRINETRA AI - Traffic Violation Detection API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )
```

#### Step 7: Create Core Database Models

Create `backend/app/db/models.py`:
```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    vehicle_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_text = Column(String(16), index=True, unique=False)
    vehicle_type = Column(String(50))
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

class Violation(Base):
    __tablename__ = "violations"
    violation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True))
    camera_id = Column(String(50), index=True)
    types = Column(ARRAY(String), default=[])  # e.g., ["NO_HELMET", "TRIPLE"]
    detected_at = Column(DateTime, index=True, default=datetime.utcnow)
    risk_score = Column(Integer, nullable=True)  # 0-100
    risk_band = Column(String(20))  # LOW, MED, HIGH, CRIT
    status = Column(String(20), default="PENDING")  # PENDING, VERIFIED, REJECTED, ISSUED
    location = Column(Geometry('POINT'))
    report_text = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)

class Evidence(Base):
    __tablename__ = "evidence"
    evidence_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), index=True)
    image_uri = Column(String(500))  # S3/MinIO path
    sha256 = Column(String(64))  # Tamper-evident hash
    prev_hash = Column(String(64), nullable=True)  # Hash chain
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="VIEWER")  # ADMIN, OFFICER, AUDITOR, VIEWER
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class Hotspot(Base):
    __tablename__ = "hotspots"
    hotspot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geometry('POINT'))
    corridor = Column(String(100))
    period = Column(String(50))
    violation_count = Column(Integer)
    risk_weighted = Column(Float)
    computed_at = Column(DateTime, default=datetime.utcnow)
```

#### Step 8: Create Violation Engine

Create `backend/app/engine/violations.py`:
```python
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum

class ViolationType(str, Enum):
    NO_HELMET = "NO_HELMET"
    TRIPLE_RIDING = "TRIPLE_RIDING"
    NO_SEATBELT = "NO_SEATBELT"
    RED_LIGHT = "RED_LIGHT"
    STOP_LINE = "STOP_LINE"
    WRONG_SIDE = "WRONG_SIDE"
    ILLEGAL_PARKING = "ILLEGAL_PARKING"

@dataclass
class ViolationEvent:
    vehicle_id: str
    violations: List[ViolationType]
    frame_id: int
    timestamp: str
    camera_id: str
    speed_kmph: float = 0.0
    ped_count: int = 0
    zone_tags: List[str] = None
    signal_state: str = "GREEN"

class ViolationEngine:
    """Rule-based violation detector"""
    
    def __init__(self):
        self.rules = {
            ViolationType.NO_HELMET: self._check_no_helmet,
            ViolationType.TRIPLE_RIDING: self._check_triple_riding,
            # Add more rules as needed
        }
    
    def detect_violations(self, detections: Dict, frame_id: int) -> List[ViolationEvent]:
        """Detect violations from YOLO detections + context"""
        violations = []
        
        # Example: Check for helmet violations
        for person in detections.get('persons', []):
            if person['helmet'] == False:  # No helmet detected
                violations.append(ViolationType.NO_HELMET)
        
        return violations
    
    def _check_no_helmet(self, detections: Dict) -> bool:
        # Logic to detect helmet violations
        return False
    
    def _check_triple_riding(self, detections: Dict) -> bool:
        # Logic to detect triple riding
        return False
```

#### Step 9: Create Risk Scoring Engine

Create `backend/app/engine/risk.py`:
```python
from typing import Dict
import numpy as np

class RiskEngine:
    """Compute 0-100 risk score with explainability"""
    
    # Weights (tunable)
    WEIGHTS = {
        'severity': 0.30,
        'pedestrians': 0.20,
        'speed': 0.15,
        'school_zone': 0.12,
        'density': 0.10,
        'junction': 0.08,
        'time': 0.05,
    }
    
    # Per-violation base severity (0-1)
    SEVERITY_MAP = {
        'RED_LIGHT': 1.0,
        'WRONG_SIDE': 0.9,
        'NO_HELMET_WITH_CHILD': 0.85,
        'TRIPLE_RIDING': 0.75,
        'NO_HELMET': 0.65,
        'STOP_LINE': 0.55,
        'NO_SEATBELT': 0.50,
        'ILLEGAL_PARKING': 0.40,
    }
    
    def compute_risk_score(self, violation_type: str, context: Dict) -> int:
        """Compute 0-100 risk score"""
        
        # Base severity
        severity = self.SEVERITY_MAP.get(violation_type, 0.5)
        
        # Normalize context features to [0, 1]
        speed_norm = min(context.get('speed_kmph', 0) / 100, 1.0)  # Normalize to max 100 km/h
        ped_norm = min(context.get('ped_count', 0) / 20, 1.0)  # Normalize to max 20 pedestrians
        density_norm = context.get('traffic_density', 0.5)
        
        # Zone bonuses
        school_zone_bonus = 1.0 if 'SCHOOL_ZONE' in context.get('zones', []) else 0.0
        junction_bonus = 1.0 if 'JUNCTION' in context.get('zones', []) else 0.0
        
        # Time-of-day weight
        hour = context.get('hour', 12)
        time_weight = 1.5 if 8 <= hour <= 18 else 1.0  # Higher during peak
        
        # Weighted sum
        raw_score = (
            self.WEIGHTS['severity'] * severity +
            self.WEIGHTS['pedestrians'] * ped_norm +
            self.WEIGHTS['speed'] * speed_norm +
            self.WEIGHTS['school_zone'] * school_zone_bonus +
            self.WEIGHTS['density'] * density_norm +
            self.WEIGHTS['junction'] * junction_bonus +
            self.WEIGHTS['time'] * time_weight
        )
        
        # Sigmoid squash to 0-100
        sigmoid = 1 / (1 + np.exp(-raw_score))
        risk_score = int(sigmoid * 100)
        
        return risk_score, self._get_risk_band(risk_score)
    
    def _get_risk_band(self, score: int) -> str:
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
```

#### Step 10: Create API Endpoints

Create `backend/app/routers/violations.py`:
```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import io
from PIL import Image
import numpy as np
import uuid

from app.inference.model_loader import get_model
from app.engine.violations import ViolationEngine
from app.engine.risk import RiskEngine
from app.db.session import get_db

router = APIRouter()

violation_engine = ViolationEngine()
risk_engine = RiskEngine()

@router.post("/detect")
async def detect_violation(
    file: UploadFile = File(...),
    camera_id: str = "DEMO",
    db = Depends(get_db)
):
    """Detect violations in uploaded image"""
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_np = np.array(image)
        
        # Get model
        model = get_model()
        
        # Run inference
        results = model(image_np)
        detections = results[0].boxes
        
        # Detect violations
        violations = violation_engine.detect_violations(
            {'boxes': detections},
            frame_id=0
        )
        
        # Compute risk
        context = {
            'speed_kmph': 50,
            'ped_count': 3,
            'traffic_density': 0.6,
            'zones': ['SCHOOL_ZONE'],
            'hour': 14,
        }
        
        risk_score, risk_band = risk_engine.compute_risk_score(
            violations[0].name if violations else 'UNKNOWN',
            context
        )
        
        # Store in DB
        violation_id = str(uuid.uuid4())
        
        return {
            "violation_id": violation_id,
            "violations": [v.value for v in violations],
            "risk_score": risk_score,
            "risk_band": risk_band,
            "camera_id": camera_id,
            "status": "PENDING",
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list")
async def list_violations(
    skip: int = 0,
    limit: int = 50,
    db = Depends(get_db)
):
    """List recent violations"""
    # Query DB, return paginated list
    return {
        "violations": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
    }
```

---

### Phase 4: Frontend Development (Hours 24-32)

#### Step 11: Create React App Structure

Create `frontend/src/App.jsx`:
```jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Live from './pages/Live';
import Heatmap from './pages/Heatmap';
import Trends from './pages/Trends';
import Search from './pages/Search';
import Evidence from './pages/Evidence';
import RiskQueue from './pages/RiskQueue';
import Login from './pages/Login';
import './index.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  return (
    <Router>
      {isLoggedIn ? (
        <>
          <Header onLogout={() => {
            localStorage.removeItem('token');
            setIsLoggedIn(false);
          }} />
          <div className="main-container">
            <Routes>
              <Route path="/" element={<Live />} />
              <Route path="/heatmap" element={<Heatmap />} />
              <Route path="/trends" element={<Trends />} />
              <Route path="/search" element={<Search />} />
              <Route path="/evidence/:id" element={<Evidence />} />
              <Route path="/risk-queue" element={<RiskQueue />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </>
      ) : (
        <Routes>
          <Route path="/login" element={<Login onLogin={() => setIsLoggedIn(true)} />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      )}
    </Router>
  );
}

export default App;
```

Create `frontend/src/pages/Live.jsx`:
```jsx
import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import EventCard from '../components/EventCard';
import api from '../api/client';
import '../styles/Live.css';

export default function Live() {
  const { data: violations, isLoading, error } = useQuery({
    queryKey: ['violations'],
    queryFn: () => api.get('/violations/list?limit=50'),
    refetchInterval: 3000,  // Poll every 3s
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="live-container">
      <h1>🚨 Live Violations Feed</h1>
      <div className="event-feed">
        {violations?.data?.violations?.map((v) => (
          <EventCard key={v.violation_id} violation={v} />
        ))}
      </div>
      <div className="kpi-bar">
        <div className="kpi">Today: 1,204 violations</div>
        <div className="kpi">HIGH Risk: 312</div>
        <div className="kpi">Pending: 88</div>
      </div>
    </div>
  );
}
```

Create `frontend/src/components/EventCard.jsx`:
```jsx
import React from 'react';
import RiskBadge from './RiskBadge';
import ViolationTag from './ViolationTag';
import '../styles/EventCard.css';

export default function EventCard({ violation }) {
  const handleVerify = () => {
    // TODO: Call API to mark as verified
    console.log('Verified:', violation.violation_id);
  };

  const handleReject = () => {
    // TODO: Call API to mark as rejected
    console.log('Rejected:', violation.violation_id);
  };

  return (
    <div className="event-card">
      <div className="event-image">
        <img src={violation.thumbnail_uri || '/placeholder.jpg'} alt="Event" />
      </div>
      <div className="event-body">
        <div className="event-header">
          <span className="plate">{violation.vehicle?.plate_text || 'UNKNOWN'}</span>
          <RiskBadge score={violation.risk_score} />
        </div>
        <div className="event-violations">
          {violation.violations?.map((v) => (
            <ViolationTag key={v} type={v} />
          ))}
        </div>
        <div className="event-time">{violation.detected_at}</div>
      </div>
      <div className="event-actions">
        <button onClick={handleVerify} className="btn-verify">✓ Verify</button>
        <button onClick={handleReject} className="btn-reject">✗ Reject</button>
        <a href={`/evidence/${violation.violation_id}`} className="btn-evidence">Evidence</a>
      </div>
    </div>
  );
}
```

---

### Phase 5: Integration & Deployment (Hours 32-48)

#### Step 12: Run Full Stack Locally

```bash
# Terminal 1: PostgreSQL + Redis
docker-compose up postgres redis minio

# Terminal 2: Backend API
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Frontend
cd frontend
npm run dev
# Opens at http://localhost:5173

# Terminal 4 (optional): Flower (task monitoring)
celery -A app.tasks flower
```

#### Step 13: Database Initialization

```bash
# Create DB schema from models
cd backend
python scripts/init_db.py

# Seed mock data
python scripts/seed_data.py

# Run migrations (if using Alembic)
alembic upgrade head
```

---

## 📊 PART 3: BUILD TIMELINE & PRIORITY

### **24-Hour Sprint**
| Hours | Task | Owner | Status |
|-------|------|-------|--------|
| 0-3 | Env setup, dependencies, DB | Team | ⚙️ |
| 3-9 | YOLO training (Colab) | ML Engineer | 🔬 |
| 9-13 | Violation rules + OCR | Backend Dev | 🔧 |
| 13-18 | Risk scoring + API | Backend Dev | 🔧 |
| 18-24 | Live feed UI + Events | Frontend Dev | 💻 |

### **48-Hour Sprint (Extended)**
| Hours | Task | Owner | Status |
|-------|------|-------|--------|
| 24-32 | Heatmap + Trends charts | Frontend Dev | 💻 |
| 32-38 | Congestion + Prediction | ML Engineer | 🔬 |
| 38-42 | Verification workflow | Backend Dev | 🔧 |
| 42-46 | Polish + Demo data | Full Team | ✨ |
| 46-48 | Rehearse + Backup | Full Team | 🎤 |

---

## ✅ SUCCESS CRITERIA

### MVP (Must Have)
- ✅ YOLO detection (vehicle, helmet, plate)
- ✅ 3+ violation types working
- ✅ Risk scoring (0-100)
- ✅ OCR plate reading
- ✅ NL report generation
- ✅ Live dashboard + evidence viewer
- ✅ Heatmap visualization

### Nice to Have
- 🟡 Congestion estimator
- 🟡 Predictive forecasting
- 🟡 Multi-camera support
- 🟡 Full RBAC/Auth

### Skip for Now
- ❌ Real RTSP streams
- ❌ Edge/Jetson deployment
- ❌ LLM report rewriting
- ❌ Mobile app

---

## 🎯 Key Success Factors

1. **Start with the spine (end-to-end)** - don't try to perfect one component
2. **Use pre-trained models** - YOLOv8 is ready; fine-tune on small dataset
3. **Fake external dependencies** - mock camera, signal state, RTO
4. **Beautiful UI** - the dashboard wins hackathons
5. **Rehearse the demo** - script every click, have a fallback video
6. **Tell the story** - it's not "a detector," it's "detect → prioritise → prove → predict"

---

## 🚨 COMMON PITFALLS TO AVOID

| Pitfall | Why It Fails | Fix |
|---------|-------------|-----|
| Training on all 7 violations | Takes weeks, low data | Pick 2-3 (helmet, triple, signal) |
| Building perfect RBAC | Scope creep, time waste | Hard-code 2 roles (Officer, Admin) |
| Real RTSP streams | Networking hell | Use MP4 video loops + image uploads |
| Full database schema | Over-engineering | Use SQLite for hackathon |
| Fancy cloud deployment | CI/CD complexity | Docker Compose local + GCP VM is enough |
| Perfectionist code | Never ships | Prioritize working → clean |

