
PostgreSQL requires either `POSTGRES_PASSWORD` or `POSTGRES_HOST_AUTH_METHOD=trust` to be set on first initialization.

### 4. Remove Failed Container

```powershell
docker rm ai-assistent-postgres
```

### 5. Recreate Container with Trust Authentication

```powershell
docker create --name ai-assistent-postgres -e POSTGRES_USER=root -e POSTGRES_HOST_AUTH_METHOD=trust postgres:16
docker start ai-assistent-postgres
```

| Flag | Purpose |
|---|---|
| `--name ai-assistent-postgres` | Container name *(note: contains a typo — see Known Issues)* |
| `-e POSTGRES_USER=root` | Sets the PostgreSQL superuser to `root` |
| `-e POSTGRES_HOST_AUTH_METHOD=trust` | Allows password-less connections — **local development only** |

> ⚠️ `trust` authentication is acceptable for an isolated local dev container but must never be used in staging/production, per the project's non-negotiable security rules (see [`docs/architecture.md`](architecture.md) → Global Architectural Rules).

### 6. Verify Container Is Running

```powershell
docker ps
```

Confirmed `STATUS: Up`.

### 7. Connect via `psql`

```powershell
docker exec -it ai-assistent-postgres psql -U root
```

### 8. Create Project Database

```sql
CREATE DATABASE ai_assistant;
\c ai_assistant
```

### 9. Verify Connection and Version

```sql
SELECT current_database();
SELECT version();
```

**Confirmed:**
- Connected database: `ai_assistant`
- PostgreSQL version: `16.15 (Debian 16.15-1.pgdg13+2)`

### 10. Exit

```sql
\q
```

---

## Current Configuration

| Setting | Value |
|---|---|
| Container name | `ai-assistent-postgres` *(typo — should be `ai-assistant-postgres`)* |
| Image | `postgres:16` |
| Database | `ai_assistant` |
| User | `root` |
| Password | None (`trust` auth) |
| Host port mapping | ❌ Not configured |
| Accessible from Windows host | ❌ No — container-internal only |

---

## Known Issues & Action Required

Two items must be fixed before this database can be used by Alembic or the FastAPI service (both run on the Windows host, outside the container):

### Issue 1 — No Port Mapping
The container was created without `-p 5432:5432`, so PostgreSQL is only reachable from inside the container (via `docker exec`). Any tool running on the host — Alembic, `psql` from PowerShell, or the FastAPI service — cannot currently connect.

### Issue 2 — Container Name Typo
`ai-assistent-postgres` should be `ai-assistant-postgres` for consistency with the rest of the project.

### Fix

```powershell
docker stop ai-assistent-postgres
docker rm ai-assistent-postgres

docker run --name ai-assistant-postgres `
  -e POSTGRES_USER=root `
  -e POSTGRES_PASSWORD=admin123 `
  -e POSTGRES_DB=ai_assistant `
  -p 5432:5432 `
  -d postgres:16
```

> Switching from `trust` to `POSTGRES_PASSWORD` here is intentional — it matches the credential pattern Alembic/FastAPI will use via a `DATABASE_URL` connection string, and avoids relying on passwordless auth even locally.

Then verify:

```powershell
docker ps
# PORTS column should show: 0.0.0.0:5432->5432/tcp

docker exec -it ai-assistant-postgres psql -U root -d ai_assistant
```

```sql
SELECT version();
\q
```

---

## Setup Status

| Item | Status |
|---|---|
| Docker installed and verified | ✅ |
| PostgreSQL 16 image pulled | ✅ |
| Container created and running | ✅ |
| `ai_assistant` database created | ✅ |
| Connection verified (container-internal) | ✅ |
| Port mapped to host (`5432:5432`) | ❌ Pending |
| Container name corrected | ❌ Pending |
| Password-based auth (replacing `trust`) | ❌ Pending |
| Connection verified from host machine | ❌ Pending |

**Overall Foundation task status:** Not yet complete — pending the fixes above before Alembic setup (next task) can proceed.

---

## Final Configuration

| Setting | Value |
|---|---|
| Container name | `ai-assistant-postgres` |
| Image | `postgres:16` |
| Database | `ai_assistant` |
| User | `root` |
| Password | `admin123` *(local dev only — will move to Vault-backed secrets per Foundation requirements)* |
| Host port mapping | `0.0.0.0:5432->5432/tcp` ✅ |
| Accessible from Windows host | ✅ Yes |

**Fix applied:**
```powershell
docker rm ai-assistent-postgres
docker run --name ai-assistant-postgres -e POSTGRES_USER=root -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=ai_assistant -p 5432:5432 -d postgres:16
```

## Setup Status (Final)

| Item | Status |
|---|---|
| Docker installed and verified | ✅ |
| PostgreSQL 16 image pulled | ✅ |
| Container created and running | ✅ |
| `ai_assistant` database created | ✅ |
| Port mapped to host (`5432:5432`) | ✅ |
| Container name corrected | ✅ |
| Password-based auth configured | ✅ |
| Connection verified from host machine | ✅ |

**PostgreSQL local setup: COMPLETE ✅**