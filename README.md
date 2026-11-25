<div align="center">

# VIREONIQ — AI Career & Workforce Intelligence Platform

### Evidence-Focused Career Preparation, ATS Resume Studio & Interview Simulation

[![License](https://img.shields.io/badge/License-See_LICENSE_File-red.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Stage-Hardened_Beta-orange.svg?style=for-the-badge)](docs/IMPROVEMENT_REPORT.md)
[![Developed by](https://img.shields.io/badge/Developed%20By-Priya%20Ranjan-8A2BE2.svg?style=for-the-badge&logo=github)](https://github.com/Priya-Ranjan-0201)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.141-009688.svg?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18.2-61DAFB.svg?style=flat-square&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-5.2_(Strict)-3178C6.svg?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/TailwindCSS-4.3-38B2AC.svg?style=flat-square&logo=tailwindcss&logoColor=white" alt="TailwindCSS" />
  <img src="https://img.shields.io/badge/Vite-5.4-646CFF.svg?style=flat-square&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-7-DC382D.svg?style=flat-square&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/MongoDB-7-47A248.svg?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Qdrant-Vector_DB-E50914.svg?style=flat-square&logo=qdrant&logoColor=white" alt="Qdrant" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
</p>

</div>

---

**VIREONIQ** is an evidence-oriented career preparation and workforce analytics platform built with **FastAPI** and **React + TypeScript**. It organizes resume parsing, deterministic Python AST complexity analysis, interview simulations, skill evidence tracking, and recruiter candidate ranking around a unified Career Twin data model.

See [docs/BASELINE.md](docs/BASELINE.md), [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md), and [docs/IMPROVEMENT_REPORT.md](docs/IMPROVEMENT_REPORT.md) for current verification metrics, architectural caveats, and pending maintenance decisions.

---

## Core Platform Capabilities

- **Career Digital Twin**: Aggregates `SkillEvidence`, `ProjectEvidence`, `AssessmentResult`, and temporal decay calculations (`services/career_digital_twin_service.py`, `services/evidence_graph_service.py`).
- **MNC ATS Resume Studio**: Computes deterministic 6-dimension ATS rubric scores and rule-based suggestions across **30 configured company profiles** and **15 engineering role keyword taxonomies**, paired with **6 React preview/print templates**.
- **Readiness & Gap Optimization**: Multi-dimensional readiness scoring, bottleneck ranking, and counterfactual what-if trajectory simulation (`services/career_readiness_engine.py`, `services/counterfactual_simulation_service.py`).
- **Deterministic Python AST & Interview Studio**: Static Python AST time/space complexity evaluation alongside interview simulation workflows and Judge0-backed sandbox execution (`Sandbox Unavailable` fail-closed when offline).
- **Cryptographic Talent Passport**: Data-minimized public credential links signed with `CREDENTIAL_SIGNING_KEY` HMAC-SHA256 verification.
- **Multi-Tenant Recruiter & Organization Views**: Role-gated (`require_roles`) job matching and organizational capability matrix views under `/api/v1/recruiter-intel` and `/api/v1/org`.

---

## System Architecture

```text
Frontend (React 18, TS Strict)      Backend (FastAPI 0.141, Async)      Data & External Services
┌────────────────────────────┐      ┌────────────────────────────┐      ┌──────────────────────────┐
│ React Router 6 + Zustand   │ ──▶  │ /api/v1 REST (75 modules)  │ ──▶  │ PostgreSQL 16 (System of │
│ Vite 5 + Tailwind CSS 4.3  │      │ WebSockets (/ws, /advanced)│      │ Record) / SQLite (tests) │
│ Monaco Code Editor         │      │ RS256 JWT + Argon2id Auth  │      │ Redis 7 (Cache/Limiter)  │
│ Vitest + ESLint + tsc      │      │ Celery Workers + structlog │      │ MongoDB 7 + Qdrant       │
└────────────────────────────┘      └────────────────────────────┘      │ Judge0 + LLM Providers   │
                                                                        └──────────────────────────┘
```

---

## Quick Start

### Option 1: Native Dev Mode (Databases in Docker, App Locally)

```powershell
# 1. Start backing data services (configure .env first)
copy .env.example .env
docker compose up -d postgres redis mongodb qdrant

# 2. Backend API (Terminal 1)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. Frontend UI (Terminal 2)
cd frontend
npm ci
npm run dev
```

- **Frontend UI**: `http://localhost:5173`
- **Backend Swagger UI (non-production)**: `http://localhost:8000/docs`

### Option 2: Full Docker Compose Stack

```bash
cp .env.example .env
# Edit .env with strong SECRET_KEY, CREDENTIAL_SIGNING_KEY, database credentials, and RSA keys
docker compose up -d --build
docker compose ps
```

### Option 3: Windows Interactive Script (`run.bat`)

Run `run.bat` from the repository root for interactive setup, Docker Compose startup, or local test execution.

---

## Verification & Automated Tests

All verification runs offline against in-memory SQLite (`aiosqlite`) and resilient fallbacks (`SafeRedis`, `MockQdrantClient`). External services (`PostgreSQL`, `Redis`, `MongoDB`, `Qdrant`, `Judge0`, LLM providers) and GitHub Actions cloud runners must still be exercised in full integration environments.

### Backend (`backend/`)
```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .          # Lint (0 errors)
.\.venv\Scripts\python.exe -m mypy .                # Typecheck (300 source files, 0 errors)
.\.venv\Scripts\python.exe -m pytest tests/ -q      # 165 unit/integration/WS tests
.\.venv\Scripts\python.exe -m pytest -m benchmark -v # 2 benchmark tests
```

### Frontend (`frontend/`)
```powershell
cd frontend
npm run lint        # ESLint (0 errors, 28 hook/fast-refresh warnings)
npm run typecheck   # tsc -p tsconfig.app.json --noEmit with strict: true (0 errors)
npm test            # Vitest unit/component suite (6 files, 14 tests)
npm run build       # Typecheck + Vite production bundle
```

---

## Local Development Seed Credentials

> [!CAUTION]
> Seed scripts in `backend/scripts/` refuse to execute when `ENVIRONMENT=production`. Never create or retain default accounts in staging or production deployments.

| Role | Email | Password | Intended Scope |
|:---|:---|:---|:---|
| Candidate / Student | `test@example.com` | `password` | Local development seed account |
| Recruiter | `recruiter@example.com` | `password` | Local recruiter flow testing |
| Admin | `admin@example.com` | `password` | Local admin/workforce testing |

*(Dev-only frontend offline mock fallback in `frontend/src/lib/mockAuth.ts` is inactive unless `import.meta.env.DEV && VITE_ENABLE_MOCK_AUTH === 'true'`.)*

---

## API Overview (Verified Paths)

Full endpoint catalog: [docs/API.md](docs/API.md)

| Method | Endpoint | Summary |
|:---|:---|:---|
| `GET` | `/health` | Service liveness and DB connectivity check |
| `POST` | `/api/v1/auth/login` | Authenticate with Argon2id and issue RS256 JWT + refresh cookie |
| `POST` | `/api/v1/auth/logout` | Revoke access JWT JTI and clear refresh cookie |
| `GET` | `/api/v1/resume-builder/metadata` | List 30 configured company profiles and 15 role taxonomies |
| `POST` | `/api/v1/resume-builder/calculate-ats` | Compute 6-dimension ATS rubric score |
| `POST` | `/api/v1/resume-builder/optimize-mnc` | Rewrite bullets with action-verb/XYZ heuristics |
| `GET` | `/api/v1/readiness` | Compute Career Readiness Index |
| `POST` | `/api/v1/assessments/start` | Initialize adaptive assessment session |
| `GET` | `/api/v1/career-twin` | Retrieve Career Digital Twin snapshot |
| `POST` | `/api/v1/career-simulator/what-if` | Run non-mutating counterfactual query |
| `GET` | `/api/v1/mnc-interview/memory` | Retrieve cross-session interview memory |
| `POST` | `/api/v1/credentials/issue` | Issue HMAC-SHA256 signed credential |
| `POST` | `/api/v1/recruiter-intel/discover` | Multi-tenant candidate search and ranking |
| `GET` | `/api/v1/org/matrix` | Organizational capability heatmap (`Org Admin` / `Recruiter`) |
| `GET` | `/api/v1/privacy-security/export` | Export candidate profile/skills/credentials/simulations JSON |
| `POST` | `/api/v1/privacy-security/account/delete` | Self-service account/data deletion (retaining `SecurityAuditLog`) |

---

## Repository Structure

```text
VIREONIQ/
├── .github/workflows/ci.yml   # GitHub Actions CI (backend lint/mypy/pytest/pip-audit + frontend lint/tsc/vitest/build)
├── backend/
│   ├── alembic/               # Alembic migrations
│   ├── api/                   # FastAPI v1 router & 75 endpoint modules
│   ├── core/                  # Settings validation, RS256/Argon2id security, Redis/Qdrant/Mongo & LLM clients
│   ├── crud/                  # Async SQLAlchemy CRUD helpers
│   ├── db/                    # SQLAlchemy models & session factory
│   ├── schemas/               # Pydantic v2 schemas
│   ├── services/              # 123 service modules (twin, readiness, ATS, assessments, interviews, etc.)
│   ├── tests/                 # 49 test_*.py modules (165 standard + 2 benchmark tests)
│   └── workers/               # Celery app & async tasks
├── frontend/
│   └── src/
│       ├── api/               # Axios API modules & hooks
│       ├── components/        # Reusable UI primitives & navigation
│       ├── layouts/           # Route guards & page layouts
│       ├── lib/               # Axios setup, error parser, dev-gated mockAuth, offline engine
│       ├── pages/             # React Router pages (73 modules)
│       ├── store/             # Zustand state stores
│       └── __tests__/         # Vitest + RTL test suites (6 files, 14 tests)
├── docs/                      # Architecture, Security, Testing, API, Known Limitations, Improvement Report
├── docker-compose.yml         # Local/container service orchestration
├── CONTRIBUTING.md            # Contribution & CI check guidelines
├── INCIDENT_RESPONSE.md       # Security incident runbook (draft)
└── LICENSE                    # Controlling software license
```

---

## Security & Governance Notes

- Production startup rejects weak `SECRET_KEY`, `CREDENTIAL_SIGNING_KEY`, default DB passwords, SQLite fallback URLs, wildcard CORS with credentials, and missing RSA keys (`backend/core/config.py`).
- Privacy endpoints provide user export and self-service deletion primitives, but the codebase has **not** undergone formal external GDPR/CCPA or SOC2 legal/security certification.
- Known pending owner decisions (license conflict resolution, `python-jose`/`passlib` replacement, semver-major npm upgrades, and legacy service consolidation) are tracked in [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

---

## License

> [!WARNING]
> **License Notice (Pending Decision)**: The repository [LICENSE](LICENSE) file currently specifies a **Proprietary & Strict Source-Available Copyright License**, which previously conflicted with an MIT badge in this README. Until the repository owner selects a final license, [LICENSE](LICENSE) remains the controlling terms file.

---

**Author**: [Priya Ranjan](https://github.com/Priya-Ranjan-0201)
