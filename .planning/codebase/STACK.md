# Technology Stack

**Analysis Date:** 2026-04-04

## Languages

**Primary:**
- **Python** — Entire backend API under `apps/api/src/`. CI runs on Python 3.13 (`.github/workflows/ci.yml`); `apps/api/src/main.py` documents Python 3.10+ as the intended minimum.

**Secondary:**
- **SQL** — Schema and Supabase-oriented scripts in `db/sql/supabase/` (e.g. `db/sql/supabase/00_complete_setup.sql`).
- **HTML** — Standalone `register.html` at repo root (not part of the FastAPI app bundle).

## Runtime

**Environment:**
- CPython (see CI `python-version: '3.13'` in `.github/workflows/ci.yml`).

**Package Manager:**
- **pip** — Primary install path via `requirements.txt` and `requirements-dev.txt`.
- **`pyproject.toml`** — Declares project metadata and optional `[project.optional-dependencies] dev` (pytest, pytest-cov, ruff, httpx); align installs with `pip install -e ".[dev]"` when using editable installs.
- **Lockfile:** No `requirements.lock` or `poetry.lock` in repo; dependency versions are unpinned in `requirements.txt` except implicit resolution at install time.

## Frameworks

**Core:**
- **FastAPI** — HTTP API and OpenAPI docs; app factory and middleware in `apps/api/src/main.py`.
- **Uvicorn** (`uvicorn[standard]` in `pyproject.toml` / `requirements.txt`) — ASGI server for production/dev.
- **SQLAlchemy** — ORM; engine and session factory in `apps/api/src/api/v1/db/session.py`.
- **Alembic** — Migrations; configured by `alembic.ini` with `script_location = apps/api/src/alembic` (revision files under `apps/api/src/alembic/versions/`).
- **Pydantic** — Request/response models in `apps/api/src/api/v1/schemas/`; `Settings` in `apps/api/src/api/v1/core/config.py` uses `BaseModel` (not `pydantic-settings`).

**Testing:**
- **pytest** / **pytest-cov** — Configured in `pyproject.toml` under `[tool.pytest.ini_options]` and `[tool.coverage.*]`; tests live under `tests/`.
- **httpx** — Used as FastAPI test client in integration tests (declared in dev dependencies).

**Lint / format:**
- **Ruff** — CI runs `ruff check` and `ruff format --check` (`.github/workflows/ci.yml`).

**API cross-cutting:**
- **slowapi** — Rate limiting; limiter in `apps/api/src/api/v1/core/limiter.py`, wired in `apps/api/src/main.py`.
- **python-multipart** — Listed in `requirements.txt` for form/file uploads used by FastAPI.

## Key Dependencies

**Critical:**
- **psycopg2-binary** — PostgreSQL driver; SQLAlchemy URLs use `postgresql+psycopg2://` when not using SQLite (see `apps/api/src/api/v1/core/config.py`).
- **python-jose[cryptography]** — JWT encode/decode in `apps/api/src/api/v1/core/security.py` and `apps/api/src/api/v1/endpoints/auth.py`.
- **passlib[argon2]** — Password hashing in `apps/api/src/api/v1/core/security.py`.
- **email-validator** — Supports Pydantic `EmailStr` validation (declared in `pyproject.toml`).

**Infrastructure:**
- **SQLite** — Fallback URL `sqlite:///./siscav_dev.db` when neither `DATABASE_URL` nor full `POSTGRES_*` set (`config.py`); Alembic default `sqlalchemy.url` in `alembic.ini` matches SQLite for local migration workflows.

## Configuration

**Environment:**
- **No pydantic-settings** — `Settings` reads `os.getenv` directly in `apps/api/src/api/v1/core/config.py`.
- **Templates (do not commit secrets):** `env.local.example`, `env.supabase.example` document variable names; runtime also honors `DATABASE_URL`, `POSTGRES_*`, `SECRET_KEY`, `ALGORITHM`, token TTLs, `UPLOAD_DIR`, `MAX_FILE_SIZE_MB`, and `ENVIRONMENT` / `DEBUG` (see `main.py` for error detail behavior).

**Build:**
- **`alembic.ini`** — Alembic entry config.
- **`pyproject.toml`** — Project and tool configuration (pytest, coverage).

## Platform Requirements

**Development:**
- Python 3.10+ (documented) / 3.13 in CI; pip; optional PostgreSQL or Supabase-compatible `DATABASE_URL`; Ruff and pytest from `requirements-dev.txt`.

**Production:**
- ASGI host (typically Uvicorn behind a reverse proxy); PostgreSQL or compatible cloud Postgres (e.g. Supabase) with `sslmode=require` when applicable; writable directory for `UPLOAD_DIR` if file uploads are used.

## Other repository artifacts

- **`package-lock.json`** — Present at repo root without a matching `package.json` in the workspace layout surveyed; treat as ancillary unless a Node toolchain is added.

---

*Stack analysis: 2026-04-04*
