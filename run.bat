 @echo off
setlocal EnableDelayedExpansion

:: ─────────────────────────────────────────────────────────────
::   VIREONIQ X — Startup Wizard v16.0.0-rc1
::   AI Career Intelligence & Autonomous Career OS
:: ─────────────────────────────────────────────────────────────

title VIREONIQ X Startup Wizard

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║               VIREONIQ X — STARTUP WIZARD                 ║
echo  ║       AI Career Intelligence Platform v16.0.0-rc1         ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
echo  Select your execution mode:
echo.
echo    [1]  Full Docker Stack (Production Grade)
echo    [2]  Native Mode (Start FastAPI Backend + Vite Frontend)
echo    [3]  First-Time Setup (Install Python ^& Node Dependencies)
echo    [4]  Start Data Services Only (Postgres, Redis, Mongo, Qdrant)
echo    [5]  Run Complete Automated Test Suite (147 Tests)
echo    [6]  Stop All Docker Services
echo    [7]  Exit
echo.

set /p mode="  Enter choice (1-7): "

if "%mode%"=="1" goto DOCKER_FULL
if "%mode%"=="2" goto NATIVE
if "%mode%"=="3" goto SETUP
if "%mode%"=="4" goto DATA_SERVICES
if "%mode%"=="5" goto RUN_TESTS
if "%mode%"=="6" goto STOP_DOCKER
if "%mode%"=="7" goto EXIT

echo [ERROR] Invalid choice. Please enter 1-7.
pause
goto EXIT

:: ─────────────────────────────────────────────────────────
::  OPTION 1: Full Docker Compose (all services)
:: ─────────────────────────────────────────────────────────
:DOCKER_FULL
echo.
echo [INFO] Starting the full VIREONIQ X stack via Docker Compose in background...
echo [INFO] This includes: Postgres, Redis, MongoDB, Qdrant, Backend, Frontend, Nginx
docker-compose up -d --build
echo.
echo [OK] All containers are running in the background!
echo    Frontend UI      : http://localhost (or http://localhost:5173 for dev)
echo    Backend API Docs : http://localhost:8000/docs
echo    Login Credentials: test@example.com / password
echo.
pause
goto EXIT

:: ─────────────────────────────────────────────────────────
::  OPTION 2: Native Mode
:: ─────────────────────────────────────────────────────────
:NATIVE
echo.
echo ────────────────────────────────────────────────────
echo  Starting VIREONIQ X in Native Mode
echo ────────────────────────────────────────────────────

:: Kill any stale processes on ports 8000 and 5173
echo [INFO] Cleaning up stale processes on ports 8000 and 5173...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 "') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":5173 "') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Start data services via Docker if available
echo [INFO] Checking Docker daemon status...
tasklist /fi "imagename eq docker.exe" 2>nul | findstr /i "docker.exe" >nul
if %errorlevel% equ 0 (
    echo [INFO] Checking if Docker daemon is responsive (2s timeout)...
    powershell -Command "if (Start-Job -ScriptBlock { docker ps } | Wait-Job -Timeout 2) { exit 0 } else { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        docker-compose up -d postgres redis mongodb qdrant
        echo [OK] Data services started (Postgres, Redis, MongoDB, Qdrant).
    ) else (
        echo [WARNING] Docker daemon is unresponsive.
        echo           Starting in SQLite + In-Memory Fallback mode.
    )
) else (
    echo [WARNING] Docker not detected.
    echo           Starting in SQLite + In-Memory Fallback mode.
)

:: Wait briefly for containers to stabilize
timeout /t 3 /nobreak >nul

:: Start Backend
echo.
echo [INFO] Starting Backend (FastAPI) on http://localhost:8000 ...
if exist backend\.venv\Scripts\activate.bat (
    start "VIREONIQ X Backend" cmd /k "cd /d %~dp0backend && call .venv\Scripts\activate.bat && set PYTHONPATH=. && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) else (
    echo [WARNING] backend\.venv not found. Attempting global Python...
    start "VIREONIQ X Backend" cmd /k "cd /d %~dp0backend && set PYTHONPATH=. && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
)

:: Start Frontend
echo [INFO] Starting Frontend (Vite) on http://localhost:5173 ...
start "VIREONIQ X Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ────────────────────────────────────────────────────
echo  VIREONIQ X is launching in separate windows!
echo ────────────────────────────────────────────────────
echo.
echo    Backend API Docs : http://localhost:8000/docs
echo    Frontend UI      : http://localhost:5173
echo    Login Credentials: test@example.com / password
echo.
pause
goto EXIT

