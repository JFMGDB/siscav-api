# Codebase Structure

**Analysis Date:** 2026-04-10

## Directory Layout

```
siscav-api-1/
├── .github/                    # CI workflows and GitHub docs
│   └── workflows/
│       └── ci.yml
├── .planning/                  # Planning artifacts (e.g. codebase docs)
├── apps/
│   └── api/
│       └── src/
│           ├── main.py       # FastAPI app factory and middleware
│           ├── api/
│           │   └── v1/
│           │       ├── api.py            # Aggregates all v1 routers
│           │       ├── deps.py           # DI: DB session, JWT user, controllers
│           │       ├── controllers/      # Business logic
│           │       ├── core/             # config, security, rate limiter
│           │       ├── crud/             # Deprecated CRUD helpers
│           │       ├── db/             # SQLAlchemy Base + session
│           │       ├── endpoints/        # FastAPI routers per domain
│           │       ├── models/         # SQLAlchemy ORM models
│           │       ├── repositories/   # Data access (static methods)
│           │       ├── schemas/        # Pydantic request/response models
│           │       ├── utils/          # Shared helpers (e.g. plate normalization)
│           │       └── ml/             # Standalone script(s), not wired to API
│           └── alembic/              # Migrations (versions/, env.py)
├── db/
│   └── sql/
│       └── supabase/           # Reference SQL for Supabase (extensions, types, tables)
├── docs/                       # Project documentation (Portuguese specs, etc.)
├── tests/                      # Pytest: unit + integration
├── alembic.ini                 # Alembic entry; script_location -> apps/api/src/alembic
├── docker-compose.yml          # Dev: api + optional local Postgres (profile local)
├── Dockerfile.dev              # Dev image; uvicorn command from compose
├── env.local.example           # Example env (do not commit secrets)
├── env.supabase.example
├── pyproject.toml              # Project metadata, pytest/coverage, Ruff tool refs
├── requirements.txt
├── requirements-dev.txt
├── ruff.toml
├── pyrightconfig.json
├── SISCAV_API.postman_collection.json
└── SISCAV_API.postman_environment.json
```

## Directory Purposes

**`apps/api/src/`:**
- Purpose: All importable Python package roots for the API (`apps.api.src...`).
- Contains: `main.py`, `api/v1/**`, `alembic/`.
- Key files: `apps/api/src/main.py`, `apps/api/src/api/v1/api.py`, `apps/api/src/api/v1/deps.py`.

**`apps/api/src/api/v1/endpoints/`:**
- Purpose: Route definitions only; keep handlers small.
- Contains: `auth.py`, `whitelist.py`, `access_logs.py`, `devices.py`, `gate_control.py`, `health.py`, `__init__.py`.
- Key files: `apps/api/src/api/v1/endpoints/whitelist.py` (pattern: `Depends(get_plate_controller)`, `Depends(get_current_user)`).

**`apps/api/src/api/v1/controllers/`:**
- Purpose: Application services / use cases; orchestrate repositories and raise HTTP errors.
- Contains: `*_controller.py` modules; `__init__.py`.

**`apps/api/src/api/v1/repositories/`:**
- Purpose: SQLAlchemy queries and persistence; static methods on classes.
- Contains: `authorized_plate_repository.py`, `user_repository.py`, `access_log_repository.py`, `__init__.py`.

**`apps/api/src/api/v1/models/`:**
- Purpose: ORM table mappings.
- Contains: `user.py`, `authorized_plate.py`, `access_log.py`.

**`apps/api/src/api/v1/schemas/`:**
- Purpose: Pydantic models for API contracts.
- Contains: `user.py`, `authorized_plate.py`, `access_log.py`, `token.py`, `device.py`.

**`apps/api/src/api/v1/core/`:**
- Purpose: App-wide non-route code: settings, crypto/JWT, rate limiter.
- Contains: `config.py`, `security.py`, `limiter.py`.

**`apps/api/src/api/v1/db/`:**
- Purpose: Declarative base and session factory.
- Contains: `base.py`, `session.py`, `__init__.py`.

**`apps/api/src/alembic/`:**
- Purpose: Database migrations.
- Contains: `env.py`, `versions/*.py`, `script.py.mako`.

