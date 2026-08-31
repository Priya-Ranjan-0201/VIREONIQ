# VIREONIQ X — Operations & Production Runbook

## 1. System Health & Probes

| Probe Endpoint | Purpose | Normal Response |
|:---|:---|:---|
| `GET /api/v1/health` | Application liveness and PostgreSQL/Redis connectivity | `{"status": "ok", "database": "connected"}` |
| `GET /api/v1/health/db` | Detailed database connection pool metrics | `{"pool_size": 20, "checked_out": 2}` |

---

## 2. Standard Operational Procedures

### Database Migrations
```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

### Redis Cache Purge / Reset
```bash
redis-cli -h localhost -p 6379 FLUSHDB
```

### SSL / JWT Key Rotation
1. Generate new RSA keypair:
   ```bash
   openssl genrsa -out private_key.pem 2048
   openssl rsa -in private_key.pem -pubout -out public_key.pem
   ```
2. Update `.env` with new key content and restart backend service. Existing active tokens remain valid until expiration.

---

## 3. Incident Escalation Protocol

1. **Severity 1 (P0)**: Service Outage / Database Unreachable $\rightarrow$ Runbook automated fallback $\rightarrow$ Page on-call lead.
2. **Severity 2 (P1)**: LLM Gateway High Error Rate ($>5\%$) $\rightarrow$ Automatic fallback to deterministic mock logic triggers transparently; monitor LLM quota.
3. **Severity 3 (P2)**: Degraded Non-Critical Endpoint $\rightarrow$ Log correlation ID and investigate within 4 hours.
