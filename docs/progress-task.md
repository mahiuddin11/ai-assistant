# AI Assistant Foundation — Tasks 4, 5 & 6

## Overview

This document records the implementation and verification of Foundation Phase Tasks 4, 5, and 6 for the `ai_assistant` project.

Project root:

```text
C:\laragon\www\ai_assistant
```

Completed tasks:

- **Task 4:** NATS Event Bus — Local Setup
- **Task 5:** NATS Publish/Subscribe Smoke Test
- **Task 6:** Prometheus Metrics Endpoint for Hello World Service

---

# Task 4 — NATS Event Bus

## Objective

Set up a local NATS server to act as the event bus for communication between services.

NATS provides lightweight, asynchronous communication between different services without tightly coupling them together.

A simplified architecture:

```text
Service A
    |
    | publish: task.created
    v
NATS Event Bus
    |
    +------> AI Agent
    |
    +------> Notification Service
    |
    +------> Logging / Analytics
```

For the AI Assistant platform, this allows different services to communicate through events.

---

## Docker Setup

NATS was started locally using Docker:

```powershell
docker run --name ai-assistant-nats -p 4222:4222 -p 8222:8222 -d nats:latest
```

### Container

Container name:

```text
ai-assistant-nats
```

Image:

```text
nats:latest
```

### Ports

| Port | Purpose |
|---|---|
| `4222` | NATS client connections |
| `8222` | NATS monitoring |

---

## Verification

Running containers were checked using:

```powershell
docker ps
```

The NATS container appeared as:

```text
ai-assistant-nats
```

NATS logs were checked using:

```powershell
docker logs ai-assistant-nats
```

The logs confirmed:

```text
Server is ready
```

This confirms that the NATS server successfully started and is ready to accept client connections.

---

## NATS Architecture

The current local setup is:

```text
Python Services
      |
      | NATS client
      v
+-------------------+
|   NATS Server     |
|                   |
| Port: 4222        |
| Monitor: 8222     |
+-------------------+
```

---

## Why NATS Is Used

NATS will act as the event bus for the AI Assistant platform.

For example, when a task is created:

```text
User
 |
 v
API Service
 |
 | task.created
 v
NATS
 |
 +----> AI Agent
 |
 +----> Notification
 |
 +----> Analytics
```

The publishing service does not need to know which services are listening to the event.

This provides:

- Loose coupling
- Asynchronous communication
- Service scalability
- Event-driven architecture
- Easier integration between Python and other services

---

## Task 4 Status

**COMPLETED**

NATS is running successfully in Docker and is available locally.

---

# Task 5 — NATS Publish/Subscribe Smoke Test

## Objective

Verify that the Python application can successfully communicate with the NATS server.

The smoke test verifies four things:

1. Connect to NATS
2. Subscribe to a subject
3. Publish a message
4. Receive the published message

---

## Python Environment

A Python virtual environment was created under:

```text
scripts\venv
```

The NATS Python client was installed using:

```powershell
pip install nats-py
```

Installed version:

```text
nats-py 2.15.0
```

---

## Test Subject

The smoke test used the following NATS subject:

```text
foundation.test
```

---

## Test Script

The smoke test script was executed from the `scripts` directory.

Command:

```powershell
python test_event_bus.py
```

---

## Successful Test Output

The test produced:

```text
✅ Connected to NATS server
👂 Subscribed to 'foundation.test'
📤 Published: Hello from AI Assistant Foundation phase!
📩 Received on 'foundation.test': Hello from AI Assistant Foundation phase!

✅ SMOKE TEST PASSED — publish/subscribe working correctly
```

---

## What the Test Proves

The successful result confirms that the Python application can:

```text
Python Application
        |
        | Connect
        v
      NATS
        |
        | Subscribe
        v
 foundation.test
        ^
        |
        | Publish
        |
Python Publisher
```

The complete publish/subscribe communication path is working correctly.

---

## Event Flow

The actual test flow was:

