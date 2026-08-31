# VIREONIQ (PLACEIQ) — Engineering Guidelines & Master Rules

**Project Name**: VIREONIQ (PLACEIQ) — AI Career Intelligence Platform  
**Purpose**: Production-grade, evidence-driven career acceleration and workforce intelligence operating system.

---

## 1. Backend Technology Stack
- **Framework**: FastAPI with Python 3.10+ (Python 3.12 recommended), async and await on every function.
- **ORM & Migrations**: SQLAlchemy 2.0 async ORM, Alembic migrations with SQLite/PostgreSQL support.
- **Background Tasks**: Celery with Redis for distributed background processing.
- **HTTP Client**: `httpx` for async non-blocking HTTP requests.
- **Logging & Tracing**: `structlog` for structured JSON logging.
- **Document Processing**: `PyMuPDF` (fitz) and `python-docx` for binary and structured resume ingestion.

---

## 2. Frontend Technology Stack
- **Framework**: React 18 with TypeScript in strict mode.
- **Build Tool**: Vite 5 with Hot Module Replacement (HMR).
- **Styling**: Tailwind CSS 3.4, Lucide React icons, Radix UI primitives.
- **Animations**: Framer Motion for micro-interactions and transitions.
- **Charts & Data Viz**: Recharts for readiness, radar, and telemetry visualization.
- **State Management**: Zustand for fast global state management.
- **Code Lab**: Monaco Editor for in-browser multi-language coding.
- **Voice & Media**: Web Speech API for voice mock interviews.

---

## 3. Databases & Infrastructure
- **Primary Relational**: PostgreSQL 15+ (with async fallback support).
- **Document Storage**: MongoDB 7.
- **Cache & Rate Limiting**: Redis 7.
- **Vector Search**: Qdrant vector database.

---

## 4. Security & Cryptographic Invariants (Non-Negotiable)
- **Password Hashing**: Use **Argon2id** with unique salts for all passwords; never plain bcrypt, never MD5/SHA.
- **JWT Infrastructure**: Use **RS256** asymmetric JWT with 2048-bit RSA keys; never HS256.
- **Cookie Security**: Refresh tokens in `HttpOnly; Secure; SameSite=Lax` cookies only; never raw `localStorage`.
- **Database Safety**: All queries through SQLAlchemy 2.0 ORM; zero unparameterized SQL strings.
- **File Validation**: Validate file MIME types and headers with byte-level checks.
- **Prompt Sanitization**: Check user inputs for prompt injection before routing to AI providers.
- **Level 3 Autonomy Safety**: Server-side `PermissionError` blocks any high-impact action (job application, recruiter contact) without active user confirmation.

---

## 5. Architectural Separation of Concerns
- `api/api_v1/endpoints/`: Handles HTTP routing, request deserialization, dependency injection, and HTTP responses.
- `services/`: Contains pure business logic, mathematical algorithms, and external AI orchestrations.
- `crud/`: Handles database access layer and query execution.
- `db/models.py`: Defines declarative SQLAlchemy ORM models.
- `schemas/`: Defines strict Pydantic v2 request/response schemas.
- `core/`: Application settings, security utilities, and crypto helpers.

---

## 6. Code Quality Invariants
- Strict type annotations on all function parameters and return types.
- Complete docstrings on all public methods and service classes.
- Zero placeholder functions raising `NotImplementedError` or returning ungrounded dummy data in production paths.
- All automated tests in `backend/tests` must pass 100% (109/109 tests).

---

<div align="center">
  <sub>© 2026 VIREONIQ (PLACEIQ) — Engineering Rules & Architecture Invariants</sub>
</div>
