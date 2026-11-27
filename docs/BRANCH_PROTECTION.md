# VIREONIQ: GitHub Branch Protection & CI/CD Governance Runbook

This document defines the production branch protection policy, required CI/CD status checks, and access governance for the `main` branch of `Priya-Ranjan-0201/VIREONIQ`.

---

## 1. Governance Objectives

1. **Zero Direct Commits**: All modifications to `main` must flow through verified pull requests created from dedicated phase or feature branches.
2. **Automated Verification Gate**: Code cannot enter `main` unless every automated CI check (lint, typecheck, migrations, test suites, SAST security scans, license audits, production builds) passes completely green.
3. **Linear, Auditable History**: Rebase or squash merging ensures a clean git log without non-fast-forward merge noise.
4. **No Administrative Overrides**: Protection rules apply equally to administrators to prevent accidental pushes or bypasses.

---

## 2. Recommended Branch Protection Rules for `main`

Navigate to **GitHub Repository -> Settings -> Branches -> Add branch protection rule** (or edit rule for `main`).

| Setting | Value | Rationale |
| :--- | :--- | :--- |
| **Branch name pattern** | `main` | Targets canonical production branch. |
| **Require a pull request before merging** | **Checked** | Prevents direct commits or force pushes to `main`. |
| - *Require approvals* | `1` | Ensures human review and sign-off before merge. |
| - *Dismiss stale pull request approvals when new commits are pushed* | **Checked** | Prevents approving outdated code. Any new push invalidates earlier approval. |
| - *Require review from Code Owners* | *Optional (enable when CODEOWNERS is defined)* | Routes reviews to designated domain owners. |
| **Require status checks to pass before merging** | **Checked** | Gates merges on successful CI workflow completion. |
| - *Require branches to be up to date before merging* | **Checked** | Prevents merge skew; branches must be tested against current `main` HEAD. |
| - *Status checks that are required* | `Backend Lint, Typecheck, Migrations, Tests, Audit & Licenses`<br>`Frontend Lint, Typecheck, Build & Audit` | Exact job names from `.github/workflows/ci.yml`. Merges are blocked if any check fails. |
| **Require conversation resolution before merging** | **Checked** | Ensures all reviewer comments and audit queries are addressed. |
| **Require signed commits** | **Checked** (Recommended) | Enforces cryptographic GPG/SSH commit signature verification. |
| **Require linear history** | **Checked** | Requires Squash or Rebase merge; prohibits merge commits on `main`. |
| **Do not allow bypassing the above settings** | **Checked** | Enforces all checks even for repository administrators and owners. |
| **Restrict who can push to matching branches** | Only approved maintainers / No direct pushers | Ensures only GitHub Actions / merge queue can advance `main`. |

---

## 3. GitHub CLI Configuration Command

If configuring via GitHub CLI (`gh`), execute the following command with repository administrative credentials:

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/Priya-Ranjan-0201/VIREONIQ/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["Backend Lint, Typecheck, Migrations, Tests, Audit & Licenses","Frontend Lint, Typecheck, Build & Audit"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  -f restrictions=null \
  -F required_linear_history=true \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F required_conversation_resolution=true
```

---

## 4. Security Scanning & Gate Inventory

The repository CI pipeline enforces the following automated security layers prior to every merge:

1. **Secret Hygiene Scanner** (`.github/workflows/ci.yml`):
   - Regex scan across all tracked repository files detecting leaked AWS keys, private SSH/RSA keys, OpenAI tokens (`sk-proj-*`), and GitHub personal access tokens (`ghp_*`).
2. **Static Application Security Testing (SAST)**:
   - **Bandit** (`bandit -r core/ api/ services/ crud/ schemas/ -ll`):
     - Scans AST for high- and medium-severity vulnerabilities (SQL injection, unsafe deserialization, hardcoded passwords, weak cryptography).
3. **Dependency Vulnerability Audits**:
   - Backend: `pip-audit` reporting known CVEs across Python package dependencies.
   - Frontend: `npm audit --omit=dev --audit-level=high` scanning production JavaScript packages.
4. **License Compliance Scanning**:
   - Enforces zero non-permissive copyleft (`GPL`, `AGPL`) licenses in runtime dependencies for backend and frontend.
5. **Database Migration Round-Trip**:
   - Executes `alembic upgrade head -> alembic downgrade base -> alembic upgrade head` on a clean PostgreSQL instance in CI.