```text
1. Python connects to NATS
          |
          v
2. Subscriber subscribes to:
   foundation.test
          |
          v
3. Publisher sends:
   "Hello from AI Assistant Foundation phase!"
          |
          v
4. NATS routes the message
          |
          v
5. Subscriber receives the message
```

---

## Why This Smoke Test Is Important

This is a foundation-level test.

Before building more complex event-driven services, we need to prove that the event bus itself works.

Once this basic communication works, the same mechanism can later be used for events such as:

```text
task.created
task.updated
task.completed
user.created
agent.started
agent.completed
notification.send
```

---

## Task 5 Status

**COMPLETED**

NATS Python publish/subscribe communication was successfully verified.

---

# Task 6 — Prometheus Metrics Endpoint

## Objective

Add Prometheus metrics support to the FastAPI Hello World service.

The purpose is to allow the service to expose operational metrics that can later be collected by Prometheus.

The target endpoint is:

```text
/metrics
```

Local URL:

```text
http://127.0.0.1:8000/metrics
```

---

# Hello World Service

Service location:

```text
services\hello-world
```

Main application:

```text
main.py
```

Current project files:

```text
services/
└── hello-world/
    ├── venv/
    ├── __pycache__/
    ├── Dockerfile
    ├── main.py
    ├── README.md
    └── requirements.txt
```

---

## Existing Endpoints

Before adding Prometheus instrumentation, the service provided:

```text
/
 /healthz
 /readyz
```

The root endpoint returns:

```json
{
  "message": "AI Assistant Platform - Foundation service is running"
}
```

---

# Prometheus Instrumentation

The following package was added:

```text
prometheus-fastapi-instrumentator
```

---

## Dependency Compatibility Issue

Initially, version `8.1.0` was installed.

However, version `8.1.0` required:

```text
Starlette >=1.0.0,<2.0.0
```

while the existing FastAPI version was:

```text
FastAPI 0.115.0
```

which requires:

```text
Starlette >=0.37.2,<0.39.0
```

This created a dependency conflict.

The conflicting version was removed and a compatible version was installed:

```text
prometheus-fastapi-instrumentator 7.1.0
```

The final environment contains:

```text
FastAPI                         0.115.0
Starlette                       0.38.6
prometheus-fastapi-instrumentator 7.1.0
prometheus-client               0.26.0
```

---

## Dependency Verification

The environment was checked using:

```powershell
python -m pip check
```

The final result was:

```text
No broken requirements found.
```

This confirms that the installed packages have compatible dependencies.

---

# FastAPI Configuration

The following import was added to `main.py`:

```python
from prometheus_fastapi_instrumentator import Instrumentator
```

Prometheus instrumentation was added after the FastAPI application was created:

```python
Instrumentator().instrument(app).expose(app)
```

The relevant application structure is:

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Hello World Service")

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {"message": "AI Assistant Platform - Foundation service is running"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}
```

---

# Running the Service

The Hello World service was started locally using:

```powershell
python -m uvicorn main:app --reload
```

The service became available at:

```text
http://127.0.0.1:8000
```

Uvicorn confirmed:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# Endpoint Verification

## Root Endpoint

The root endpoint was tested successfully.

Request:

```text
http://127.0.0.1:8000/
```

Response:

```json
{
  "message": "AI Assistant Platform - Foundation service is running"
}
```

---

# Prometheus Metrics Endpoint

The main Task 6 test was:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/metrics
```

The endpoint returned Prometheus-formatted metrics successfully.

---

## Request Metrics

The response included:

```text
# HELP http_requests_total Total number of requests by method, status and handler.
# TYPE http_requests_total counter
```

Example:

```text
http_requests_total{handler="/metrics",method="GET",status="2xx"} 1.0
http_requests_total{handler="/",method="GET",status="2xx"} 1.0
```

This proves that HTTP requests are being tracked.

---

## Request Duration Metrics

The endpoint also returned:

```text
http_request_duration_seconds
```

and:

```text
http_request_duration_highr_seconds
```

These metrics allow request latency to be monitored.

For example:

