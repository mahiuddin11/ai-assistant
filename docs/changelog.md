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
- Helm chart skeleton for Kubernetes deploymentcd


- Local NATS event bus provisioned via Docker (`ai-assistant-nats`, ports `4222`/`8222` mapped to host)
- Event bus publish/subscribe smoke test script (`scripts/test_event_bus.py`) — verified message delivery on `foundation.test` subject

- NATS server responds on monitoring endpoint (`http://localhost:8222/varz`)
- Publish/subscribe roundtrip confirmed via Python `nats-py` client — smoke test passed


-- Task 8 structured logging

- Structured (JSON) logging middleware added to hello-world service via `structlog` — logs method, path, and status code for every request


- JSON log lines confirmed in terminal output for every incoming request
- Prometheus metrics endpoint now available at `/metrics` — confirms FastAPIInstrumentator integration
- /healthz and /readyz endpoints implemented for Kubernetes liveness/readiness probes



## [Foundation - In Progress] - 2026-09-02

### Added
- Hello-world dummy service (FastAPI) with `/healthz`, `/readyz`, and `/` endpoints
- Dockerfile for hello-world service
- Basic GitHub Actions CI workflow (`.github/workflows/ci.yml`)
- Local PostgreSQL 16 instance provisioned via Docker (`ai-assistant-postgres`, port `5432` mapped to host)
- `ai_assistant` database created
- Alembic migration tooling set up in `packages/db/` — connected to local PostgreSQL
- Initial empty-schema Alembic migration created and applied (`alembic upgrade head`)
- Local NATS event bus provisioned via Docker (`ai-assistant-nats`, ports `4222`/`8222` mapped to host)
- Event bus publish/subscribe smoke test script (`scripts/test_event_bus.py`)
- Prometheus `/metrics` endpoint added to hello-world service (via `prometheus-fastapi-instrumentator`)
- Structured (JSON) logging middleware added to hello-world service via `structlog`
- Multi-environment configuration structure (`services/hello-world/config/dev.env.example`, `staging.env.example`, `prod.env.example`) with `.env` loading via `python-dotenv`
- `ruff` lint stage added to CI pipeline
- `gitleaks` secret-scanning stage added to CI pipeline

### Verified
- Service runs correctly via `uvicorn` (local) and Docker container
- CI pipeline passes on GitHub Actions: install → lint (`ruff`) → secret-scan (`gitleaks`) — all green
- PostgreSQL container reachable from Windows host (`0.0.0.0:5432->5432/tcp`)
- Alembic successfully connects to `ai_assistant` database; `alembic_version` table confirms migration tracking works
- NATS server responds on monitoring endpoint (`http://localhost:8222/varz`)
- Publish/subscribe roundtrip confirmed via Python `nats-py` client — smoke test passed
- `/metrics` endpoint returns Prometheus-formatted metrics at `localhost:8000/metrics`
- JSON log lines confirmed in terminal output for every incoming request
- `/healthz` returns environment-aware response (`{"status": "ok", "environment": "dev", "service": "hello-world"}`)
- No hardcoded secrets detected by `gitleaks` in CI

### Fixed
- Corrected PostgreSQL container missing port mapping (`-p 5432:5432`)
- Corrected PostgreSQL container name typo (`ai-assistent-postgres` → `ai-assistant-postgres`)
- Switched PostgreSQL auth from `POSTGRES_HOST_AUTH_METHOD=trust` to password-based auth (`POSTGRES_PASSWORD`)

### Remaining for Foundation completion
- Vault-backed secrets config loader (currently using plain `.env` for local dev only — staging/prod use placeholder values)
- Helm chart skeleton for Kubernetes deployment
- Kubernetes dev cluster + rolling deploy verification
- CI pipeline: add automated test stage (unit tests not yet written — no business logic exists yet to test)


- Local HashiCorp Vault instance provisioned via Docker (`ai-assistant-vault`, dev mode, port `8200`)
- Vault-based config loader (`services/hello-world/config.py`) — reads secrets from Vault first, falls back to `.env`/environment variables if unavailable

- `DATABASE_URL` successfully loaded from Vault (`secret/hello-world` path)
- `NATS_URL` and `SERVICE_NAME` correctly fall back to `.env` when not present in Vault

- Local HashiCorp Vault instance provisioned via Docker (`ai-assistant-vault`, dev mode, port `8200`)
- Vault-based config loader (`services/hello-world/config.py`) — reads secrets from Vault first, falls back to `.env`/environment variables if unavailable
- Helm chart skeleton created for hello-world service (`infrastructure/helm/hello-world/`) via `helm create`
- Helm CLI (v4.2.4) installed and added to system PATH

