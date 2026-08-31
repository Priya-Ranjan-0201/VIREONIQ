# VIREONIQ X — Developer Setup & Clean-Clone Guide

## 1. Prerequisites

- **Python**: 3.10+ (Python 3.12 recommended)
- **Node.js**: 18.0+ (Node.js 20+ recommended)
- **Database**: PostgreSQL 15+ (Local or Docker) / SQLite (Built-in zero-config fallback)
- **Memory**: 4GB RAM minimum (8GB recommended)

---

## 2. Quick Setup

### Automated Windows Launcher (Recommended)
Simply run the interactive setup & startup wizard from the repository root:
```cmd
run.bat
```

### Manual Setup

#### Backend Setup:
```powershell
cd backend

# 1. Create Virtual Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Configure Environment
copy .env.example .env

# 4. Initialize Database & Run Server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Frontend Setup:
```powershell
cd frontend

# 1. Install Node Dependencies
npm install

# 2. Start Vite Dev Server
npm run dev
```
- **Frontend UI**: [http://localhost:5173](http://localhost:5173)

---

## 3. Running Automated Tests

Run the complete 16-phase test suite:
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
Expected result: **147 passed** in ~8.2 seconds.

---

## 4. Production Build Verification

Build the production frontend bundle:
```powershell
cd frontend
npm run build
```
Expected result: **0 TypeScript / Vite compile errors**.