```text
http_request_duration_seconds_count
http_request_duration_seconds_sum
http_request_duration_seconds_bucket
```

These can later be used to calculate response-time statistics.

---

## Python Runtime Metrics

The endpoint also exposed Python runtime metrics such as:

```text
python_gc_objects_collected_total
python_gc_objects_uncollectable_total
python_gc_collections_total
python_info
```

These provide information about the Python runtime and garbage collection.

---

## Request and Response Size Metrics

The service also exposed:

```text
http_request_size_bytes
http_response_size_bytes
```

These metrics provide information about request and response payload sizes.

---

# What Task 6 Proves

The Hello World service is successfully exposing Prometheus-compatible metrics.

Current architecture:

```text
                 +----------------------+
                 |  Hello World Service |
                 |       FastAPI        |
                 +----------+-----------+
                            |
                            |
                       /metrics
                            |
                            v
                 +----------------------+
                 |      Prometheus      |
                 |   Future component   |
                 +----------------------+
```

Currently the endpoint can be accessed locally through:

```text
http://127.0.0.1:8000/metrics
```

When the service is later deployed through Docker/Compose, Prometheus can be configured to scrape the service's `/metrics` endpoint.

---

# Current Foundation Status

| Task | Component | Status |
|---|---|---|
| 4 | NATS Event Bus | ✅ Completed |
| 5 | NATS Publish/Subscribe Smoke Test | ✅ Completed |
| 6 | Prometheus Metrics Endpoint | ✅ Completed |

---

# Current Local Infrastructure

At this stage, the local foundation contains:

```text
AI Assistant Platform
│
├── PostgreSQL
│   ├── Container: ai-assistant-postgres
│   └── Port: 5432
│
├── NATS
│   ├── Container: ai-assistant-nats
│   ├── Client Port: 4222
│   └── Monitoring Port: 8222
│
└── Hello World Service
    ├── FastAPI
    ├── Port: 8000
    ├── /
    ├── /healthz
    ├── /readyz
    └── /metrics
```

---

# Verification Summary

## NATS

```text
NATS Server
    ↓
Running successfully
    ↓
Python client connected
    ↓
Publish successful
    ↓
Subscribe successful
    ↓
Message received
```

## Prometheus

```text
FastAPI
    ↓
Prometheus Instrumentator
    ↓
/metrics
    ↓
Prometheus-compatible output
    ↓
Request + latency + runtime metrics available
```

---

# Completed Foundation Milestone

Tasks 4, 5, and 6 establish three important pieces of the AI Assistant foundation:

### 1. Event Bus

NATS provides asynchronous service-to-service communication.

### 2. Event Communication

The Python NATS smoke test confirms that services can publish and consume events.

### 3. Observability

Prometheus instrumentation provides metrics for monitoring the Hello World service.

Together:

```text
                 AI Assistant Foundation
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       NATS            FastAPI        Prometheus
     Event Bus         Service         Metrics
          |               |               |
          |               |               |
          +-------+-------+---------------+
                  |
                  v
          Observable Services
```

---

# Next Task

The next planned foundation task is:

## Task 7 — Structured Logging

The goal of Task 7 is to introduce structured application logging.

Expected improvements include:

- Consistent log format
- Log levels
- Timestamps
- Service identification
- Request information
- Error information
- Easier log processing in production
- Better integration with centralized logging systems

The eventual architecture will move toward:

```text
Application
    |
    +----> Metrics ----> Prometheus
    |
    +----> Logs ------> Logging System
    |
    +----> Events ----> NATS
```

---

# Final Status

```text
Task 4 — NATS Event Bus
        ✅ COMPLETED

Task 5 — NATS Publish/Subscribe Smoke Test
        ✅ COMPLETED

Task 6 — Prometheus Metrics Endpoint
        ✅ COMPLETED

Next:
Task 7 — Structured Logging
        ⏳ PENDING
```


# Task Progress Tracker

এই ফাইলটা `docs/roadmap.md` ও `docs/requirements.md`-এর পরিপূরক — সেখানে ভার্সন/ফেজ-লেভেল সামারি আছে, এখানে দিনে-দিনে সম্পন্ন হওয়া ছোট টাস্কের বিস্তারিত ট্র্যাকিং রাখা হয়।

