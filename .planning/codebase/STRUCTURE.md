# Codebase Structure

**Analysis Date:** 2026-04-04

## Directory Layout

```
siscav-api/                          # Repository root (Python project: pyproject.toml)
├── apps/
│   └── api/
│       └── src/
│           ├── main.py              # FastAPI app, middleware, /api/v1 mount
│           ├── alembic/             # Migrations
│           │   ├── env.py
│           │   └── versions/
│           └── api/
│               └── v1/
│                   ├── api.py       # Aggregates APIRouter instances
│                   ├── deps.py      # FastAPI Depends: DB, JWT, controllers
│                   ├── controllers/
│                   ├── endpoints/
│                   ├── repositories/
│                   ├── models/
│                   ├── schemas/
│                   ├── core/      # config, security, limiter
│                   ├── db/        # Base, session, engine
│                   ├── utils/
│                   └── ml/        # Auxiliary script(s), not wired as HTTP layer
├── tests/                           # Pytest root (see pyproject.toml testpaths)
│   ├── conftest.py
│   ├── integration/
│   ├── unit/
│   └── scripts/                     # Manual/debug helpers
├── db/
│   └── sql/                         # Reference SQL (e.g. Supabase setup scripts)
├── docs/                            # API docs, Postman, guides
├── scripts/                         # Repo-level utilities (e.g. token debug)
├── .github/workflows/               # CI (pytest, ruff)
├── pyproject.toml                   # Project metadata, pytest, coverage, deps
├── requirements.txt               # Runtime pins (used by CI per workflow)
├── requirements-dev.txt
├── ruff.toml
└── pyrightconfig.json               # include: apps, extraPaths for editors
```

## Directory Purposes

**`apps/api/src/`:**
- Purpose: All production API code and Alembic configuration for this service.
- Contains: `main.py`, versioned package `api/v1/`, `alembic/`.
- Key files: `apps/api/src/main.py`, `apps/api/src/api/v1/api.py`, `apps/api/src/api/v1/deps.py`

**`apps/api/src/api/v1/endpoints/`:**
- Purpose: HTTP route modules; each file defines one `APIRouter`.
- Key files: `auth.py`, `whitelist.py`, `access_logs.py`, `gate_control.py`, `devices.py`, `health.py`, `__init__.py` (re-exports routers)

**`apps/api/src/api/v1/controllers/`:**
- Purpose: Per-domain orchestration and rules invoked from endpoints.
- Key files: `auth_controller.py`, `plate_controller.py`, `access_log_controller.py`, `gate_controller.py`, `device_controller.py`

**`apps/api/src/api/v1/repositories/`:**
- Purpose: Database access helpers (SQLAlchemy 2.x style queries).
- Key files: `user_repository.py`, `authorized_plate_repository.py`, `access_log_repository.py`

**`apps/api/src/api/v1/models/`:**
- Purpose: SQLAlchemy ORM entity definitions.
- Key files: `user.py`, `authorized_plate.py`, `access_log.py`, `__init__.py`

**`apps/api/src/api/v1/schemas/`:**
- Purpose: Pydantic models for API I/O and token payloads.
- Key files: `user.py`, `token.py`, `authorized_plate.py`, `access_log.py`, `gate_control.py`, `device.py`

**`apps/api/src/api/v1/core/`:**
- Purpose: Configuration, JWT/password helpers, shared limiter instance.
- Key files: `config.py`, `security.py`, `limiter.py`

**`apps/api/src/api/v1/db/`:**
- Purpose: Declarative base, engine, session factory, `get_db` dependency.
- Key files: `base.py`, `session.py`

**`apps/api/src/api/v1/utils/`:**
- Purpose: Pure helpers (e.g. plate normalization).
- Key file: `utils/plate.py`

**`tests/`:**
- Purpose: Automated tests; mirrors domains with `unit/` and `integration/` packages.
- Key files: `tests/conftest.py`, `tests/test_main.py`, `tests/unit/test_*`, `tests/integration/test_endpoints*.py`

**`db/sql/`:**
- Purpose: Database setup or reference scripts outside Alembic (e.g. Supabase-oriented SQL).

