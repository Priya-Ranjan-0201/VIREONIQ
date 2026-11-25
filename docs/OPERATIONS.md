# VIREONIQ — Operations & Local Runbook

## 1. System Health Probes

| Probe Endpoint | Purpose | Observed Response Shape |
|:---|:---|:---|
| `GET /health` | Root liveness & active DB `SELECT 1` probe (`backend/main.py`) | `{"status": "ok", "database": "connected" \| "disconnected", "environment": "..."}` |
| `GET /api/v1/health` | API v1 router status (`backend/api/api_v1/router.py`) | `{"status": "ok", "message": "VIREONIQ API is running."}` |

---

## 2. Standard Operational Procedures

### Database Migrations (`backend/alembic/`)
```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Redis Cache Inspection / Reset (Local Dev Only)
```bash
docker compose exec redis redis-cli FLUSHDB
```

### RSA Key Rotation
1. Generate a 2048-bit RSA keypair outside git (`backend/.secrets/` or secret manager):
   ```bash
   openssl genrsa -out private_key.pem 2048
   openssl rsa -in private_key.pem -pubout -out public_key.pem
   ```
2. Provide `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY` (or `JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH`) via environment secrets and restart the backend service.

---

## 3. Degradation & Fallback Behavior

- **Redis unavailable**: `SafeRedis` (`backend/core/redis.py`) logs warnings, falls back to TTL-bounded in-memory rate/blacklist tracking on a 30-second cooldown, and attempts recovery automatically.
- **Judge0 sandbox unavailable**: `code_execution_service.py` returns `status.id = 13` (`Sandbox Unavailable`, `passed = False`) without running host `python -c` commands.
- **LLM APIs unavailable / unconfigured**: Fails over per gateway configuration (`core/llm/`) or returns explicit unavailable responses.

---

## 4. Rollback & Deployment Procedures

### Automated Container Rollback
If a new release fails healthchecks or generates elevated 5xx error rates:
1. Re-tag and deploy previous known-good image SHA:
   ```bash
   docker compose pull vireoniq-backend:<PREVIOUS_GIT_SHA>
   docker compose up -d --no-deps backend
   ```
2. Verify liveness immediately:
   ```bash
   curl -f http://localhost:8000/health
   ```

### Database Schema Rollback
If an Alembic migration fails in staging/production:
```bash
docker compose exec backend alembic downgrade -1
```
*Note*: Never introduce destructive schema drops (e.g. `DROP COLUMN`) in single-step migrations; use two-phase expand/contract deployments.

---

## 5. Observability, Metrics & Telemetry

- **Prometheus Metrics**: Exposes HTTP request latency, status codes, Celery queue depth, and LLM token usage counters.
- **Structured JSON Logging**: Every log entry contains `timestamp`, `level`, `event`, and `request_id` via `structlog`. PII (emails, names, tokens) is redacted before output.
- **Distributed Tracing**: OpenTelemetry instrumentation tracks database query execution and external service roundtrips without transmitting payload bodies.

