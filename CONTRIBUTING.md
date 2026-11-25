# Contributing to VIREONIQ

Thank you for contributing to VIREONIQ. Please follow the workflow and verification standards below before opening a pull request.

## Branch & Commit Workflow

1. Never commit directly to `main`. Create a descriptive feature or hardening branch (for example, `fix/auth-token-check` or `feat/career-twin-ui`).
2. Keep pull requests focused on one logical scope and use conventional commit messages (`fix:`, `feat:`, `chore:`, `docs:`, `test:`, `refactor:`, `ci:`).
3. Never commit secrets, `.env` files, private PEM keys, `celerybeat-schedule*` runtime artifacts, or local database files.
4. Preserve the repository `LICENSE` unless a maintainer explicitly approves a license change.

## Local Verification Checks

Run all checks locally before opening a pull request; the same gates run in `.github/workflows/ci.yml`:

### Backend (`backend/`)
```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy .
.\.venv\Scripts\python.exe -m pytest tests/ -q
.\.venv\Scripts\python.exe -m pytest -m benchmark -v
.\.venv\Scripts\python.exe -m pip_audit --no-deps --disable-pip -r requirements.txt --ignore-vuln PYSEC-2026-4298
```

### Frontend (`frontend/`)
```powershell
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

## Documentation Standards

- Every architectural, API route, or test claim in `README.md` and `docs/` must match code in the repository and observed test runs.
- Keep `docs/KNOWN_LIMITATIONS.md` updated whenever external service integrations, dependency exceptions, or deferred refactors change.