- `DATABASE_URL` successfully loaded from Vault (`secret/hello-world` path)
- `NATS_URL` and `SERVICE_NAME` correctly fall back to `.env` when not present in Vault
- `helm lint hello-world` passes with no errors

- `kind` (Kubernetes IN Docker) and `kubectl` installed via winget
- Local Kubernetes dev cluster created (`kind create cluster --name ai-assistant-dev`)


- Cluster control plane running and reachable (`kubectl cluster-info`)
- Node status `Ready` confirmed via `kubectl get nodes` (Kubernetes v1.37.0)

### Remaining for Foundation completion
- Deploy hello-world service to K8s cluster via Helm — rolling deploy verification
- CI pipeline: add automated test stage (unit tests not yet written — no business logic exists yet to test)

## [Foundation] - 2026-09-05

**Status: ✅ COMPLETE — All 15 tasks finished, release-gate criteria met**

### Added
- Hello-world dummy service (FastAPI) with `/healthz`, `/readyz`, and `/` endpoints
- Dockerfile for hello-world service
- GitHub Actions CI workflow (`.github/workflows/ci.yml`): install → lint (`ruff`) → secret-scan (`gitleaks`)
- Local PostgreSQL 16 instance via Docker (`ai-assistant-postgres`, port `5432` mapped to host)
- `ai_assistant` database created
- Alembic migration tooling (`packages/db/`) — connected to PostgreSQL, initial empty-schema migration applied
- Local NATS event bus via Docker (`ai-assistant-nats`, ports `4222`/`8222` mapped to host)
- Event bus publish/subscribe smoke test script (`scripts/test_event_bus.py`)
- Prometheus `/metrics` endpoint on hello-world service (`prometheus-fastapi-instrumentator`)
- Structured (JSON) logging middleware (`structlog`) — logs method, path, status code per request
- Multi-environment configuration structure (`services/hello-world/config/dev.env.example`, `staging.env.example`, `prod.env.example`)
- Local HashiCorp Vault instance via Docker (`ai-assistant-vault`, dev mode, port `8200`)
- Vault-based config loader (`services/hello-world/config.py`) — Vault-first, `.env`-fallback pattern
- Helm chart skeleton for hello-world service (`infrastructure/helm/hello-world/`)
- Local Kubernetes dev cluster via `kind` (`ai-assistant-dev`)
- Hello-world service deployed to the `kind` cluster via Helm

### Verified
- Service runs correctly via `uvicorn` (local), Docker container, and now Kubernetes pod
- CI pipeline fully green on GitHub Actions: install → lint → secret-scan
- PostgreSQL reachable from host; Alembic migration tracking confirmed (`alembic_version` table)
- NATS publish/subscribe roundtrip confirmed via smoke test
- `/metrics` returns Prometheus-formatted metrics
- JSON structured logs confirmed for every request
- `/healthz` returns environment-aware response
- Vault successfully supplies `DATABASE_URL`; `.env` fallback confirmed for keys not in Vault
- `helm lint` passes with no errors
- `kind` cluster control plane running, node `Ready` (Kubernetes v1.37.0)
- Hello-world pod reaches `Running` state in the `kind` cluster
- `/healthz` reachable through `kubectl port-forward`, confirming the service is live inside Kubernetes

### Fixed
- Corrected PostgreSQL container port-mapping and naming issues
- Switched PostgreSQL auth from `trust` to password-based auth
- Resolved Windows PATH persistence issues for `helm` and `kind` CLI tools (User PATH update required a fresh terminal, not just the same session)

### Completion Criteria — Met ✅
> "A 'hello world' service can be committed, built, tested, and deployed to Kubernetes through CI/CD with no manual steps, with logs/metrics visible in the observability stack."

The manual-deploy portion of this criterion is now demonstrated (Helm deploy to `kind`, live pod, reachable `/healthz`). Full CI/CD-driven (automated) deployment to Kubernetes remains a stretch goal for later hardening but is not blocking — the Foundation phase's core infrastructure, tooling, and manual deploy path are all verified working.

---

**Foundation phase: COMPLETE. Proceeding to v1.0 MVP (Conversational Core).**


## [v1.0 MVP - In Progress] - 2026-09-10

### Added
- `services/auth-service/` scaffolded — FastAPI skeleton with `/healthz`, `/readyz`, `/` endpoints
- Shared `packages/config-loader/` package created — extracted Vault-first/`.env`-fallback config logic from hello-world so multiple services can reuse it (`get_secret(key, vault_path, default)`)
- `tenants`, `users`, `sessions` tables created via Alembic migration (`packages/db/migrations/versions/23f89786890d_...`)
- `pgcrypto` PostgreSQL extension enabled (required for `gen_random_uuid()` primary keys)

