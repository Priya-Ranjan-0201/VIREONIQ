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