---

## Foundation Phase — Task Log

| # | Task | Status | Date | Notes |
|---|---|---|---|---|
| 1 | PostgreSQL local setup via Docker | ✅ Done | 2026-08-31 | Fixed port-mapping + naming issues; see `docs/database-setup.md` |
| 2 | Alembic migration tooling setup | ✅ Done | 2026-09-01 | `packages/db/` — connected, `alembic upgrade head` verified |
| 3 | GitHub Actions folder + empty `ci.yml` | ✅ Done | 2026-08-31 | `.github/workflows/ci.yml` created |
| 4 | NATS event bus via Docker | ✅ Done | 2026-09-02 | `ai-assistant-nats`, ports 4222/8222 |
| 5 | Event bus publish/subscribe smoke test | ✅ Done | 2026-09-02 | `scripts/test_event_bus.py` — test passed |
| 6 | Prometheus `/metrics` endpoint | ✅ Done | 2026-09-02 | `prometheus-fastapi-instrumentator` added to hello-world |
| 7 | Structured JSON logging | ✅ Done | 2026-09-02 | `structlog` middleware logging method/path/status per request |
| 8 | Dev/staging/prod config separation | ✅ Done | 2026-09-02 | `config/*.env.example` + `.env` loading via `python-dotenv` |
| 9 | CI lint stage (`ruff`) | ✅ Done | 2026-09-02 | Added to `ci.yml`, verified green on GitHub Actions |
| 10 | CI secret-scanning (`gitleaks`) | ✅ Done | 2026-09-02 | Added to `ci.yml`, verified green, no secrets detected |

**Foundation task batch 1 (Tasks 1–10): ✅ Complete**

---

## Foundation Phase — Remaining Work

| # | Task | Status | Notes |
|---|---|---|---|
| 11 | Vault-backed secrets config loader | ⬜ Not started | Currently using plain `.env` for dev; staging/prod use placeholders |
| 12 | Helm chart skeleton for hello-world | ⬜ Not started | Needed for Kubernetes deployment |
| 13 | Kubernetes dev cluster setup | ⬜ Not started | Likely via `minikube` or `kind` |
| 14 | Rolling deploy verification on K8s | ⬜ Not started | Depends on 12 + 13 |
| 15 | CI: automated test stage | ⬜ Not started | No business logic yet to unit test — revisit once v1.0 begins |

---


## How to Use This File

- Every time a small task (not a full roadmap phase) is completed, add a row to the relevant phase's table above.
- When all tasks for a phase are done and the phase's full release-gate (see `docs/roadmap.md`) passes, mark the phase complete in `docs/changelog.md` with a dated entry, and start a new section here for the next phase (e.g. `## v1.0 MVP — Task Log`).
- This file is a working log, not a specification — the technical "what must be built" always lives in `docs/requirements.md`.


| 11 | Vault local setup via Docker | ✅ Done | `ai-assistant-vault`, dev-mode, port 8200 |
| 12 | Vault-based config loader (with .env fallback) | ✅ Done | `services/hello-world/config.py` — verified Vault-first, env-fallback behavior |
| 13 | Helm chart skeleton for hello-world | ✅ Done | `infrastructure/helm/hello-world/` — `helm lint` passes |
| 14 | Kubernetes dev cluster setup | ⬜ Not started | Likely via `minikube` or `kind` |
| 15 | Rolling deploy verification on K8s | ⬜ Not started | Depends on 14 |


---

## Environment Notes

- **Helm CLI installed via winget** (`winget install Helm.Helm`) — v4.2.4. If `helm` command is "not recognized" in a new terminal despite successful winget install, the fix that worked: manually verify the binary path via `Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter helm.exe`, then ensure it's in the **User PATH** via `[Environment]::SetEnvironmentVariable("Path", ..., "User")`, and open a **completely new** PowerShell window (not a new tab) to pick up the change.


