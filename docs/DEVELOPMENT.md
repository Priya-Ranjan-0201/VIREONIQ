# VIREONIQ — Developer Setup & Local Verification Guide

## 1. Prerequisites

- **Python**: 3.12 (matches `.github/workflows/ci.yml` and `backend/.venv`)
- **Node.js**: 20+ (`npm 10+`)
- **Database**: PostgreSQL 16 + Redis 7 (via Docker Compose or local install); SQLite (`aiosqlite`) works for local offline unit tests and development fallback (`ENVIRONMENT=development` or `test`)
- **Memory**: 4 GB RAM minimum (8 GB recommended)

---

## 2. Quick Setup

### Automated Windows Launcher
From the repository root:
```cmd
run.bat
```

### Manual Backend Setup
```powershell
cd backend

# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install pinned application and dev/test dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 3. Configure local environment variables
copy ..\.env.example .env

# 4. Run development server (requires PostgreSQL or non-production SQLite URL)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API**: `http://localhost:8000`
- **Swagger UI (non-production only)**: `http://localhost:8000/docs`

### Manual Frontend Setup
```powershell
cd frontend
npm ci
npm run dev
```
- **Frontend UI**: `http://localhost:5173`

> To enable dev-only offline mock auth (`demo@vireoniq.com`), set `VITE_ENABLE_MOCK_AUTH=true` in `frontend/.env.local`. Mock auth is stripped/disabled in production builds (`import.meta.env.DEV` gate).

---

## 3. Running Automated Checks

### Backend Verification
```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy .
.\.venv\Scripts\python.exe -m pytest tests/ -q
.\.venv\Scripts\python.exe -m pytest -m benchmark -v
```

### Frontend Verification
```powershell
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

Both suites match the CI checks defined in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
