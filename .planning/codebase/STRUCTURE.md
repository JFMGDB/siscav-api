# Codebase Structure

**Analysis Date:** 2026-04-04

## Directory Layout

```
siscav-api/
├── apps/
│   └── api/
│       ├── docs/                 # API-specific documentation
│       └── src/
│           ├── main.py           # FastAPI app, middleware, /api/v1 mount
│           ├── seed_demo.py      # Demo data seeding script
│           ├── alembic/          # Alembic env + versions (migrations)
│           │   └── versions/
│           └── api/
│               └── v1/
│                   ├── api.py    # Aggregates v1 routers
│                   ├── deps.py   # FastAPI DI: db, user, controllers
│                   ├── controllers/
│                   ├── core/     # config, security, limiter
│                   ├── db/       # Base, session, engine
│                   ├── endpoints/
│                   ├── models/
│                   ├── repositories/
│                   ├── schemas/
│                   └── utils/
├── tests/                        # pytest: unit + integration
│   ├── conftest.py
│   ├── integration/
│   ├── unit/
│   ├── scripts/                  # ad-hoc test helpers
│   └── test_main.py
├── db/
│   └── sql/                      # SQL setup scripts (e.g. Supabase)
├── docs/                         # Project documentation, Postman, guides
├── scripts/                      # Repo-level utility scripts
├── .planning/                    # Planning artifacts (this folder)
├── alembic.ini                   # Points script_location to apps/api/src/alembic
├── pyproject.toml                # Project metadata, pytest/ruff/coverage config
├── requirements.txt
├── requirements-dev.txt
├── ruff.toml
├── register.html                 # Standalone HTML (not part of FastAPI package)
├── uploads/                      # Runtime image storage (default upload target)
└── README.md
```

## Directory Purposes

**`apps/api/src/`:**
- Purpose: All production API Python code and Alembic migration scripts for this service.
- Contains: `main.py`, package `api.v1.*`, `alembic/`.
- Key files: `apps/api/src/main.py`, `apps/api/src/api/v1/api.py`, `apps/api/src/api/v1/deps.py`.

**`apps/api/src/api/v1/endpoints/`:**
- Purpose: HTTP route handlers only; keep them thin.
- Contains: `*_router` modules per feature area.
- Key files: `whitelist.py`, `auth.py`, `access_logs.py`, `gate_control.py`, `devices.py`, `health.py`.

**`apps/api/src/api/v1/controllers/`:**
- Purpose: Use-case logic and orchestration between repositories, schemas, and file/storage rules.
- Key files: `plate_controller.py`, `auth_controller.py`, `access_log_controller.py`, `gate_controller.py`, `device_controller.py`.

**`apps/api/src/api/v1/repositories/`:**
- Purpose: Database access; SQLAlchemy queries only.
- Key files: `authorized_plate_repository.py`, `user_repository.py`, `access_log_repository.py`.

**`apps/api/src/api/v1/models/`:**
- Purpose: SQLAlchemy ORM entities.
- Key files: `user.py`, `authorized_plate.py`, `access_log.py`.

**`apps/api/src/api/v1/schemas/`:**
- Purpose: Pydantic models shared by endpoints and controllers.
- Key files: `user.py`, `authorized_plate.py`, `access_log.py`, `token.py`, `device.py`.

**`apps/api/src/api/v1/core/`:**
- Purpose: App-wide configuration, crypto/JWT, rate limiting.
- Key files: `config.py`, `security.py`, `limiter.py`.

**`apps/api/src/api/v1/db/`:**
- Purpose: Declarative base (`base.py`), engine and `get_db()` (`session.py`).

**`tests/`:**
- Purpose: Pytest suites; mirrors API domains in `unit/` and `integration/`.
- Key files: `tests/conftest.py`, `tests/integration/test_endpoints_*.py`, `tests/unit/test_controllers_*.py`.

**`db/sql/`:**
- Purpose: Database provisioning or reference SQL outside Alembic (e.g. Supabase setup).

**`docs/`:**
- Purpose: Human-facing documentation, API guides, Postman collections when stored here.

**`scripts/`:**
- Purpose: Small maintenance or debug utilities at repo root (not the FastAPI package).

## Key File Locations

**Entry Points:**
- `apps/api/src/main.py`: ASGI `app` factory and global middleware/handlers.
- `alembic.ini` (repo root): Alembic configuration; `script_location = apps/api/src/alembic`.

**Configuration:**
- `apps/api/src/api/v1/core/config.py`: Runtime settings resolution (`DATABASE_URL`, JWT, uploads path, etc.).
- `pyproject.toml`: pytest markers, coverage `source = ["apps"]`, optional dev deps.
- `ruff.toml`: Ruff lint/format configuration.
- `env.local.example`, `env.supabase.example`: Documented env var templates (do not commit real secrets).

**Core Logic:**
- Business flows live under `apps/api/src/api/v1/controllers/` with persistence in `repositories/`.

**Testing:**
- `tests/conftest.py`: Shared fixtures (if present) for app client and DB.
- Domain tests: `tests/unit/test_*`, `tests/integration/test_*`.

## Naming Conventions

**Files:**
- Endpoints: `snake_case.py` matching resource (`whitelist.py`, `access_logs.py`).
- Controllers: `{domain}_controller.py`.
- Repositories: `{entity}_repository.py`.
- Models: `snake_case.py` for entity (`authorized_plate.py`).
- Schemas: mirror entity names where applicable (`authorized_plate.py` in `schemas/`).

**Directories:**
- Package layout uses `apps.api.src...` as import root (run pytest/tests with project root on `PYTHONPATH` or install mode per project docs).

**Python symbols:**
- Routers: `router = APIRouter()`.
- FastAPI path operations: `read_*`, `create_*`, `update_*`, `delete_*` style in endpoints (see `whitelist.py`).

## Where to Add New Code

**New REST feature under v1:**
- Routes: add `apps/api/src/api/v1/endpoints/{feature}.py` with an `APIRouter`.
- Register: `include_router` in `apps/api/src/api/v1/api.py` with `prefix` and `tags`.
- Logic: `apps/api/src/api/v1/controllers/{feature}_controller.py`.
- Persistence: `apps/api/src/api/v1/repositories/{entity}_repository.py` (static methods pattern).
- ORM: `apps/api/src/api/v1/models/{entity}.py` + Alembic revision under `apps/api/src/alembic/versions/`.
- I/O models: `apps/api/src/api/v1/schemas/{entity}.py`.

**New authenticated dependency:**
- Add factory functions beside existing ones in `apps/api/src/api/v1/deps.py`; reuse `get_db` and `get_current_user` patterns.

**Tests:**
- Unit: `tests/unit/test_controllers_{feature}.py` and/or `tests/unit/test_repositories_{feature}.py`.
- Integration: `tests/integration/test_endpoints_{feature}.py`; use `@pytest.mark.integration` when marking slow HTTP tests (see `pyproject.toml` markers).

**Utilities:**
- Shared pure functions: `apps/api/src/api/v1/utils/` with `__init__.py` exports as needed.

## Special Directories

**`apps/api/src/alembic/versions/`:**
- Purpose: Revision scripts generated/edited for schema changes.
- Generated: Yes (via Alembic CLI).
- Committed: Yes.

**`uploads/`:**
- Purpose: Filesystem storage for access log images; path comes from settings (`upload_dir`).
- Generated: Yes at runtime.
- Committed: Typically gitignored for local dev binaries (verify `.gitignore`).

**`venv/`:**
- Purpose: Local virtual environment.
- Generated: Yes.
- Committed: No.

---

*Structure analysis: 2026-04-04*
