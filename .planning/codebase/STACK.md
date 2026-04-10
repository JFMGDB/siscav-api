# Technology Stack

**Analysis Date:** 2026-04-10

## Languages

**Primary:**
- Python 3.13 — Application code under `apps/`, tests under `tests/`, Alembic migrations under `apps/api/src/alembic/`. CI (``.github/workflows/ci.yml``) and `Dockerfile.dev` target 3.13; `pyrightconfig.json` sets `"pythonVersion": "3.13"`.

**Secondary:**
- SQL — Hand-written schema scripts for Supabase-oriented setup in `db/sql/supabase/` (`01_enable_extensions.sql`, `02_types.sql`, `03_tables.sql`, `04_indexes.sql`).

## Runtime

**Environment:**
- CPython 3.13 (see `Dockerfile.dev`, `.github/workflows/ci.yml`, `pyrightconfig.json`).

**Package Manager:**
- pip — Dependencies listed in `requirements.txt` (runtime) and `requirements-dev.txt` (dev/CI includes `-r requirements.txt`).
- Lockfile: Not detected (no `uv.lock`, `poetry.lock`, or pinned versions in `requirements.txt`).

## Frameworks

**Core:**
- FastAPI — HTTP API and OpenAPI docs; entrypoint `apps/api/src/main.py` (`FastAPI` app, CORS, SlowAPI middleware).
- Uvicorn [standard] — ASGI server; `docker-compose.yml` runs `uvicorn apps.api.src.main:app --host 0.0.0.0 --port 8000 --reload`.
- SQLAlchemy — ORM; engine and `SessionLocal` in `apps/api/src/api/v1/db/session.py`; models under `apps/api/src/api/v1/models/`.
- Pydantic — Request/response and settings-shaped models; schemas in `apps/api/src/api/v1/schemas/`. Note: `Settings` in `apps/api/src/api/v1/core/config.py` uses `pydantic.BaseModel` plus `os.getenv`; the project avoids `pydantic-settings` to keep dependencies minimal (documented in that file).
- Alembic — Migrations; config `alembic.ini` (`script_location = apps/api/src/alembic`), env logic `apps/api/src/alembic/env.py`.

**Testing:**
- pytest — Config in `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`).
- pytest-cov — Coverage; CI runs `pytest -v --cov=apps --cov-report=term-missing` (see `.github/workflows/ci.yml`). Coverage source: `apps` with omissions in `pyproject.toml` `[tool.coverage.run]`.

**Build/Dev:**
- Ruff — Lint and format; config `ruff.toml` (target `py313`, line length 100, broad rule sets).
- Docker — `Dockerfile.dev` (multi-stage base `python:3.13-slim`), `docker-compose.yml` (API + optional local Postgres).

## Key Dependencies

**Critical:**
- `fastapi` — Web framework (`apps/api/src/main.py`, routers under `apps/api/src/api/v1/endpoints/`).
- `uvicorn[standard]` — ASGI server for local and container runs.
- `sqlalchemy` — Database access layer.
- `alembic` — Schema migrations (`apps/api/src/alembic/`).
- `psycopg2-binary` — PostgreSQL driver for SQLAlchemy URLs using `postgresql+psycopg2` (`apps/api/src/api/v1/core/config.py`).
- `pydantic` — Validation and `Settings`-style model in `config.py`.
- `passlib` — Password hashing; `apps/api/src/api/v1/core/security.py` uses `CryptContext(schemes=["argon2"], ...)`. `requirements.txt` lists `passlib[argon2]`; `pyproject.toml` lists `passlib[bcrypt]` — prefer the resolved runtime in `requirements.txt` and `security.py` (argon2).
- `python-jose[cryptography]` — JWT create/verify in `security.py` (`jwt.encode` / validation paths via controllers).
- `slowapi` — Rate limiting; `apps/api/src/api/v1/core/limiter.py`, wired in `main.py` (`Limiter`, `SlowAPIMiddleware`, `RateLimitExceeded` handler).
- `email-validator` — Supports Pydantic `EmailStr` (schemas such as `apps/api/src/api/v1/schemas/user.py`).
- `python-multipart` — Form/file uploads for FastAPI (`requirements.txt`); used with access log uploads (`UploadFile` in `apps/api/src/api/v1/endpoints/access_logs.py`).

**Infrastructure:**
- Not applicable as separate runtime services in Python deps (Postgres runs as Docker image `postgres:16-alpine` in `docker-compose.yml`, not a pip package).

## Configuration

**Environment:**
- Loaded via `os.getenv` and `apps/api/src/api/v1/core/config.py` (`Settings`, `get_settings()` cached with `lru_cache`). Database URL resolution: `DATABASE_URL` → or composed `POSTGRES_*` → else SQLite fallback `sqlite:///./siscav_dev.db`.
- Example env templates (variable names only; do not commit real secrets): `env.local.example`, `env.supabase.example`.
- `.env` files may exist locally; not read for this analysis.

**Build:**
- `alembic.ini` — Default `sqlalchemy.url` for Alembic; overridden at runtime from `DATABASE_URL` or `get_settings().database_url` in `apps/api/src/alembic/env.py`.
- `ruff.toml` — Lint/format.
- `pyrightconfig.json` — Editor/type-check paths (`apps`, `venv`).
- `pyproject.toml` — Project metadata, pytest/coverage options, dependency list (may diverge slightly from `requirements.txt`; installs typically use requirements files per README/CI).

## Platform Requirements

**Development:**
- Python 3.13+ (per README and CI).
- Optional: Docker + Docker Compose for API and local Postgres (`docker-compose.yml`, `Dockerfile.dev`).
- For OpenAPI/HTTP testing: Postman assets `SISCAV_API.postman_collection.json`, `SISCAV_API.postman_environment.json` (client tooling, not runtime deps).

**Production:**
- Not fully specified in-repo; `config.py` supports PostgreSQL (including Supabase-style `DATABASE_URL` with `sslmode=require` as documented in comments). HTTPS for clients/IoT is described in `README.md` as an expectation, not a coded integration.

## Standalone / non-packaged scripts

**ALPR prototype (not part of declared pip dependencies):**
- `apps/api/src/api/v1/ml/recognize-plate.py` imports `cv2` (OpenCV), `easyocr`, `numpy`, and Windows-specific `winsound`. These libraries are not listed in `requirements.txt` or `pyproject.toml` dependencies; treat as experimental/local tooling unless added to project dependencies.

---

*Stack analysis: 2026-04-10*