:: ─────────────────────────────────────────────────────────
::  OPTION 3: First-Time Environment Setup
:: ─────────────────────────────────────────────────────────
:SETUP
echo.
echo ────────────────────────────────────────────────────
echo  First-Time Environment Setup
echo ────────────────────────────────────────────────────

:: Start data services
echo.
echo [STEP 1/5] Starting data services via Docker...
tasklist /fi "imagename eq docker.exe" 2>nul | findstr /i "docker.exe" >nul
if %errorlevel% equ 0 (
    echo [INFO] Checking if Docker daemon is responsive (2s timeout)...
    powershell -Command "if (Start-Job -ScriptBlock { docker ps } | Wait-Job -Timeout 2) { exit 0 } else { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        docker-compose up -d postgres redis mongodb qdrant
        echo [OK] Postgres, Redis, MongoDB, Qdrant started.
    ) else (
        echo [WARNING] Docker daemon is unresponsive.
        echo           Assuming SQLite + In-Memory fallback mode for setup.
    )
) else (
    echo [WARNING] Docker not found.
    echo           Assuming SQLite + In-Memory fallback mode for setup.
)

:: Wait for Postgres to accept connections
echo [INFO] Waiting for Postgres to be ready...
timeout /t 5 /nobreak >nul

:: Create Python virtual environment
echo.
echo [STEP 2/5] Setting up Python virtual environment...
cd /d %~dp0backend
if not exist .venv (
    echo [INFO] Creating virtual environment in backend\.venv ...
    python -m venv .venv 2>nul || py -m venv .venv 2>nul || python3 -m venv .venv 2>nul
    if not exist .venv (
        echo [ERROR] Failed to create virtual environment.
        echo         Ensure Python 3.10+ is installed and on PATH.
        pause
        goto EXIT
    )
)
call .venv\Scripts\activate.bat

:: Install Python dependencies
echo.
echo [STEP 3/5] Installing Python dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed. Check your Python/pip installation.
    pause
    goto EXIT
)

:: Generate RSA keys and initialize database
echo.
echo [STEP 4/5] Generating RSA keys and initializing database...
set PYTHONPATH=.
if not exist .secrets\private_key.pem (
    echo [INFO] Generating RS256 key pair...
    python scripts\generate_keys.py
)
echo [INFO] Creating database tables...
python scripts\init_db_schema.py
echo [INFO] Seeding default user (test@example.com / password)...
python scripts\seed_user.py

cd /d %~dp0

:: Install Node.js dependencies
echo.
echo [STEP 5/5] Installing Frontend (Node.js) dependencies...
cd /d %~dp0frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed. Check your Node.js/npm installation.
    pause
    goto EXIT
)
cd /d %~dp0

echo.
echo ════════════════════════════════════════════════════
echo  Setup Complete!
echo ════════════════════════════════════════════════════
echo.
echo  Login credentials: test@example.com / password
echo.
echo  Next steps:
echo    - Run this wizard again and select [2] Native Mode
echo    - Or select [1] Full Docker Stack
echo.
pause
goto EXIT

:: ─────────────────────────────────────────────────────────
::  OPTION 4: Data Services Only
:: ─────────────────────────────────────────────────────────
:DATA_SERVICES
echo.
echo [INFO] Starting data services only (Postgres, Redis, MongoDB, Qdrant)...
docker-compose up -d postgres redis mongodb qdrant
echo.
echo [OK] Data services are running:
echo    PostgreSQL : localhost:5432
echo    Redis      : localhost:6379
echo    MongoDB    : localhost:27017
echo    Qdrant     : localhost:6333
echo.
pause
goto EXIT

:: ─────────────────────────────────────────────────────────
::  OPTION 5: Run Automated Test Suite (147 Tests)
:: ─────────────────────────────────────────────────────────
:RUN_TESTS
echo.
echo ────────────────────────────────────────────────────
echo  Running Complete Automated Test Suite (147 Tests)
echo ────────────────────────────────────────────────────
cd /d %~dp0backend
if exist .venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe -m pytest -v
) else (
    python -m pytest -v
)
cd /d %~dp0
echo.
pause
goto EXIT

:: ─────────────────────────────────────────────────────────
::  OPTION 6: Stop Docker
:: ─────────────────────────────────────────────────────────
:STOP_DOCKER
echo.
echo [INFO] Stopping all Docker containers...
docker-compose down
echo [OK] All services stopped.
pause
goto EXIT

:: ─────────────────────────────────────────────────────────
::  EXIT
:: ─────────────────────────────────────────────────────────
:EXIT
echo.
echo [INFO] Wizard finished.
