# Technology Stack

**Analysis Date:** 2026-04-04

## Languages

**Primary:**
- Python 3.10+ — stated minimum in `apps/api/src/main.py` (OpenAPI description); CI and tooling target newer Python (see Runtime).

**Secondary:**
- SQL — schema and Supabase-oriented scripts in `db/sql/supabase/00_complete_setup.sql` and related paths.

## Runtime

**Environment:**
- CPython — GitHub Actions uses 3.13 (`.github/workflows/ci.yml`); `ruff.toml` sets `target-version = "py313"`.

**Package Manager:**
- pip — primary install path documented via `requirements.txt` / `requirements-dev.txt` and CI.
- Lockfile: **Not detected** for Python (no `poetry.lock` / `Pipfile.lock`); versions are pinned in `pyproject.toml` `[project.dependencies]` and mirrored in `requirements.txt`.

## Frameworks

**Core:**
- FastAPI `0.135.1` — HTTP API, OpenAPI, dependency injection (`apps/api/src/main.py`, `apps/api/src/api/v1/api.py`).
- Uvicorn `[standard] 0.42.0` — ASGI server (declared in `pyproject.toml` / `requirements.txt`).
- SQLAlchemy `2.0.49` — ORM and engine/session (`apps/api/src/api/v1/db/session.py`, `apps/api/src/api/v1/db/base.py`).
- Alembic `1.18.4` — migrations; script location `apps/api/src/alembic`, config `alembic.ini`, env `apps/api/src/alembic/env.py`.
- Pydantic `2.12.5` — schemas and a lightweight `Settings` model in `apps/api/src/api/v1/core/config.py` (project avoids `pydantic-settings` to keep runtime deps minimal).

**Testing:**
- pytest `9.0.2` — runner; config in `pyproject.toml` `[tool.pytest.ini_options]`.
- pytest-cov `7.1.0` — coverage; sources `apps` with omissions in `pyproject.toml` `[tool.coverage.run]`.
- httpx `0.28.1` — HTTP client for tests (declared in dev deps).

**Build/Dev:**
- Ruff `0.14.6` — lint and format; config `ruff.toml` (line length 100, broad rule sets, first-party `apps`).

## Key Dependencies

**Critical:**
- `psycopg2-binary==2.9.11` — PostgreSQL driver for SQLAlchemy URLs using `postgresql+psycopg2://` (`apps/api/src/api/v1/core/config.py`).
- `python-jose[cryptography]==3.5.0` — JWT encode/decode (`apps/api/src/api/v1/core/security.py`, `apps/api/src/api/v1/deps.py`).
- `passlib[argon2]==1.7.4` — password hashing Argon2 (`apps/api/src/api/v1/core/security.py`).
- `slowapi==0.1.9` — rate limiting; limiter `apps/api/src/api/v1/core/limiter.py`, wired in `apps/api/src/main.py`.
- `python-multipart==0.0.20` — multipart uploads for access-log images (`apps/api/src/api/v1/endpoints/access_logs.py`).
- `email-validator==2.3.0` — supports Pydantic `EmailStr` on user/auth schemas.

**Infrastructure:**
- Standard library `urllib.request` — outbound HTTP to gate actuator (`apps/api/src/api/v1/controllers/gate_controller.py`); no `requests` in application runtime.

## Configuration

**Environment:**
- Read via `os.getenv` in `apps/api/src/api/v1/core/config.py` (no `.env` file is read by code in-repo; operators use env files or host env).
- Startup guard: `assert_production_secrets_valid()` in `apps/api/src/main.py` imports from `config.py` before app wiring.
- Example templates: `env.local.example`, `env.supabase.example` (variable names and patterns only; do not commit secrets).

**Build:**
- `pyproject.toml` — project metadata and tool config for pytest/coverage.
- `alembic.ini` — default `sqlalchemy.url` (SQLite); overridden by `DATABASE_URL` or `get_settings().database_url` in `apps/api/src/alembic/env.py`.
- `ruff.toml` — lint/format.

## Platform Requirements

**Development:**
- Python compatible with declared dependencies; PostgreSQL optional (SQLite fallback when no DB env vars).
- `PYTHONPATH` / working directory must allow imports `apps.api.src...` (see `apps/api/src/seed_demo.py` for path bootstrap when run as script).

**Production:**
- PostgreSQL (or compatible URL) recommended; `ENVIRONMENT=production` requires non-default `SECRET_KEY` (`apps/api/src/api/v1/core/config.py`).

---

*Stack analysis: 2026-04-04*
