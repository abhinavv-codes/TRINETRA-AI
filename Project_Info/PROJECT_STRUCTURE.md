# TRINETRA AI - Complete Project Structure

```
trinetra/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI entry point
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── violations.py       # POST /violations/detect, GET /violations
│   │   │   ├── analytics.py        # GET /heatmap, /predict, /trends
│   │   │   ├── evidence.py         # Evidence viewer & download
│   │   │   ├── auth.py             # POST /auth/login, JWT handlers
│   │   │   └── health.py           # Health checks
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Settings, env vars
│   │   │   ├── security.py         # JWT, password hashing, auth
│   │   │   ├── junctions.py        # Junction config loader (JSON)
│   │   │   └── constants.py        # Violation types, risk bands
│   │   │
│   │   ├── inference/
│   │   │   ├── __init__.py
│   │   │   ├── yolo.py             # YOLO detector wrapper
│   │   │   ├── tracker.py          # ByteTrack wrapper
│   │   │   ├── ocr.py              # PaddleOCR wrapper
│   │   │   └── model_loader.py     # Singleton model management
│   │   │
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── violations.py       # Violation rules engine (7+ classes)
│   │   │   ├── risk.py             # Risk scoring (0-100 formula + ML)
│   │   │   ├── congestion.py       # Parking congestion estimator
│   │   │   ├── report.py           # NL report generator + templating
│   │   │   └── evidence.py         # Evidence image annotation + hashing
│   │   │
│   │   ├── analytics/
│   │   │   ├── __init__.py
│   │   │   ├── heatmap.py          # KDE hotspot generation
│   │   │   ├── trends.py           # Time-series aggregation
│   │   │   ├── corridors.py        # Corridor ranking
│   │   │   └── predict.py          # Predictive forecasting (LightGBM/Prophet)
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy ORM models
│   │   │   ├── schemas.py          # Pydantic schemas for API
│   │   │   ├── session.py          # DB session/connection management
│   │   │   └── migrations/
│   │   │       ├── env.py          # Alembic config
│   │   │       └── versions/       # Alembic migration files
│   │   │
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   └── evidence.py         # Save/retrieve evidence from S3/MinIO
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py           # Logging setup
│   │       ├── validators.py       # Input validation helpers
│   │       └── geometry.py         # Zone polygon, homography utilities
│   │
│   ├── models/
│   │   └── best.pt                 # Trained YOLOv8 weights (generated after training)
│   │
│   ├── config/
│   │   ├── junctions/
│   │   │   ├── junction_j17.json   # Junction config (zones, allowed dirs, etc.)
│   │   │   └── junction_j05.json
│   │   ├── requirements.txt         # Python dependencies
│   │   └── .env.example            # Environment template
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_inference.py       # Model & inference tests
│   │   ├── test_violations.py      # Violation engine tests
│   │   ├── test_risk.py            # Risk scoring tests
│   │   ├── test_api.py             # API endpoint tests
│   │   └── fixtures/
│   │       └── sample_frames/      # Test images
│   │
│   ├── scripts/
│   │   ├── train_yolo.py           # YOLO training script
│   │   ├── init_db.py              # Initialize DB schema
│   │   ├── seed_data.py            # Seed mock data
│   │   └── download_datasets.py    # Fetch public datasets
│   │
│   ├── requirements.txt             # Python deps (copy from dependencies)
│   ├── Dockerfile                   # Container image
│   └── .dockerignore
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx                # React entry
│   │   ├── App.jsx                 # Root component
│   │   ├── index.css               # Global styles (Tailwind)
│   │   │
│   │   ├── pages/
│   │   │   ├── Live.jsx            # Live violations feed
│   │   │   ├── Heatmap.jsx         # KDE hotspot map
│   │   │   ├── Trends.jsx          # Time-series charts
│   │   │   ├── Search.jsx          # Filter & search
│   │   │   ├── Evidence.jsx        # Full evidence viewer
│   │   │   ├── RiskQueue.jsx       # Officer worklist (sorted by risk)
│   │   │   ├── DeploymentPlan.jsx  # Predictive staffing
│   │   │   └── Login.jsx           # Auth page
│   │   │
│   │   ├── components/
│   │   │   ├── EventCard.jsx       # Live event card component
│   │   │   ├── MapLayer.jsx        # React-Leaflet heatmap
│   │   │   ├── TrendChart.jsx      # Recharts line/bar charts
│   │   │   ├── CorridorRanking.jsx # Top corridors sidebar
│   │   │   ├── EvidenceViewer.jsx  # Annotated image + hash + report
│   │   │   ├── RiskBadge.jsx       # Risk score indicator (colored)
│   │   │   ├── ViolationTag.jsx    # Violation type badges
│   │   │   ├── FactorBreakdown.jsx # Risk score component breakdown
│   │   │   ├── Header.jsx          # Nav + logout
│   │   │   └── LoadingSpinner.jsx  # Loading state
│   │   │
│   │   ├── api/
│   │   │   ├── client.js           # Axios/fetch API client
│   │   │   ├── violations.js       # /violations endpoints
│   │   │   ├── analytics.js        # /analytics endpoints
│   │   │   └── auth.js             # Auth helpers
│   │   │
│   │   ├── hooks/
│   │   │   ├── useViolations.js    # React Query hook for violations
│   │   │   ├── useAnalytics.js     # Hook for analytics data
│   │   │   ├── useAuth.js          # Auth state management
│   │   │   └── usePoll.js          # Polling hook
│   │   │
│   │   ├── utils/
│   │   │   ├── formatters.js       # Date, risk band, formatting
│   │   │   ├── constants.js        # Violation labels, colors
│   │   │   └── storage.js          # LocalStorage token management
│   │   │
│   │   └── styles/
│   │       └── tailwind.config.js
│   │
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite build config
│   ├── Dockerfile                  # Frontend container
│   └── .dockerignore
│
├── notebooks/
│   ├── train_yolo.ipynb            # Google Colab training notebook
│   ├── data_analysis.ipynb         # Dataset EDA
│   └── sample_inference.ipynb      # Test inference on sample frames
│
├── data/
│   ├── datasets/
│   │   ├── train/
│   │   │   ├── images/
│   │   │   └── labels/
│   │   ├── val/
│   │   │   ├── images/
│   │   │   └── labels/
│   │   └── test/
│   │       ├── images/
│   │       └── labels/
│   │
│   ├── data.yaml                   # YOLO dataset config
│   ├── junctions/
│   │   └── (junction configs)
│   │
│   └── test_media/
│       ├── sample_frames/          # Test JPGs
│       └── demo_videos/            # Short MP4s for demo
│
├── docker-compose.yml              # Multi-container orchestration
├── docker-compose.dev.yml          # Development variant
│
├── .github/
│   └── workflows/
│       ├── tests.yml               # CI/CD: run tests
│       └── deploy.yml              # CI/CD: build & push images
│
├── scripts/
│   ├── setup.sh                    # One-command setup (Linux/Mac)
│   ├── setup.bat                   # One-command setup (Windows)
│   ├── start_dev.sh                # Start local dev stack
│   └── prepare_demo.sh             # Prep demo data
│
├── docs/
│   ├── API.md                      # API reference
│   ├── ARCHITECTURE.md             # System architecture
│   ├── SETUP.md                    # Setup instructions
│   ├── DEPLOYMENT.md               # Cloud deployment guide
│   └── DEMO.md                     # Demo script & walkthrough
│
├── .env.example                    # Environment template
├── .gitignore
├── README.md                       # Project overview
├── LICENSE
└── CONTRIBUTING.md

```

## 📁 Key Folder Purposes

| Folder | Purpose |
|---|---|
| `backend/app` | Core FastAPI application code |
| `backend/models` | Pre-trained YOLO weights |
| `backend/config` | Junction configs & settings |
| `backend/tests` | Unit & integration tests |
| `frontend/src` | React application source |
| `notebooks` | Jupyter notebooks for training & exploration |
| `data` | Datasets, test media, junction configs |
| `scripts` | Setup & utility scripts |
| `docs` | Documentation |

## 🗂️ Database Schema Location
- ORM models: `backend/app/db/models.py`
- Alembic migrations: `backend/app/db/migrations/versions/`

## 🚀 Important Files to Understand
1. **Backend entry**: `backend/app/main.py`
2. **Frontend entry**: `frontend/src/main.jsx`
3. **Orchestration**: `docker-compose.yml`
4. **Config example**: `.env.example`
5. **Model weights**: `backend/models/best.pt` (generated after training)
