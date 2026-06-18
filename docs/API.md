# TRINETRA API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/login`) require Bearer token:
```
Authorization: Bearer {token}
```

---

## Auth Endpoints

### POST /auth/login
Login and get JWT token.

**Request:**
```json
{
  "username": "demo",
  "password": "demo123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "role": "OFFICER"
}
```

### GET /auth/me
Get current user info.

**Response:**
```json
{
  "username": "demo",
  "email": "demo@trinetra.ai",
  "role": "OFFICER",
  "is_active": true
}
```

---

## Violations Endpoints

### POST /violations/detect
Detect violations in an image.

**Form Data:**
- `file`: Image file (JPEG/PNG)
- `camera_id`: Camera identifier (string)

**Response:**
```json
{
  "violation_id": "uuid",
  "vehicle_plate": "KA-05-AB-1234",
  "violations": ["NO_HELMET", "TRIPLE_RIDING"],
  "risk_score": 87,
  "risk_band": "HIGH",
  "camera_id": "J17-N",
  "timestamp": "2026-06-18T10:30:45",
  "status": "PENDING"
}
```

### GET /violations/list
Get paginated violations list.

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Page size (default: 50)
- `camera_id`: Filter by camera (optional)
- `status`: Filter by status (optional)

**Response:**
```json
{
  "violations": [...],
  "total": 1000,
  "skip": 0,
  "limit": 50
}
```

### GET /violations/{violation_id}
Get detailed violation info.

**Response:**
```json
{
  "violation_id": "uuid",
  "vehicle_plate": "KA-05-AB-1234",
  "violations": [...],
  "risk_score": 87,
  "evidence_uri": "s3://bucket/evidence.jpg",
  "report": "Motorcycle without helmet at junction...",
  "factors": {
    "severity": 0.30,
    "pedestrians": 0.20,
    "speed": 0.15
  }
}
```

### POST /violations/{violation_id}/verify
Verify or reject a violation.

**Request:**
```json
{
  "action": "VERIFIED",
  "note": "Confirmed by officer"
}
```

---

## Analytics Endpoints

### GET /analytics/heatmap
Get violation hotspots as GeoJSON.

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [77.5946, 12.9716]},
      "properties": {
        "violation_id": "uuid",
        "risk_score": 87,
        "violation_type": "NO_HELMET"
      }
    }
  ]
}
```

### GET /analytics/corridors
Get top violating corridors.

**Query Parameters:**
- `limit`: Top N corridors (default: 10)

**Response:**
```json
{
  "corridors": [
    {
      "corridor": "Bangalore Circle",
      "violation_count": 145,
      "avg_risk_score": 72.5,
      "risk_weighted": 10512
    }
  ]
}
```

### GET /analytics/trends
Get hourly/daily trends.

**Response:**
```json
{
  "data": [
    {
      "timestamp": "2026-06-18 08:00",
      "count": 42,
      "risk_avg": 68.5
    }
  ]
}
```

### GET /analytics/predict
Get 7-day forecasts.

**Response:**
```json
{
  "predictions": [
    {
      "date": "2026-06-19",
      "predicted_violations": 145,
      "confidence": 0.78,
      "recommended_officers": 4
    }
  ]
}
```

### GET /analytics/statistics
Get daily KPI summary.

**Response:**
```json
{
  "total_violations": 342,
  "high_risk_count": 23,
  "critical_count": 5,
  "avg_risk_score": 64.2,
  "pending_count": 18
}
```

---

## Health Endpoints

### GET /health
System health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-06-18T10:30:45",
  "service": "TRINETRA AI"
}
```

### GET /health/ready
Readiness check (deps healthy).

**Response:**
```json
{
  "database": true,
  "models": true,
  "cache": true
}
```

---

## Error Responses

All errors return:
```json
{
  "detail": "Error message"
}
```

### Status Codes
- `200` - OK
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
