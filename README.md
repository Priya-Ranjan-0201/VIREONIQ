<div align="center">

# 🚀 VIREONIQ

### AI-Powered Career & Workforce Intelligence Platform

[![License](https://img.shields.io/badge/License-See_LICENSE_File-red.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Stage-Release_Candidate_1.0.0-green.svg?style=for-the-badge)](docs/LAUNCH_READINESS_REPORT.md)
[![CI](https://img.shields.io/github/actions/workflow/status/Priya-Ranjan-0201/VIREONIQ/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/Priya-Ranjan-0201/VIREONIQ/actions)
[![Developed by](https://img.shields.io/badge/Developed%20By-Priya%20Ranjan-8A2BE2.svg?style=for-the-badge&logo=github)](https://github.com/Priya-Ranjan-0201)

<p>
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

**Evidence-focused career preparation · ATS resume studio · AI interview simulation · Workforce analytics**

</div>

---

## 📋 Table of Contents

- [What is VIREONIQ?](#-what-is-vireoniq)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Quick Start](#-quick-start)
- [Authentication & Local Setup](#-authentication--local-setup)
- [All Platform Modules](#-all-platform-modules)
- [API Reference](#-api-reference)
- [Repository Structure](#-repository-structure)
- [Testing & Verification](#-testing--verification)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Environment Variables](#-environment-variables)
- [Security & Governance](#-security--governance)
- [Documentation Index](#-documentation-index)
- [Tech Stack](#-tech-stack)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 What is VIREONIQ?

**VIREONIQ** is a full-stack AI career intelligence platform that helps job seekers, students, recruiters, and organizations make evidence-backed career decisions. It combines deterministic scoring algorithms with multi-provider LLM integration (Gemini, Claude, OpenAI, DeepSeek, NVIDIA NIM, Ollama) to deliver:

- **Resume optimization** with ATS compatibility scoring across 30+ MNC company profiles
- **AI-powered interview simulation** (voice, coding, behavioral, P2P mock)
- **Career trajectory modeling** with counterfactual what-if scenarios
- **Cryptographic talent credentials** for verifiable skill proof
- **Workforce analytics** for recruiters and organizations

The platform runs locally with SQLite fallback for zero-config dev, or scales to PostgreSQL + Redis + MongoDB + Qdrant for production.

### 🚦 Launch Scope & Honest Feature Tiers

In accordance with our [Launch Readiness Report](docs/LAUNCH_READINESS_REPORT.md) and [Feature Inventory](docs/FEATURE_INVENTORY.md), platform capabilities are grouped into three verified tiers:

| Tier | Status | User Availability | Key Modules Included |
| :--- | :---: | :--- | :--- |
| **Tier 1: Public Beta** | 🟢 **Ready** | Open to all public users | Auth & Session Management, Talent Passport, Resume Scoring, Gap Analysis, Adaptive Practice, Verified Asymmetric Credentials, Settings, Public Verification |
| **Tier 2: Invite-Only** | 🟡 **Cohort Gated** | Partner universities & pilot cohorts | MNC Interview Studio, Coding Sandbox (Judge0), Career Twin Simulator, College Admin Dashboard, Faculty Classrooms |
| **Tier 3: Review Gated** | ⚪ **Disabled by Default** | Requires governance review | Recruiter Intelligence Search, Reverse Interview Matching, High School Trajectory, Parent Dashboard |

---

## ✨ Key Features

### 🧠 Career Intelligence Engine
| Feature | Description |
|:--|:--|
| **Career Digital Twin** | Unified profile aggregating skills, projects, assessments with temporal decay |
| **Career GPS** | AI-generated step-by-step career path recommendations |
| **What-If Simulator** | Counterfactual career trajectory modeling (non-mutating queries) |
| **Readiness Index** | Multi-dimensional career readiness scoring with bottleneck ranking |
| **Psychometric DNA** | Personality-career fit analysis and cognitive profiling |

### 📄 Resume & ATS Studio
| Feature | Description |
|:--|:--|
| **ATS Score Checker** | 6-dimension rubric scoring against 30 company profiles, 15 role taxonomies |
| **JD Matcher** | Job description alignment analysis with keyword gap identification |
| **Resume Builder** | Drag-and-drop builder with 6 print-ready React templates |
| **Bullet Rewriter** | Action-verb / XYZ heuristic optimization for resume bullets |
| **Portfolio Intelligence** | Developer portfolio analysis and scoring |

### 🎤 Interview Preparation
| Feature | Description |
|:--|:--|
| **MNC Interview Studio** | Company-specific interview simulation (30 MNC profiles) |
| **Voice Interview** | Real-time voice-based interview with AI evaluator |
| **Coding Interview** | Monaco editor + Judge0 sandbox with AST complexity analysis |
| **P2P Mock Interview** | Peer-to-peer WebSocket practice sessions |
| **Cognitive Load Monitor** | Real-time stress and performance tracking during interviews |
| **Cross-Session Memory** | Persistent interview performance tracking across sessions |

### 🏆 Career Growth & Learning
| Feature | Description |
|:--|:--|
| **Gamification System** | XP, badges, streaks, and achievement tracking |
| **Leaderboard** | Competitive ranking across users |
| **Syllabus Optimizer** | Personalized learning path generation |
| **Micro Internships** | Short-duration project-based learning opportunities |
| **Skill Decay Tracker** | Time-based skill freshness analysis |
| **Offline Practice** | IndexedDB-backed practice mode without internet |

### 💼 Jobs & Opportunities
| Feature | Description |
|:--|:--|
| **Opportunity Hub** | Curated job listings with smart filtering |
| **Smart Apply Tracker** | Application status tracking with follow-up reminders |
| **Offer Comparator** | Side-by-side job offer analysis |
| **Offer Negotiator** | AI-powered salary negotiation coaching |
| **Employer Truth Score** | Company culture and satisfaction scoring |
| **Salary Predictor** | Market-informed compensation estimation |

### 🔐 Trust & Credentials
| Feature | Description |
|:--|:--|
| **Talent Passport** | Cryptographic HMAC-SHA256 signed skill credentials |
| **Public Verification** | URL-based credential verification for employers |
| **Privacy Controls** | GDPR-style data export and self-service account deletion |

### 👥 Multi-Role Dashboards
| Feature | Description |
|:--|:--|
| **Recruiter Intelligence** | Multi-tenant candidate discovery, ranking, and war room |
| **Workforce Intelligence** | Organizational capability heatmaps and skill gaps |
| **College Admin** | Institutional placement analytics |
| **Faculty Dashboard** | Student progress tracking for educators |
| **Parent Dashboard** | Student career progress visibility |

### 🌐 Specialized Modules
| Feature | Description |
|:--|:--|
| **Language Bridge** | Multilingual career content translation |
| **Vernacular Library** | Regional language learning resources |
| **Career Rebirth** | Career change guidance for industry transitions |
| **High School Trajectory** | Early career planning for high school students |
| **Community Hub** | Peer community for career discussions |
| **Lab Mode** | Experimental features sandbox |
| **Cohort Mode** | Group-based learning and career preparation |
| **Earn-to-Learn** | Monetize skills while learning |
| **AI Copilot** | General-purpose career AI assistant |
| **Developer Platform** | API access and integrations |

---

## 🏗 System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              VIREONIQ PLATFORM ARCHITECTURE                          │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Frontend (React 18, TS Strict)       Backend (FastAPI 0.141, Async)                │
│  ┌──────────────────────────┐         ┌──────────────────────────────┐               │
│  │ React Router 6 + Zustand │  REST   │ /api/v1 REST (75+ endpoints) │               │
│  │ Vite 5 + TailwindCSS 4.3 │ ◄────► │ WebSockets (/ws, /advanced)  │               │
│  │ Framer Motion animations │  WS     │ RS256 JWT + Argon2id Auth    │               │
│  │ Monaco Code Editor       │         │ Celery Workers + structlog   │               │
│  │ Radix UI + Recharts      │         │ Prometheus /metrics endpoint  │               │
│  │ 73+ page modules         │         │ 123 service modules          │               │
│  │ Code-split lazy loading  │         │ Multi-LLM orchestrator       │               │
│  │ Dark/Light theme         │         │ PII redaction pipeline       │               │
│  │ Vitest + ESLint          │         │ Rate limiting (SlowAPI)      │               │
│  └──────────────────────────┘         └──────────────┬───────────────┘               │
│                                                       │                               │
│                           ┌───────────────────────────┼────────────────┐              │
│                           ▼                           ▼                ▼              │
│               ┌──────────────────┐    ┌──────────────────┐  ┌────────────────┐       │
│               │ PostgreSQL 16    │    │ Redis 7          │  │ MongoDB 7      │       │
│               │ (System of       │    │ (Cache, Rate     │  │ (Interview     │       │
│               │  Record)         │    │  Limiter, Celery │  │  sessions,     │       │
│               │ SQLite (dev)     │    │  Broker/Backend) │  │  analytics)    │       │
│               └──────────────────┘    └──────────────────┘  └────────────────┘       │
│                                                                                      │
│               ┌──────────────────┐    ┌──────────────────┐                           │
│               │ Qdrant           │    │ Judge0           │                           │
│               │ (Vector search   │    │ (Code sandbox    │                           │
│               │  for RAG)        │    │  execution)      │                           │
│               └──────────────────┘    └──────────────────┘                           │
│                                                                                      │
│               ┌──────────────────────────────────────────┐                           │
│               │ LLM Providers (pluggable)                │                           │
│               │ Gemini │ Claude │ OpenAI │ DeepSeek      │                           │
│               │ NVIDIA NIM │ Ollama (local)              │                           │
│               └──────────────────────────────────────────┘                           │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 20+ (LTS)** and **npm 10+**
- **Docker** (optional, for backing data services)

### Option 1: Native Dev Mode (Recommended for Local Development)

```powershell
# 1. Clone the repo
git clone https://github.com/Priya-Ranjan-0201/VIREONIQ.git
cd VIREONIQ

# 2. Set up environment
copy .env.example .env
# Edit .env with your API keys (or leave defaults for mock mode)

# 3. Backend (Terminal 1)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 4. Frontend (Terminal 2)
cd frontend
npm ci
npm run dev
```

### Option 2: Full Docker Compose

```bash
cp .env.example .env
# Edit .env with strong SECRET_KEY, CREDENTIAL_SIGNING_KEY, and DB credentials
docker compose up -d --build
docker compose ps
```

### Option 3: Windows Interactive Script

```powershell
.\run.bat
```

### Access Points

| Service | URL |
|:--|:--|
| **Frontend UI** | http://localhost:5173 |
| **Backend API Docs (Swagger)** | http://localhost:8000/docs |
| **Backend ReDoc** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |
| **Prometheus Metrics** | http://localhost:8000/metrics |

---

## 🔐 Authentication & Local Setup

Authentication in VIREONIQ is powered by **Argon2id password hashing**, **RS256 asymmetric JWT access tokens**, and secure HTTP-only refresh cookies.

- **Production & Staging**: Default accounts are forbidden. Users create accounts via `/api/v1/auth/register` and authenticate via `/api/v1/auth/login`. Strong passwords and unique email addresses are strictly enforced.
- **Local Development Only**: For offline testing and fixture evaluation, synthetic dev accounts and offline mock authentication instructions are documented in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#4-local-development-seed-accounts-non-production-only).

> [!CAUTION]
> No default credentials exist in staging or production deployments. Seed scripts refuse to run when `ENVIRONMENT=production`.

---

## 📱 All Platform Modules

### Navigation Routes (73+ Pages)

<details>
<summary><strong>🏠 Core</strong></summary>

| Route | Page |
|:--|:--|
| `/dashboard` | Main Dashboard |
| `/career-os` | Career Operating System |
| `/career-twin` | Career Digital Twin |
| `/career-simulator` | What-If Career Simulator |
| `/career-gps` | Career GPS Navigator |
| `/career-control-center` | Career Control Center |
| `/outcome-intelligence` | Outcome Analytics |
| `/market-intelligence` | Market Intelligence |
| `/benchmarks` | Benchmark Reports |
</details>

<details>
<summary><strong>📄 Resume & ATS</strong></summary>

| Route | Page |
|:--|:--|
| `/resume` | Resume Score Checker |
| `/ats-score` | ATS Compatibility Scorer |
| `/jd-match` | JD Matcher |
| `/resume-rewriter` | Resume Section Rewriter |
| `/bullet-rewriter` | Bullet Point Optimizer |
| `/resume-builder` | Full Resume Builder |
| `/portfolio` | Portfolio Intelligence |
| `/salary-predictor` | Salary Predictor |
</details>

<details>
<summary><strong>🎤 Interview & Assessment</strong></summary>

| Route | Page |
|:--|:--|
| `/mnc-interview` | MNC Interview Studio |
| `/interview` | General Interview |
| `/coding-interview` | Coding Interview (Monaco + Judge0) |
| `/voice-interview` | Voice Interview |
| `/p2p-mock` | Peer-to-Peer Mock Interview |
| `/assessment` | Adaptive Assessment Room |
| `/cognitive-load` | Cognitive Load Monitor |
| `/company-profiles` | Company Profiles Browser |
</details>

<details>
<summary><strong>📚 Learning & Growth</strong></summary>

| Route | Page |
|:--|:--|
| `/syllabus-optimizer` | Personalized Syllabus |
| `/micro-internships` | Micro Internships |
| `/skill-decay` | Skill Decay Tracker |
| `/prep-calendar` | Preparation Calendar |
| `/rebirth` | Career Rebirth |
| `/language-bridge` | Language Bridge |
| `/highschool` | High School Trajectory |
| `/offline-practice` | Offline Practice Mode |
| `/earn-to-learn` | Earn to Learn |
| `/vernacular-library` | Vernacular Library |
| `/lab-mode` | Lab Mode (Experimental) |
| `/cohort-mode` | Cohort Mode |
</details>

<details>
<summary><strong>💼 Jobs & Network</strong></summary>

| Route | Page |
|:--|:--|
| `/opportunities` | Opportunity Hub |
| `/applications` | Smart Apply Tracker |
| `/offer-comparison` | Offer Comparator |
| `/offer-negotiator` | Offer Negotiator |
| `/routing-intelligence` | Application Intelligence |
| `/mentors` | Mentor Network |
| `/truth` | Truth Database |
| `/employer-truth` | Employer Truth Score |
| `/community` | Community Hub |
</details>

<details>
<summary><strong>🏆 Gamification & Credentials</strong></summary>

| Route | Page |
|:--|:--|
| `/gamification` | Gamification Dashboard |
| `/leaderboard` | Leaderboard |
| `/credential` | My Credentials |
| `/passport` | Talent Passport |
| `/certification` | Production Certification |
| `/psychometric-dna` | Psychometric DNA |
</details>

<details>
<summary><strong>👥 Admin & Organization</strong></summary>

| Route | Page |
|:--|:--|
| `/recruiter` | Recruiter Intelligence |
| `/war-room` | Recruiter War Room |
| `/workforce` | Workforce Intelligence |
| `/college-admin` | College Admin Dashboard |
| `/faculty-dashboard` | Faculty Dashboard |
| `/parent-view` | Parent Dashboard |
| `/parent-connect` | Parent Connect |
</details>

<details>
<summary><strong>⚙️ Account & Settings</strong></summary>

| Route | Page |
|:--|:--|
| `/settings` | User Settings |
| `/billing` | Pricing & Plans |
| `/privacy` | Privacy & Data Export |
| `/copilot` | AI Copilot |
| `/developer-platform` | Developer Platform |
</details>

---

## 📡 API Reference

Full documentation: [docs/API.md](docs/API.md) | Interactive: http://localhost:8000/docs

### Core Endpoints

| Method | Endpoint | Description |
|:--|:--|:--|
| `GET` | `/health` | Service liveness + DB connectivity |
| `GET` | `/metrics` | Prometheus metrics (HTTP latency, LLM costs, queue depth) |
| `POST` | `/api/v1/auth/register` | Register new user (Argon2id password hash) |
| `POST` | `/api/v1/auth/login` | Authenticate → RS256 JWT + refresh cookie |
| `POST` | `/api/v1/auth/logout` | Revoke JWT JTI + clear refresh cookie |
| `POST` | `/api/v1/auth/refresh` | Rotate access token via refresh cookie |

### Resume & ATS

| Method | Endpoint | Description |
|:--|:--|:--|
| `GET` | `/api/v1/resume-builder/metadata` | List 30 company profiles + 15 role taxonomies |
| `POST` | `/api/v1/resume-builder/calculate-ats` | 6-dimension ATS rubric scoring |
| `POST` | `/api/v1/resume-builder/optimize-mnc` | Action-verb/XYZ bullet rewriting |
| `POST` | `/api/v1/resume/upload` | Upload + parse resume (PDF/DOCX) |
| `POST` | `/api/v1/resume/score` | Deterministic resume scoring |

### Career Intelligence

| Method | Endpoint | Description |
|:--|:--|:--|
| `GET` | `/api/v1/career-twin` | Career Digital Twin snapshot |
| `GET` | `/api/v1/readiness` | Career Readiness Index |
| `POST` | `/api/v1/career-simulator/what-if` | Counterfactual trajectory query |
| `GET` | `/api/v1/career-gps` | Career path recommendations |

### Interview & Assessment

| Method | Endpoint | Description |
|:--|:--|:--|
| `POST` | `/api/v1/assessments/start` | Initialize adaptive assessment |
| `GET` | `/api/v1/mnc-interview/memory` | Cross-session interview memory |
| `WS` | `/ws/interview` | Real-time interview WebSocket |
| `WS` | `/ws/advanced` | Advanced WebSocket features |

### Credentials & Privacy

| Method | Endpoint | Description |
|:--|:--|:--|
| `POST` | `/api/v1/credentials/issue` | Issue HMAC-SHA256 signed credential |
| `GET` | `/api/v1/credentials/verify/:id` | Public credential verification |
| `GET` | `/api/v1/privacy-security/export` | Export all user data (JSON) |
| `POST` | `/api/v1/privacy-security/account/delete` | Self-service account deletion |

### Recruiter & Org

| Method | Endpoint | Description |
|:--|:--|:--|
| `POST` | `/api/v1/recruiter-intel/discover` | Multi-tenant candidate search |
| `GET` | `/api/v1/org/matrix` | Organizational capability heatmap |

---

## 📂 Repository Structure

```
VIREONIQ/
├── .github/
│   └── workflows/
│       ├── ci.yml               # Main CI: lint, typecheck, test, build (backend + frontend)
│       ├── containers.yml       # Docker build, Trivy scan, SBOM, GHCR push
│       ├── heavy-eval.yml       # Manual: model evaluation, red-team, determinism
│       └── playwright.yml       # E2E smoke tests with screenshots
│
├── backend/
│   ├── alembic/                 # Database migration scripts
│   ├── api/api_v1/endpoints/    # FastAPI route handlers (75+ endpoint modules)
│   ├── core/
│   │   ├── config.py            # Pydantic settings with production validation
│   │   ├── security.py          # RS256 JWT, Argon2id, RBAC
│   │   ├── observability.py     # Prometheus metrics + X-Request-ID tracing
│   │   ├── logging.py           # Structured logging with request correlation
│   │   ├── pii_redactor.py      # PII detection and redaction pipeline
│   │   └── model_safety.py      # LLM output safety guardrails
│   ├── crud/                    # Async SQLAlchemy CRUD operations
│   ├── db/                      # SQLAlchemy models & session factory
│   ├── eval/                    # ML evaluation framework
│   │   ├── metrics.py           # Scoring metrics (MRR, NDCG, precision)
│   │   ├── model_gate.py        # 12-item Model Gate checklist
│   │   ├── redteam.py           # OWASP LLM red-team probes
│   │   ├── robustness.py        # Input perturbation robustness tests
│   │   └── run_baseline_suite.py # Automated baseline evaluation runner
│   ├── schemas/                 # Pydantic v2 request/response schemas
│   ├── scripts/
│   │   ├── seed_demo_data.py    # Dev user + data seeding
│   │   ├── seed_jobs.py         # Job listing seeding
│   │   └── seed_intelligence.py # Recruiter persona seeding
│   ├── services/                # 123 service modules (business logic)
│   ├── tests/                   # Backend test modules & fixtures
│   ├── workers/                 # Celery async task workers
│   ├── main.py                  # FastAPI application entry point
│   └── requirements.txt         # Pinned Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API modules & React Query hooks
│   │   ├── components/          # Reusable UI (Radix UI, animated components)
│   │   ├── layouts/             # AuthGuard, GuestGuard, DashboardLayout
│   │   ├── lib/
│   │   │   ├── axios.ts         # HTTP client with interceptors + retry
│   │   │   ├── mockAuth.ts      # Dev-only offline mock authentication
│   │   │   └── offlineEngine.ts # IndexedDB offline session support
│   │   ├── pages/               # React Router pages (code-split with React.lazy)
│   │   ├── store/               # Zustand state management
│   │   └── __tests__/           # Vitest + RTL test suites
│   ├── tests/e2e/               # Playwright E2E smoke tests
│   ├── index.html               # Vite entry point
│   ├── tailwind.config.ts       # Tailwind CSS 4.3 configuration
│   └── package.json             # Node dependencies & scripts
│
├── docs/
│   ├── API.md                   # Full API endpoint catalog
│   ├── ARCHITECTURE.md          # System architecture deep-dive
│   ├── BASELINE.md              # Verification metrics baseline
│   ├── DATABASE.md              # Data model documentation
│   ├── DATA_SOURCES.md          # Data provenance registry
│   ├── DECISIONS.md             # Architecture decision log
│   ├── DEVELOPMENT.md           # Developer setup guide
│   ├── IMPROVEMENT_REPORT.md    # Before/after improvement metrics
│   ├── KNOWN_LIMITATIONS.md     # Known issues & pending decisions
│   ├── OPERATIONS.md            # Operational runbooks
│   ├── PRIVACY.md               # Privacy engineering notes
│   ├── RESEARCH.md              # Research evidence brief
│   ├── SECURITY.md              # Security architecture
│   ├── AI_SECURITY.md           # AI/ML-specific security controls
│   ├── AI_GOVERNANCE.md         # AI governance framework
│   ├── TESTING.md               # Testing strategy
│   ├── THREAT_MODEL.md          # Threat model analysis
│   ├── RELEASE.md               # Release process
│   ├── evals/                   # Machine-readable evaluation reports
│   └── models/                  # ML model cards (ATS scorer, RAG, retrieval, simulator)
│
├── monitoring/
│   └── grafana/                 # Grafana dashboard for HTTP/LLM/queue metrics
│
├── tests/load/
│   └── locustfile.py            # Locust load testing definitions
│
├── docker-compose.yml           # Production container orchestration
├── docker-compose.dev.yml       # Dev override (relaxed passwords)
├── Dockerfile                   # Backend container image
├── frontend/Dockerfile          # Frontend container image
├── .pre-commit-config.yaml      # Pre-commit hooks (ruff, format, secrets)
├── .env.example                 # Environment variable template
├── run.bat                      # Windows interactive setup script
├── CONTRIBUTING.md              # Contribution guidelines
├── INCIDENT_RESPONSE.md         # Security incident runbook
└── LICENSE                      # Software license
```

---

## ✅ Testing & Verification

All tests run offline using in-memory SQLite (`aiosqlite`) and mock fallbacks (`SafeRedis`, `MockQdrantClient`).

### Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m ruff check .              # Fast linting and import hygiene
python -m mypy .                    # Strict static type checking
python -m pytest tests/ -q          # Pytest suite (see CI status badge)
python -m pytest -m benchmark -v    # Performance benchmark suite
```

### Frontend

```powershell
cd frontend
npm run lint                        # ESLint checks
npm run typecheck                   # Strict TypeScript check (tsconfig.app.json)
npm test                            # Vitest unit & component suite (see CI status badge)
npm run build                       # Production bundle build
```

### Evaluation Framework

```powershell
cd backend
python eval/run_baseline_suite.py   # Retrieval, Model Gate, Red-Team evaluation
python eval/redteam.py              # OWASP LLM01/02/06/09 probes
```

---

## 🔄 CI/CD Pipeline

GitHub Actions runs on every push and PR:

| Workflow | Trigger | What It Does |
|:--|:--|:--|
| `ci.yml` | Push / PR | Backend (ruff, mypy, pytest, pip-audit) + Frontend (eslint, tsc, vitest, build) |
| `containers.yml` | Push to main | Docker build, Trivy vulnerability scan, SBOM generation, GHCR push |
| `heavy-eval.yml` | Manual / Scheduled | Model evaluation, red-team suite, determinism verification |
| `playwright.yml` | Manual / PR | E2E smoke tests with screenshot capture |

All actions are **SHA-pinned** for supply chain security. CI target: under 15 minutes.

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|:--|:--|:--|
| `SECRET_KEY` | Yes | JWT signing secret (≥32 chars in production) |
| `CREDENTIAL_SIGNING_KEY` | Yes | HMAC credential signing key |
| `ENVIRONMENT` | No | `development` (default) / `production` |
| `DATABASE_URL` | No | PostgreSQL connection string |
| `POSTGRES_PASSWORD` | No | Database password |
| `REDIS_URL` | No | Redis connection string |
| `MONGODB_URL` | No | MongoDB connection string |
| `QDRANT_URL` | No | Qdrant vector DB URL |
| `DEFAULT_LLM_PROVIDER` | No | `gemini` / `claude` / `openai` / `deepseek` / `nvidia_nim` / `ollama` |
| `GEMINI_API_KEY` | No | Google Gemini API key |
| `ANTHROPIC_API_KEY` | No | Anthropic Claude API key |
| `OPENAI_API_KEY` | No | OpenAI API key |
| `JUDGE0_API_URL` | No | Judge0 code execution endpoint |
| `VITE_ENABLE_MOCK_AUTH` | No | Frontend: `true` to enable offline mock auth |

> [!TIP]
> For local development, the app works with zero configuration using SQLite and mock fallbacks. Only add API keys for LLM-powered features.

---

## 🔒 Security & Governance

- **Authentication**: RS256 JWT access tokens + HTTP-only refresh cookies + Argon2id password hashing
- **Authorization**: Role-based access control (`require_roles` decorator) with Admin, Recruiter, User, Org Admin roles
- **Production Validation**: Startup rejects weak secrets, default DB passwords, SQLite URLs, and wildcard CORS
- **Rate Limiting**: SlowAPI per-endpoint rate limiting
- **PII Protection**: Automated PII detection and redaction pipeline
- **LLM Safety**: Output guardrails, prompt injection detection, hallucination mitigation
- **Observability**: Prometheus metrics, structured logging, X-Request-ID correlation, distributed tracing
- **Container Security**: Trivy vulnerability scanning, SBOM generation, build provenance attestation
- **Code Quality**: Ruff linting, mypy strict typing, pre-commit hooks, `detect-private-key` scanning

> [!WARNING]
> This codebase has **not** undergone formal external security audit, GDPR/CCPA certification, or SOC2 assessment. See [docs/SECURITY.md](docs/SECURITY.md) and [docs/AI_SECURITY.md](docs/AI_SECURITY.md).

---

## 📚 Documentation Index

| Document | Description |
|:--|:--|
| [docs/API.md](docs/API.md) | Complete API endpoint catalog |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture deep-dive |
| [docs/BASELINE.md](docs/BASELINE.md) | Current verification metrics |
| [docs/DATABASE.md](docs/DATABASE.md) | Data model and schema reference |
| [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) | Data provenance and licensing |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Architecture decision log |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Developer setup guide |
| [docs/IMPROVEMENT_REPORT.md](docs/IMPROVEMENT_REPORT.md) | Before/after metrics comparison |
| [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) | Known issues and pending decisions |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Operational runbooks |
| [docs/PRIVACY.md](docs/PRIVACY.md) | Privacy engineering notes |
| [docs/RESEARCH.md](docs/RESEARCH.md) | Research evidence brief |
| [docs/SECURITY.md](docs/SECURITY.md) | Security architecture |
| [docs/AI_SECURITY.md](docs/AI_SECURITY.md) | AI/ML security controls |
| [docs/AI_GOVERNANCE.md](docs/AI_GOVERNANCE.md) | AI governance framework |
| [docs/TESTING.md](docs/TESTING.md) | Testing strategy |
| [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) | Threat model |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) | Security incident runbook |

---

## 🛠 Tech Stack

### Backend
| Technology | Version | Purpose |
|:--|:--|:--|
| Python | 3.12 | Runtime |
| FastAPI | 0.141.1 | Async web framework |
| Uvicorn | 0.52.4 | ASGI server |
| SQLAlchemy | 2.0.52 | Async ORM |
| Alembic | 1.19.1 | Database migrations |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Caching, rate limiting, Celery broker |
| MongoDB | 7 | Document store (interviews, analytics) |
| Qdrant | Latest | Vector similarity search (RAG) |
| Celery | 5.6.3 | Distributed task queue |
| spaCy | 3.8.16 | NLP processing |
| sentence-transformers | 6.3.0 | Embedding generation |
| Argon2-cffi | 25.1.0 | Password hashing |
| Prometheus | — | Metrics collection |

### Frontend
| Technology | Version | Purpose |
|:--|:--|:--|
| React | 18.2 | UI framework |
| TypeScript | 5.2 (strict) | Type-safe JavaScript |
| Vite | 5.4 | Build tool & dev server |
| TailwindCSS | 4.3 | Utility-first CSS |
| Framer Motion | 11.0 | Animations |
| React Router | 6.22 | Client-side routing |
| Zustand | 4.5 | State management |
| React Query | 5.18 | Server state management |
| Radix UI | Latest | Accessible UI primitives |
| Recharts | 2.11 | Data visualization |
| Monaco Editor | 4.6 | Code editor |
| Vitest | Latest | Unit testing |
| Playwright | Latest | E2E testing |

### DevOps
| Technology | Purpose |
|:--|:--|
| Docker Compose | Container orchestration |
| GitHub Actions | CI/CD (SHA-pinned actions) |
| Trivy | Container vulnerability scanning |
| Ruff | Python linting & formatting |
| mypy | Python static type checking |
| ESLint | TypeScript/React linting |
| pre-commit | Git hook automation |
| Locust | Load testing |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Key rules:

1. Never commit to `main` — create feature branches
2. All PRs must pass CI checks
3. Use conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`, `ci:`)
4. Never commit secrets, API keys, or real personal data
5. Run `ruff check .` and `npm run lint` before pushing

---

## 📄 License

> [!WARNING]
> The repository [LICENSE](LICENSE) file specifies a **Proprietary & Strict Source-Available Copyright License**. See [LICENSE](LICENSE) for the controlling terms.

---

<div align="center">

**Built with ❤️ by [Priya Ranjan](https://github.com/Priya-Ranjan-0201)**

</div>