**`tests/`:**
- Purpose: Automated tests (mirror concerns: deps, controllers, repositories, integration endpoints).
- Contains: `tests/unit/`, `tests/integration/`, top-level `test_*.py` files.

**`db/sql/supabase/`:**
- Purpose: SQL scripts for Supabase-oriented schema (not the only source of truth if Alembic is used for app DB).

## Key File Locations

**Entry Points:**
- `apps/api/src/main.py`: FastAPI `app`, CORS, rate limit middleware, includes `api_router` at `/api/v1`.

**Configuration:**
- `apps/api/src/api/v1/core/config.py`: Runtime settings (`database_url`, JWT, uploads).
- `alembic.ini`: Alembic script path and default SQLite URL (overridden in `env.py` when env is set).
- `docker-compose.yml`: `PYTHONPATH=/app`, uvicorn command, env passthrough.
- `env.local.example` / `env.supabase.example`: Document expected variables (do not commit real secrets).

**Core Logic:**
- `apps/api/src/api/v1/api.py`: Registers all v1 routers and URL prefixes (`/devices`, `/whitelist`, `/access_logs`, `/gate_control`).
- `apps/api/src/api/v1/deps.py`: Authentication and controller providers.

**Testing:**
- `tests/`: Pytest discovery per `pyproject.toml` (`testpaths = ["tests"]`).

## Naming Conventions

**Files:**
- Endpoints: `snake_case.py` matching domain (`auth.py`, `gate_control.py`).
- Controllers: `*_controller.py` in `controllers/`.
- Repositories: `*_repository.py` in `repositories/`.
- Models: `snake_case.py` (entity name, e.g. `authorized_plate.py`).
- Schemas: Often mirror models (`authorized_plate.py`, `access_log.py`).

**Directories:**
- API version folder: `v1/` under `api/` for future versioning.
- Python packages use `__init__.py` where present (`endpoints/`, `controllers/`, etc.).

**Import paths:**
- Use package imports from repo root: `from apps.api.src.api.v1...` (requires `PYTHONPATH` including project root, as in Docker and typical local runs from repo root).

## Where to Add New Code

**New Feature (HTTP + DB):**
- Primary code: Add router in `apps/api/src/api/v1/endpoints/<feature>.py`; register in `apps/api/src/api/v1/api.py`.
- Controller: `apps/api/src/api/v1/controllers/<feature>_controller.py`.
- Repository: `apps/api/src/api/v1/repositories/<entity>_repository.py`.
- ORM model: `apps/api/src/api/v1/models/<entity>.py` (subclass `Base` from `apps/api/src/api/v1/db/base.py`).
- Pydantic schemas: `apps/api/src/api/v1/schemas/<entity>.py`.
- Dependencies: Expose controller and any new deps in `apps/api/src/api/v1/deps.py`.
- Migration: New revision under `apps/api/src/alembic/versions/` after model changes; ensure `env.py` imports new model modules.

**New Component/Module:**
- Implementation: Same layers as above; avoid adding business logic to `endpoints/` beyond wiring.

**Utilities:**
- Shared helpers: `apps/api/src/api/v1/utils/` (e.g. `plate.py` for normalization/validation).

**Tests:**
- Unit tests near concern: `tests/unit/test_<area>.py`; integration: `tests/integration/test_endpoints.py` or new file under `tests/integration/`.

## Special Directories

**`apps/api/src/api/v1/crud/`:**
- Purpose: Legacy CRUD functions; transitional.
- Generated: No.
- Committed: Yes; **do not extend** for new features — use `repositories/` + `controllers/`.

**`apps/api/src/api/v1/ml/`:**
- Purpose: Contains scripts such as `recognize-plate.py`; not integrated as a FastAPI route in the surveyed layout.
- Generated: No.
- Committed: Yes.

**`uploads/` (runtime):**
- Purpose: Default directory for stored access images (`upload_dir` in settings); may appear at cwd when running locally.
- Generated: Yes (at runtime).
- Committed: Typically gitignored if created (verify `.gitignore`).

---

*Structure analysis: 2026-04-10*
