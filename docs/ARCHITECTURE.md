# TRINETRA Architecture

## System Overview

```
┌─────────────────┐
│   React SPA     │
│   (Vite 5.0)    │
└────────┬────────┘
         │
         │ HTTP/REST
         │
    ┌────▼─────────────────────┐
    │    FastAPI Backend        │
    │    (0.104.1)              │
    │  ┌──────────────────────┐ │
    │  │ Routers & Endpoints  │ │
    │  │ - Health             │ │
    │  │ - Auth               │ │
    │  │ - Violations         │ │
    │  │ - Analytics          │ │
    │  └──────────────────────┘ │
    │  ┌──────────────────────┐ │
    │  │ Business Logic       │ │
    │  │ - Risk Scoring       │ │
    │  │ - Rule Engine        │ │
    │  │ - Report Gen         │ │
    │  │ - Evidence Manager   │ │
    │  └──────────────────────┘ │
    │  ┌──────────────────────┐ │
    │  │ ML Inference         │ │
    │  │ - YOLOv8 Detection   │ │
    │  │ - PaddleOCR          │ │
    │  │ - Model Loader       │ │
    │  └──────────────────────┘ │
    └────┬──────────────────────┘
         │
    ┌────┼──────────┬──────────┬──────────┐
    │    │          │          │          │
    │ ┌──▼──┐  ┌─────▼───┐ ┌──▼──┐  ┌───▼──┐
    │ │ DB  │  │ Cache   │ │ S3  │  │Config│
    │ │PG15 │  │ Redis   │ │MinIO│  │JSON  │
    │ │PostGIS│ │ 7.0    │ │ S3  │  │      │
    │ └─────┘  └─────────┘ └─────┘  └──────┘
    └────────────────────────────────────────

```

## Backend Layers

### 1. **Routers** (API Gateway)
Location: `app/routers/`
- `health.py` - Health checks
- `auth.py` - Authentication & authorization
- `violations.py` - Detection & verification endpoints
- `analytics.py` - Analytics & forecasting endpoints

**Pattern:** FastAPI route handlers with dependency injection

### 2. **Engines** (Business Logic)
Location: `app/engine/`
- `violations.py` - Rule-based violation detection
- `risk.py` - Risk scoring algorithm (0-100)
- `congestion.py` - Impact estimation
- `report.py` - Report generation
- `evidence.py` - Tamper-detection proof

**Pattern:** Stateless processors with explainability

### 3. **Inference** (ML Models)
Location: `app/inference/`
- `model_loader.py` - Singleton pattern model loading
- `yolo.py` - YOLOv8 object detection wrapper
- `ocr.py` - PaddleOCR license plate recognition (stub)
- `tracking.py` - Multi-object tracking (stub)

**Pattern:** Lazy loading with GPU management

### 4. **Database** (Persistence)
Location: `app/db/`
- `models.py` - SQLAlchemy ORM (8 tables)
- `session.py` - Connection pooling
- `schemas.py` - Pydantic validation

**Tables:**
- Vehicle, Violation, Evidence
- User, Hotspot, Analytics
- AuditLog

### 5. **Analytics** (Insights)
Location: `app/analytics/`
- `heatmap.py` - KDE hotspot generation
- `trends.py` - Time-series aggregation
- `corridors.py` - Corridor ranking
- `predict.py` - Violation forecasting

**Pattern:** Stateless aggregators

### 6. **Storage** (S3/MinIO)
Location: `app/storage/`
- `evidence.py` - Object storage wrapper

### 7. **Utils** (Helpers)
Location: `app/utils/`
- `logger.py` - Centralized logging
- `validators.py` - Input validation

---

## Frontend Architecture

```
React App (Vite)
├── Pages (Route components)
│   ├── Live - Real-time feed
│   ├── Heatmap - GIS visualization
│   ├── Trends - Time-series charts
│   ├── Search - Filter & search
│   ├── Evidence - Detail viewer
│   └── RiskQueue - Officer worklist
│
├── Components (Reusable UI)
│   ├── Header - Navigation
│   ├── RiskBadge - Risk indicator
│   ├── ViolationTag - Type badge
│   └── Dialogs - Confirmations
│
├── Hooks (State management)
│   ├── useViolations - Fetch & poll
│   ├── useAnalytics - Dashboard data
│   ├── useAuth - Authentication
│   └── usePoll - Polling logic
│
├── API (Data layer)
│   ├── client.js - Axios + interceptors
│   ├── violations.js - Violation endpoints
│   ├── analytics.js - Analytics endpoints
│   └── auth.js - Auth endpoints
│
└── Utils (Helpers)
    ├── formatters.js - Date, risk, colors
    ├── constants.js - Enums & mappings
    └── storage.js - LocalStorage helpers
```

---

## Data Flow

### Detection Flow
```
Image → YOLOv8 → Detections
         ↓
   PaddleOCR → Plate
         ↓
  Rule Engine → Violations List
         ↓
  Risk Engine → Risk Score + Factors
         ↓
  Evidence Mgr → Hash Chain
         ↓
   Report Gen → Natural Language
         ↓
   DB Insert → Immutable Record
         ↓
   Frontend ← Response (JSON)
```

### Analytics Flow
```
DB Queries → Violation Records
     ↓
 Aggregators → Trends, Corridors
     ↓
 Heatmap Gen → GeoJSON Points
     ↓
 Prediction → Forecasts (7d)
     ↓
 Frontend ← Charts & Maps
```

---

## Deployment Stack

**Development:**
- Docker Compose (PostgreSQL, Redis, MinIO)
- Vite HMR (Frontend)
- Uvicorn reload (Backend)

**Production:**
- Kubernetes (AKS)
- Managed PostgreSQL (Azure)
- Redis Cache (Azure Cache)
- Blob Storage (Azure Blob)

---

## Key Design Patterns

1. **Dependency Injection** - FastAPI dependencies
2. **Singleton** - Model loader
3. **Repository** - Database access
4. **Factory** - Engine creation
5. **Decorator** - Route authentication
6. **Observer** - Real-time polling
