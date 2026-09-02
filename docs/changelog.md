markdown
# Changelog

All notable changes to this project's documentation and codebase are recorded here. This project has not yet reached its first code release; entries to date are documentation-level. Once development begins (starting with the Foundation phase), each merged roadmap phase will receive its own dated entry.

The format is based on [Keep a Changelog](https://keepachangelog.com/), adapted for this project's phase-based release model. Versions correspond to the roadmap versions defined in [`roadmap.md`](roadmap.md) (Foundation, v1.0, v1.1, ... Commercial GA, Enterprise Edition) rather than semantic versioning, since each roadmap version is itself a release unit.

---

## [Unreleased]

### Documentation
- Authored the complete system roadmap (Foundation → Commercial GA → Enterprise Edition), derived from the `AI-System-Architecture.md` (V1) and `AI-System-Architecture-V2-Extension.md` (V2) source architecture documents.
- Authored the Google Jules development playbook, containing phase-scoped execution prompts, a shared Repo Context Block, and a release-gate-driven workflow.
- Reorganized all documentation into a structured `README.md` + `docs/` layout:
  - `docs/project-definition.md` — vision, scope, audience, design philosophy, success criteria
  - `docs/architecture.md` — architectural principles, module inventory, data architecture, tech stack
  - `docs/roadmap.md` — phase summaries, timeline, dependency/parallelization matrix, release-gate policy
  - `docs/requirements.md` — full per-version technical specification (canonical source of truth)
  - `docs/development-plan.md` — Jules execution playbook and phase prompts
  - `docs/decisions.md` — Architecture Decision Records
  - `docs/changelog.md` — this file
- Removed duplicated testing/security checklist and dependency-matrix content across source documents, consolidating each into a single canonical location.

### Added
- Nothing shipped yet — no roadmap phase has been implemented or merged.

---

## How Future Entries Will Be Added

Each time a roadmap phase (see `roadmap.md`) is merged and passes its release gate, an entry will be added here following this format:
[Foundation] - YYYY-MM-DD
Added
CI/CD pipeline (build → lint → test → security-scan → deploy)
Kubernetes dev cluster + Helm chart skeleton
Event Bus client library with publish/subscribe smoke test
Observability baseline (OpenTelemetry, Prometheus, Grafana, Loki)
Secrets management baseline (Vault-backed config loader)
Security
Secret-scanning CI gate enabled
Least-privilege Vault access policy configured

Subsequent phases will follow the same pattern, e.g. `## [v1.0 MVP] - YYYY-MM-DD`, `## [v1.1 Voice Pipeline] - YYYY-MM-DD`, and so on through `## [Enterprise Edition] - YYYY-MM-DD`, each listing what was **Added**, **Changed**, **Fixed**, **Security**-relevant, or **Deprecated**, consistent with the completion criteria defined for that phase in `requirements.md`.

Regression verification results (confirming prior phases' completion criteria still hold) will be noted under a `### Verified` heading when a phase's merge required re-validating earlier functionality — most notably expected at the `v3.1 AI-OS Core` milestone, which requires a full V1 backward-compatibility regression pass.

## [Foundation - In Progress] - 2026-08-31
### Added
- Hello-world dummy service (FastAPI) with `/healthz` and `/readyz` endpoints
- Dockerfile for hello-world service — verified working locally via `docker build` + `docker run`
- Basic GitHub Actions CI workflow (`.github/workflows/ci.yml`) — installs dependencies on every push/PR to `main`

### Verified
- Service runs correctly via `uvicorn` (local) and Docker container
- CI pipeline passes on GitHub Actions (install-check job green)

### Remaining for Foundation completion
- Postgres + migration tooling (Alembic)
- Event bus (NATS/Kafka) client library + smoke test
- Observability stack (OpenTelemetry, Prometheus, Grafana, Loki)
- Vault-backed secrets config loader
- CI pipeline: add lint, test, and security-scan (gitleaks) stages
- Helm chart skeleton for Kubernetes deployment


## [Foundation - In Progress] - 2026-08-31

### Added
- Hello-world dummy service (FastAPI) with `/healthz` and `/readyz` endpoints
- Dockerfile for hello-world service — verified working locally via `docker build` + `docker run`
- Basic GitHub Actions CI workflow (`.github/workflows/ci.yml`) — installs dependencies on every push/PR to `main`
- Local PostgreSQL 16 instance provisioned via Docker (`ai-assistant-postgres` container, port `5432` mapped to host)
- `ai_assistant` database created
- Alembic migration tooling set up in `packages/db/` — connected to local PostgreSQL via `sqlalchemy.url`
- Initial empty-schema Alembic migration created and applied (`alembic upgrade head`)

### Verified
- Service runs correctly via `uvicorn` (local) and Docker container
- CI pipeline passes on GitHub Actions (install-check job green)
- PostgreSQL container reachable from Windows host (`0.0.0.0:5432->5432/tcp`)
- `SELECT version();` confirms PostgreSQL 16.15 running and connectable
- Alembic successfully connects to `ai_assistant` database
- `alembic_version` table created in Postgres after `alembic upgrade head`, confirming migration tracking is functional

### Fixed
- Corrected PostgreSQL container missing port mapping (`-p 5432:5432`), which initially blocked host-machine connections
- Corrected PostgreSQL container name typo (`ai-assistent-postgres` → `ai-assistant-postgres`)
- Switched PostgreSQL auth from `POSTGRES_HOST_AUTH_METHOD=trust` to password-based auth (`POSTGRES_PASSWORD`) for consistency with how Alembic/FastAPI will connect

### Remaining for Foundation completion
- Event bus (NATS/Kafka) client library + smoke test
- Observability stack (OpenTelemetry, Prometheus, Grafana, Loki)
- Vault-backed secrets config loader (currently using plain `POSTGRES_PASSWORD` for local dev only)
- CI pipeline: add lint, test, and security-scan (gitleaks) stages
- Helm chart skeleton for Kubernetes deployment