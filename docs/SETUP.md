# Setup & Installation Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Git

## Backend Setup

### 1. Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Variables
```bash
cp .env.example .env
# Edit .env with your values
```

### 4. Start Services
In separate terminals:

**PostgreSQL + Redis + MinIO:**
```bash
docker-compose up -d
```

**API Server:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Initialize Database
```bash
python scripts/init_db.py
python scripts/seed_data.py
```

### 6. Verify Backend
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Variables
```bash
cp .env.example .env
# VITE_API_URL defaults to http://localhost:8000/api/v1
```

### 3. Start Dev Server
```bash
npm run dev
```

### 4. Access Frontend
- http://localhost:5173

---

## Verification Checklist

- [ ] Backend API responding (http://localhost:8000/health)
- [ ] Frontend loads (http://localhost:5173)
- [ ] Can login with demo/demo123
- [ ] Database tables created
- [ ] Mock data seeded
- [ ] Swagger UI accessible (http://localhost:8000/docs)

---

## Docker Services

Check service health:
```bash
docker-compose ps

docker logs trinetra_postgres
docker logs trinetra_redis
docker logs trinetra_minio
```

Access MinIO console:
- http://localhost:9001
- Username: minioadmin
- Password: minioadmin

---

## Development Tips

### Hot Reload
- Backend: Uvicorn auto-reloads on file changes
- Frontend: Vite HMR preserves state

### Database Migrations
(Alembic configured but not yet initialized)
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Testing
Backend tests (TODO):
```bash
pytest tests/
```

Frontend tests (TODO):
```bash
npm run test
```

### Linting
Backend:
```bash
black app/
flake8 app/
```

Frontend:
```bash
npm run lint
```

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Error
```bash
# Check PostgreSQL is running
docker-compose ps trinetra_postgres

# Check connection string in .env
```

### Import Errors
```bash
# Reinstall in isolated venv
python -m venv venv_new
./venv_new/bin/pip install -r requirements.txt
```

### CORS Issues
- Frontend and backend must be configured correctly
- Check `FRONTEND_URL` and `BACKEND_URL` in configs

---

## Next Steps

1. Upload YOLO model weights to `backend/models/best.pt`
2. Configure actual video streams
3. Deploy to Azure AKS (see DEPLOYMENT.md)
4. Set up CI/CD pipeline (GitHub Actions)