**`docs/`:**
- Purpose: Human-facing API documentation and Postman artifacts.

## Key File Locations

**Entry Points:**
- `apps/api/src/main.py`: FastAPI `app`, middleware, router include for `/api/v1`

**Configuration:**
- `apps/api/src/api/v1/core/config.py`: `Settings`, `get_settings()`, database URL resolution
- `pyproject.toml`: dependencies, pytest markers, coverage source `apps`
- `ruff.toml`: lint/format rules

**Core Logic:**
- `apps/api/src/api/v1/api.py`: route registration and URL prefixes
- `apps/api/src/api/v1/deps.py`: authentication and controller DI

**Testing:**
- `tests/conftest.py`: shared fixtures
- `tests/integration/`: HTTP-level tests against the app
- `tests/unit/`: isolated controller, repository, security, config tests

**Migrations:**
- `apps/api/src/alembic/env.py`: migration runtime, model imports for metadata
- `apps/api/src/alembic/versions/*.py`: revision chain

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` throughout `api/v1/` (e.g. `access_log_controller.py`, `user_repository.py`).
- Endpoint modules: domain name + optional qualifier (`gate_control.py`, `access_logs.py`).
- Alembic revisions: dated prefix pattern `YYYYMMDD_NNNN_description.py` (e.g. `20251102_0001_initial_models.py`).

**Directories:**
- Plural resource folders for types of code: `endpoints/`, `controllers/`, `repositories/`, `models/`, `schemas/`.
- Single version folder `v1/` under `api/` for future versioning alongside `v2/` if needed.

**Symbols:**
- FastAPI routers: `router = APIRouter()` in each endpoint module; imported in `api.py` as `*_router`.
- Repository classes: PascalCase class name with static methods; example: `AccessLogRepository.get_all(...)`.
- Controllers: PascalCase with `Controller` suffix; constructed with `Session` where persistence is required.

## Where to Add New Code

**New HTTP feature (new resource or sub-resource):**
- Router: add `apps/api/src/api/v1/endpoints/<feature>.py` with `APIRouter`, register in `apps/api/src/api/v1/api.py` with appropriate `prefix` and `tags`.
- Orchestration: add `apps/api/src/api/v1/controllers/<feature>_controller.py` and a `get_<feature>_controller` factory in `apps/api/src/api/v1/deps.py` if the controller needs `Session`.

**New persistence entity:**
- Model: `apps/api/src/api/v1/models/<entity>.py`; export in `models/__init__.py`.
- Migration: new script under `apps/api/src/alembic/versions/`; ensure `env.py` imports the model module if autogenerate/metadata discovery requires it.
- Repository: `apps/api/src/api/v1/repositories/<entity>_repository.py`.
- API shapes: `apps/api/src/api/v1/schemas/<entity>.py`.

**Shared non-HTTP helpers:**
- Prefer `apps/api/src/api/v1/utils/` for pure functions used by multiple controllers.

**Tests:**
- Unit: `tests/unit/test_<area>_<component>.py` (follow existing patterns like `test_controllers_plate.py`, `test_repositories_user.py`).
- Integration: `tests/integration/test_endpoints_<area>.py` for route-level behavior.

**Utilities at repo root:**
- One-off scripts: `scripts/` at repository root; test/debug helpers: `tests/manual/`.

## Special Directories

**`uploads/` (default `UPLOAD_DIR`):**
- Purpose: Stored access-log images written at runtime by `AccessLogController`.
- Generated: Yes (runtime).
- Committed: Typically gitignored in real deployments; path configurable via environment.

**`apps/api/src/api/v1/ml/`:**
- Purpose: Server-side OCR pipeline (`plate_ocr.py`) used by `plate_recognition.py` endpoint.
- Generated: No.
- Committed: Yes (if present in tree).

**`.planning/`:**
- Purpose: Project planning artifacts (roadmaps, phases); consumed by GSD-style workflows.
- Generated: Mixed.
- Committed: Per team policy.

---

*Structure analysis: 2026-04-04*