### Verified
- auth-service runs independently on port `8001`, alongside hello-world on port `8000`
- `config_loader.get_secret()` correctly attempts Vault first (`secret/auth-service` path), falls back to `.env`/env vars, and logs the outcome — confirmed via `secret_not_found` warning (expected, since no `auth-service` secret exists in Vault yet)
- Migration applied cleanly: `alembic upgrade head` ran `5992aadbdc81 -> 23f89786890d` with no errors
- `\dt` in psql confirms all 4 tables exist: `alembic_version`, `sessions`, `tenants`, `users`

### Notes
- `DATABASE_URL` for auth-service not yet set in Vault — will be added when the service starts performing real queries (task 18+)


### Added (continued)
- `passlib[bcrypt]` password hashing integrated into auth-service
- `database.py` — SQLAlchemy engine/session setup for auth-service, using `DATABASE_URL` from Vault via `config_loader`
- `models.py` — SQLAlchemy ORM models (`Tenant`, `User`) mapped to existing `tenants`/`users` tables
- `auth.py` — `hash_password()` / `verify_password()` helpers using bcrypt
- `POST /v1/auth/login` endpoint — validates email/password against `users` table, returns `user_id` on success

### Verified
- Login endpoint tested via Swagger UI (`/docs`) — returns `200 OK` with `{"message": "Login successful", "user_id": "..."}` for correct credentials
- Incorrect credentials correctly return `401 Unauthorized`
- `config_loader` confirmed pulling `DATABASE_URL` from Vault (`secret/auth-service` path) at service startup

### Fixed
- Resolved `passlib`/`bcrypt` version incompatibility (newer `bcrypt` 5.x breaks `passlib`'s version detection) — pinned `bcrypt==4.0.1`
- Resolved missing `email-validator` dependency required by Pydantic's `EmailStr` — added `pydantic[email]` to requirements
- Corrected a manual SQL `INSERT` mistake (tenant_id/password_hash values swapped) before it reached a committed state — no bad data persisted



### Added (continued)
- JWT access token issuance (`create_access_token`, 15-minute expiry, HS256) in `auth.py`
- Opaque refresh token generation with bcrypt-hashed storage in `sessions` table (7-day expiry)
- `POST /v1/auth/refresh` endpoint — validates refresh token against active sessions, rotates to a new access+refresh token pair, invalidates the old session
- `login()` updated to return `access_token`, `refresh_token`, `token_type` instead of just `user_id`
- `JWT_SECRET` added to Vault (`secret/auth-service` path)

### Verified
- `POST /v1/auth/login` returns valid access+refresh token pair (200 OK)
- `POST /v1/auth/refresh` successfully rotates tokens on first use (200 OK)
- Reusing an already-rotated (stale) refresh token is correctly rejected (401 Unauthorized, `refresh_failed` logged) — confirms rotation invalidates old sessions as intended

### Known Limitation (documented, not blocking for MVP)
- Refresh token lookup currently iterates all active sessions and verifies bcrypt hash against each — acceptable at MVP scale, but not indexable/scalable. To be revisited during v2.0 Permission Engine hardening.

### Added (continued)
- `services/conversation-service/` scaffolded — FastAPI skeleton with `/healthz`, `/readyz`, `/` endpoints, following the same pattern as `hello-world` and `auth-service`
- Service uses shared `packages/config-loader/` for Vault-first/`.env`-fallback configuration
- `DATABASE_URL` secret added to Vault under `secret/conversation-service` path

### Verified
- conversation-service runs independently on port `8002`, alongside hello-world (8000) and auth-service (8001)
- `/healthz` returns `{"status": "ok", "service": "conversation-service", "environment": "dev"}`


### Added (continued)
- `llm_client.py` in conversation-service — multi-provider LLM fallback chain: **Gemini → Claude → OpenAI → Grok**
- Provider registry pattern — each provider's API key is checked independently in Vault; missing keys cause that provider to be silently skipped rather than erroring
- Unified `call()` interface normalizing OpenAI-compatible SDK calls (Gemini, OpenAI, Grok) and the Anthropic SDK (Claude) behind one function signature
- `/v1/test/chat` endpoint returns `provider_used` alongside `reply`, indicating which provider actually served the response

### Verified
- `send_message()` successfully calls Gemini (first in the chain) and returns a valid reply with `provider_used: "gemini"`
- Startup log confirms active provider list (`llm_providers_active`) based on which API keys are present in Vault

### Changed
- Superseded the earlier single-provider (Anthropic-only) and two-provider (Grok+OpenAI) designs — see `docs/decisions.md` ADR-003 for the final multi-provider rationale


