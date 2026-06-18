# TRINETRA AI - Frontend Dependencies & Quick Reference

## 📦 Frontend (Node.js / React) Dependencies

### package.json

```json
{
  "name": "trinetra-frontend",
  "version": "1.0.0",
  "description": "TRINETRA AI - Traffic Violation Detection Dashboard",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .jsx",
    "format": "prettier --write src"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.25.0",
    "@tanstack/react-query-devtools": "^5.25.0",
    "recharts": "^2.10.3",
    "react-leaflet": "^4.2.1",
    "leaflet": "^1.9.4",
    "tailwindcss": "^3.3.6",
    "clsx": "^2.0.0",
    "date-fns": "^2.30.0",
    "zustand": "^4.4.1",
    "react-hot-toast": "^2.4.1",
    "lucide-react": "^0.292.0"
  },
  "devDependencies": {
    "vite": "^5.0.8",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "eslint": "^8.56.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "prettier": "^3.1.0"
  }
}
```

### Install Command
```bash
npm install
```

---

## 🎨 Frontend Pages Overview

| Page | Component | Purpose |
|------|-----------|---------|
| **Live** | `pages/Live.jsx` | Real-time violation stream with event cards |
| **Heatmap** | `pages/Heatmap.jsx` | GIS map showing violation density + corridors |
| **Trends** | `pages/Trends.jsx` | Time-series charts (hourly, daily, by type) |
| **Search** | `pages/Search.jsx` | Filter violations by plate, type, time, camera |
| **Evidence** | `pages/Evidence.jsx` | Full annotated image + hash + NL report |
| **Risk Queue** | `pages/RiskQueue.jsx` | Officer worklist sorted by risk score |
| **Login** | `pages/Login.jsx` | JWT authentication |

---

## 🧩 Frontend Components

```
components/
├── Header.jsx              # Navigation + logout
├── EventCard.jsx           # Single violation card
├── RiskBadge.jsx          # Risk score visual indicator
├── ViolationTag.jsx       # Violation type badges
├── FactorBreakdown.jsx    # Risk scoring factors display
├── MapLayer.jsx           # React-Leaflet heatmap
├── TrendChart.jsx         # Recharts line/bar graphs
├── CorridorRanking.jsx    # Top violating corridors
├── EvidenceViewer.jsx     # Full evidence display
├── LoadingSpinner.jsx     # Loading state UI
├── ConfirmDialog.jsx      # Modal confirmations
└── FilterBar.jsx          # Search/filter controls
```

---

## 🔌 API Client (Axios)

Create `frontend/src/api/client.js`:

```javascript
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 (redirect to login)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 🎯 Quick Start (3 Commands)

```bash
# 1. Setup backend
cd backend
pip install -r requirements.txt
python scripts/init_db.py

# 2. Setup frontend
cd frontend
npm install

# 3. Start everything (from root)
docker-compose up -d
npm run dev --prefix frontend &
python -m uvicorn backend.app.main:app --reload &
```

Then open: **http://localhost:5173**

---

## 📋 Environment Variables

Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_DEBUG=true
```

---

## 🔑 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/login` | POST | Authenticate user, get JWT |
| `/violations/detect` | POST | Upload image, detect violations |
| `/violations/list` | GET | Get paginated violations |
| `/violations/{id}` | GET | Get violation detail + evidence |
| `/violations/{id}/verify` | POST | Officer verify/reject |
| `/analytics/heatmap` | GET | Get hotspot GeoJSON |
| `/analytics/predict` | GET | Get forecast data |
| `/analytics/trends` | GET | Get time-series trends |

---

## 🚀 Vite Configuration

Create `frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
```

---

## 🎨 Tailwind Configuration

Create `frontend/tailwind.config.js`:

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#ef4444',    // Red for HIGH risk
        success: '#10b981',    // Green for OK
        warning: '#f59e0b',    // Amber for MEDIUM
        danger: '#dc2626',     // Dark red for CRITICAL
      },
    },
  },
  plugins: [],
}
```

---

## 🎥 Demo Script (2-Minute Walkthrough)

```
[00:00] Login page
  - Use credentials: demo / demo123

[00:15] Live feed
  - Show 3-4 violation cards
  - Click "Evidence" on one → full image viewer
  - Show "✓ Verify" button workflow

[00:45] Heatmap
  - Pan/zoom the map
  - Click a hotspot
  - Show "Top Corridors" sidebar

[01:15] Trends page
  - Show violations/hour chart
  - Highlight peak hours (8-10 AM, 5-7 PM)

[01:30] Risk Queue
  - Sort by score (highest first)
  - Show "Officer Recommended" banner

[01:45] Search page
  - Filter by plate "KA-05-AB*"
  - Show export to CSV

[02:00] Conclusion
  - "TRINETRA: Detect → Prioritise → Prove → Predict"
```

---

## 🐛 Common Frontend Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| CORS errors | Backend not running | `docker-compose up` or start API |
| Blank heatmap | No data in DB | Run `seed_data.py` |
| Images not loading | MinIO down | Check `docker-compose ps` |
| Slow polling | Too frequent | Increase query refetch interval |
| Auth 401 | Token expired | Clear localStorage, re-login |

---

## 📱 Responsive Breakpoints

```css
/* Tailwind defaults we use */
sm: 640px   /* tablets */
md: 768px   /* small desktops */
lg: 1024px  /* desktops */
xl: 1280px  /* large screens */
```

Pages adapt:
- Mobile: Full-width cards, vertical layout
- Tablet: 2-column layout
- Desktop: 3+ column, sidebar

---

## 🎭 Color Scheme

```css
Risk Score 0-100:
  0-30:   GREEN (#10b981)     - "LOW"
  30-60:  YELLOW (#f59e0b)    - "MEDIUM"
  60-80:  ORANGE (#ef4444)    - "HIGH"
  80-100: RED (#dc2626)       - "CRITICAL"
```

---

