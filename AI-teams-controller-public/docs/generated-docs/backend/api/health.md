# Health Check API

System health and component status endpoints.

## Endpoints

### Basic Health

```http
GET /health
```

Always returns 200 if server is running.

### Detailed Health

```http
GET /health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "redis": {"status": "up", "latency_ms": 1.2},
    "celery": {"status": "up", "workers": 1},
    "pubsub": {"status": "up", "task_alive": true},
    "websocket": {"status": "up", "clients": 3}
  },
  "timestamp": "2026-01-18T12:00:00Z"
}
```

**Status values:** `healthy`, `degraded`, `unhealthy`

### Individual Components

```http
GET /health/redis    # Redis connectivity
GET /health/celery   # Celery worker status
GET /health/pubsub   # Redis pub/sub listener
GET /health/voice    # Voice feedback pipeline
```

## Status Meanings

| Status | Meaning |
|--------|---------|
| `healthy` | All components operational |
| `degraded` | Some components down, core functions work |
| `unhealthy` | Critical components down |
