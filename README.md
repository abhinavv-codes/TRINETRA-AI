# TRINETRA AI - Complete Project

TRINETRA AI is an intelligent traffic violation detection and enforcement platform using computer vision, risk analytics, and predictive intelligence.

## 📁 Project Structure

```
GRIDLOCK/
├── backend/                # FastAPI backend
│   ├── app/               # Core application
│   │   ├── main.py       # Entry point
│   │   ├── routers/      # API endpoints
│   │   ├── engine/       # Business logic
│   │   ├── inference/    # ML models
│   │   ├── db/           # Database
│   │   └── analytics/    # Analytics
│   ├── models/           # Pre-trained weights
│   ├── scripts/          # Utility scripts
│   └── requirements.txt  # Dependencies
│
├── frontend/              # React frontend
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # UI components
│   │   ├── api/          # API client
│   │   ├── hooks/        # React hooks
│   │   └── utils/        # Utilities
│   └── package.json      # Dependencies
│
├── data/                  # Datasets and configs
│   ├── datasets/
│   ├── test_media/
│   └── config/
│
├── notebooks/             # Jupyter notebooks
├── docs/                  # Documentation
└── docker-compose.yml    # Services

```

## 🚀 Quick Start

### 1. Install Dependencies

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

### 2. Start Services

PostgreSQL + Redis + MinIO:
```bash
docker-compose up -d
```

Backend API:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

### 3. Initialize Database

```bash
python backend/scripts/init_db.py
python backend/scripts/seed_data.py
```

### 4. Access the App

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- MinIO: http://localhost:9001

## 🔐 Login Credentials

- **Officer**: demo / demo123
- **Admin**: admin / admin123

## 📊 Features

- **Multi-violation detection** (7+ classes)
- **Risk scoring** (0-100 with explainability)
- **Live violation feed**
- **Heatmap visualization**
- **Trend analysis**
- **Officer worklist** (sorted by risk)
- **Tamper-evident evidence** (hash chains)
- **Predictive analytics**

## 🛠️ Technology Stack

- **Backend**: FastAPI, PyTorch, PostgreSQL, Redis
- **Frontend**: React, Tailwind, Recharts, Leaflet
- **ML**: YOLOv8, PaddleOCR, XGBoost, LightGBM
- **Infra**: Docker, MinIO

## 📖 Documentation

See `/docs` folder for detailed guides:
- `API.md` - API reference
- `ARCHITECTURE.md` - System design
- `SETUP.md` - Installation guide
- `DEPLOYMENT.md` - Production deployment

## 📝 License

Proprietary - TRINETRA AI Hackathon Project
