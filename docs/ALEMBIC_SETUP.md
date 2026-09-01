# Alembic Setup — AI Assistant

## Overview

This document records the Alembic database migration setup for the AI Assistant project.

Project path:

```text
C:\laragon\www\ai_assistant\packages\db
```

Database stack:

* Python 3.14
* SQLAlchemy 2.0.52
* Alembic 1.19.1
* Psycopg 3.3.5
* PostgreSQL 16
* Docker
* python-dotenv

---

# 1. Python Virtual Environment

The database package uses a dedicated Python virtual environment.

Location:

```text
packages/db/venv
```

Activate the environment from PowerShell:

```powershell
cd C:\laragon\www\ai_assistant\packages\db

.\venv\Scripts\Activate.ps1
```

Expected prompt:

```text
(venv) PS C:\laragon\www\ai_assistant\packages\db>
```

---

# 2. Install Database Dependencies

The following packages were installed:

```powershell
pip install sqlalchemy alembic "psycopg[binary]" python-dotenv
```

Installed versions:

| Package        | Version |
| -------------- | ------: |
| SQLAlchemy     |  2.0.52 |
| Alembic        |  1.19.1 |
| Psycopg        |   3.3.5 |
| Psycopg Binary |   3.3.5 |
| python-dotenv  |   1.2.3 |

Verification commands:

```powershell
pip show sqlalchemy
pip show alembic
pip show psycopg
```

---

# 3. PostgreSQL Docker Configuration

PostgreSQL is running inside Docker.

Current configuration:

| Setting           | Value                   |
| ----------------- | ----------------------- |
| Container         | `ai-assistant-postgres` |
| Image             | `postgres:16`           |
| Database          | `ai_assistant`          |
| User              | `root`                  |
| Password          | `admin123`              |
| Host              | `localhost`             |
| Port              | `5432`                  |
| Host Port Mapping | `5432:5432`             |

The PostgreSQL container is configured for local development.

> **Security note:** The current password is intended for local development only. Production credentials must be managed through secure secrets management and must not be committed to Git.

---

# 4. PostgreSQL Connection

The database is accessible from the Windows host.

Expected Docker port mapping:

```text
0.0.0.0:5432->5432/tcp
```

The database connection is:

```text
localhost:5432
```

Database:

```text
ai_assistant
```

User:

```text
root
```

---

# 5. Alembic Initialization

Alembic was initialized from:

```text
packages/db
```

Command:

```powershell
alembic init migrations
```

Generated structure:

```text
packages/db/
│
├── alembic.ini
├── migrations/
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
└── venv/
```

---

# 6. Alembic Configuration

The generated `alembic.ini` contains:

```ini
[alembic]
script_location = %(here)s/migrations
prepend_sys_path = .
path_separator = os
```

The default database URL remains:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

The actual database URL is **not hard-coded** in `alembic.ini`.

Instead, the URL is loaded from `.env` through `migrations/env.py`.

This keeps database credentials outside the Alembic configuration file.

---

# 7. Environment Variables

A `.env` file was created here:

```text
packages/db/.env
```

Current configuration:

```env
DATABASE_URL=postgresql+psycopg://root:admin123@localhost:5432/ai_assistant
```

### Important

The `.env` file contains credentials and must not be committed to Git.

Add the following to `.gitignore`:

```gitignore
.env
```

If the repository uses a global `.gitignore`, make sure this file is also covered.

---

# 8. Loading `.env` in Alembic

`migrations/env.py` was configured to load the environment variables.

Required imports:

```python
import os

from dotenv import load_dotenv
```

The environment is loaded using:

```python
load_dotenv()
```

The database URL is retrieved using:

```python
database_url = os.getenv("DATABASE_URL")
```

A validation check is used:

```python
if not database_url:
    raise RuntimeError("DATABASE_URL is not set in .env")
```

The URL is then passed to Alembic:

```python
config.set_main_option("sqlalchemy.url", database_url)
```

This allows Alembic to use the PostgreSQL connection from `.env`.

---

# 9. Environment Variable Verification

The `.env` configuration was tested using:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DATABASE_URL loaded:', bool(os.getenv('DATABASE_URL')))"
```

Result:

```text
DATABASE_URL loaded: True
```

Therefore:

```text
.env loading: SUCCESS
```

---

# 10. Alembic PostgreSQL Connection Verification

The following command was executed:

```powershell
alembic current
```

Result:

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

This confirms:

```text
Alembic
   ↓
SQLAlchemy
   ↓
Psycopg
   ↓
PostgreSQL
```

is working successfully.

There is currently no migration revision, so no revision ID is displayed.

This is expected because no migration has been created yet.

---

# 11. Current Status

| Component                     | Status       |
| ----------------------------- | ------------ |
| Python virtual environment    | ✅ Complete   |
| SQLAlchemy                    | ✅ Installed  |
| Alembic                       | ✅ Installed  |
| Psycopg                       | ✅ Installed  |
| python-dotenv                 | ✅ Installed  |
| PostgreSQL 16                 | ✅ Running    |
| Docker PostgreSQL             | ✅ Configured |
| Port `5432`                   | ✅ Mapped     |
| Database `ai_assistant`       | ✅ Available  |
| `.env`                        | ✅ Created    |
| `DATABASE_URL`                | ✅ Loaded     |
| Alembic initialization        | ✅ Complete   |
| Alembic PostgreSQL connection | ✅ Verified   |
| SQLAlchemy `Base`             | ⏳ Pending    |
| Models                        | ⏳ Pending    |
| `target_metadata`             | ⏳ Pending    |
| First migration               | ⏳ Pending    |
| Migration execution           | ⏳ Pending    |

---

# 12. Next Step

The next task is to connect SQLAlchemy models with Alembic.

Currently Alembic uses:

```python
target_metadata = None
```

This must eventually become something similar to:

```python
target_metadata = Base.metadata
```

The exact import depends on the project's database architecture.

Before changing `target_metadata`, inspect the Python files inside:

```text
packages/db
```

Command:

```powershell
Get-ChildItem -Recurse -File -Filter *.py
```

Look for files such as:

```text
database.py
base.py
models.py
__init__.py
```

After the SQLAlchemy `Base` and models are confirmed, configure:

```text
SQLAlchemy Base
       ↓
Base.metadata
       ↓
Alembic target_metadata
       ↓
alembic revision --autogenerate
       ↓
migrations/versions/
       ↓
alembic upgrade head
       ↓
PostgreSQL
```

---

# 13. Important Commands

### Activate virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Check Alembic

```powershell
alembic --version
```

### Check SQLAlchemy

```powershell
pip show SQLAlchemy
```

### Check PostgreSQL container

```powershell
docker ps
```

### Check current Alembic revision

```powershell
alembic current
```

### Generate migration

Do **not** run until `target_metadata` and models are configured:

```powershell
alembic revision --autogenerate -m "initial migration"
```

### Apply migrations

```powershell
alembic upgrade head
```

### Show migration history

```powershell
alembic history
```

---

# 14. Development Security Rules

The following rules should be maintained:

1. Never commit `.env`.
2. Never hard-code production database passwords.
3. Do not use `POSTGRES_HOST_AUTH_METHOD=trust` in staging or production.
4. Use password-based authentication for development and production.
5. Production secrets should be managed through a secure secrets manager.
6. Database credentials should not appear in source code, migration files, logs, or documentation committed to Git.

---

# 15. Current Milestone

**Alembic Foundation Setup: COMPLETE ✅**


The migration system is now initialized and can successfully communicate with the PostgreSQL database.

The next milestone is:

**SQLAlchemy Base + Models + Alembic `target_metadata` configuration.**
