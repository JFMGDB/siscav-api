# Architecture

**Analysis Date:** 2026-04-04

## Pattern Overview

**Overall:** Layered FastAPI backend with versioned HTTP surface (`/api/v1`), dependency injection for DB sessions and controllers, and a thin “router → controller → repository → ORM model” flow. Pydantic schemas define request/response contracts at the HTTP boundary.

**Key Characteristics:**
- **Controllers** hold use-case logic, HTTP-oriented errors (`HTTPException`), and mapping to/from Pydantic models.
- **Repositories** are stateless classes with `@staticmethod` methods; they encapsulate SQLAlchemy queries against domain models.
- **Endpoints** (`endpoints/*.py`) declare routes, OpenAPI metadata, and `Depends()` wiring only; they delegate to controllers.
- **Cross-cutting:** JWT auth and rate limiting are applied via `deps.py`, `core/security.py`, and `core/limiter.py` on the FastAPI app in `apps/api/src/main.py`.

## Layers

**HTTP / routing (API v1):**
- Purpose: Map URLs and HTTP verbs to Python callables; attach tags, query params, and response models.
- Location: `apps/api/src/api/v1/endpoints/`
- Contains: One `APIRouter` per domain (`auth.py`, `whitelist.py`, `access_logs.py`, `gate_control.py`, `devices.py`, `health.py`).
- Depends on: `apps/api/src/api/v1/deps.py`, controllers, Pydantic schemas.
- Used by: Aggregator `apps/api/src/api/v1/api.py`, included from `apps/api/src/main.py` under prefix `/api/v1`.

**Router aggregation:**
- Purpose: Single `api_router` that mounts sub-routers with domain prefixes and tags.
- Location: `apps/api/src/api/v1/api.py`
- Depends on: All endpoint modules under `endpoints/`.

**Application composition:**
- Purpose: Create `FastAPI` app, global middleware (CORS, SlowAPI), global exception handler, mount v1 API.
- Location: `apps/api/src/main.py`
- Depends on: `apps/api/src/api/v1/api.py`, `apps/api/src/api/v1/core/limiter.py`.

**Controllers (application / use cases):**
- Purpose: Business rules, validation orchestration, raising `HTTPException`, returning schema instances (e.g. `AuthorizedPlateRead.model_validate(orm_obj)`).
- Location: `apps/api/src/api/v1/controllers/` (`plate_controller.py`, `auth_controller.py`, `access_log_controller.py`, `gate_controller.py`, `device_controller.py`).
- Depends on: Repositories (static class references), `Session`, schemas, `core` utilities where needed (e.g. auth).
- Used by: Endpoints via `Depends(get_*_controller)` factories in `deps.py`.

**Repositories (data access):**
- Purpose: SQLAlchemy `select`/CRUD-style operations; no FastAPI imports.
- Location: `apps/api/src/api/v1/repositories/` (`authorized_plate_repository.py`, `user_repository.py`, `access_log_repository.py`).
- Depends on: `sqlalchemy.orm.Session`, models in `apps/api/src/api/v1/models/`.
- Used by: Controllers (and `get_current_user` in `deps.py` uses `UserRepository` directly).

**Domain models (ORM):**
- Purpose: SQLAlchemy `DeclarativeBase` subclasses and table mapping; shared UUID handling for Postgres/SQLite via `GUID` in `apps/api/src/api/v1/db/base.py`.
- Location: `apps/api/src/api/v1/models/` (`user.py`, `authorized_plate.py`, `access_log.py`).

**Schemas (DTOs):**
- Purpose: Pydantic v2 models for API input/output and token payloads.
- Location: `apps/api/src/api/v1/schemas/`.

**Infrastructure:**
- **DB session:** `apps/api/src/api/v1/db/session.py` — engine from `get_settings().database_url`, `SessionLocal`, `get_db()` generator for FastAPI.
- **Configuration:** `apps/api/src/api/v1/core/config.py` — `get_settings()` (cached) resolves DB URL from env with documented fallback order (including SQLite dev fallback).
- **Migrations:** Root `alembic.ini` points `script_location` to `apps/api/src/alembic`; revision scripts live under `apps/api/src/alembic/versions/`.

**Utilities:**
- Purpose: Pure helpers (e.g. plate normalization/validation).
- Location: `apps/api/src/api/v1/utils/plate.py`.

## Data Flow

**Authenticated CRUD (example: whitelist):**

1. Client calls `GET/POST/...` under `/api/v1/whitelist/...` (`apps/api/src/api/v1/endpoints/whitelist.py`).
2. FastAPI resolves `Depends(get_current_user)` → JWT validated in `deps.py` → `UserRepository.get_by_id` → `User` ORM instance.
3. `Depends(get_plate_controller)` builds `PlateController(db)` with request-scoped `Session` from `get_db()`.
4. `PlateController` calls `AuthorizedPlateRepository` static methods, maps results to `AuthorizedPlateRead`.

**Auth (login / refresh):**

1. `apps/api/src/api/v1/endpoints/auth.py` uses `get_auth_controller`, `get_db`, and `core/security.py` token helpers (`create_access_token`, `create_refresh_token`).
2. `AuthController` coordinates credentials and persistence via `UserRepository` (pattern mirrors other domains).

**IoT access log ingest (unauthenticated POST):**

1. `POST /api/v1/access_logs/` (`endpoints/access_logs.py`) does **not** require `get_current_user`; accepts multipart image + plate form field.
2. `AccessLogController.create_access_log` validates image, normalizes plate, checks whitelist via repository, persists log, writes file under `Path(settings.upload_dir)` (see `access_log_controller.py`).
3. Serving images: `GET .../access_logs/images/{image_filename}` uses `get_current_user` — authenticated admin-style access.

**Gate / devices (stubs):**

1. `GateController` and `DeviceController` are constructed without DB (`deps.py`); they return simulated responses for demo (`gate_controller.py`, `device_controller.py`).

**State Management:**
- No in-memory application state for domain data; per-request `Session` via `get_db()`. Rate limiter state is attached to `app.state.limiter` in `main.py`.

## Key Abstractions

**FastAPI dependency providers:**
- Purpose: Centralize construction of DB session, current user, and controllers.
- Examples: `apps/api/src/api/v1/deps.py`
- Pattern: `Annotated[..., Depends(...)]` on endpoint parameters; lazy import for `DeviceController` to avoid cycles.

**Settings singleton:**
- Purpose: Typed config (e.g. `database_url`, JWT settings, `upload_dir`).
- Examples: `apps/api/src/api/v1/core/config.py` — use `get_settings()` everywhere instead of reading `os.environ` ad hoc in business code.

**Repository as static API:**
- Purpose: Simple data layer without instantiating repository objects; controllers hold `self.repo = SomeRepository` and call `SomeRepository.method(db, ...)`.
- Examples: `apps/api/src/api/v1/repositories/authorized_plate_repository.py`

## Entry Points

**ASGI application:**
- Location: `apps/api/src/main.py`
- Triggers: Uvicorn (or compatible ASGI server) loading `app`.
- Responsibilities: Middleware stack, exception handling, include `api_router` at `/api/v1`, root `GET /`.

**CLI / one-off scripts:**
- Location: `apps/api/src/seed_demo.py` — database seeding for demos (invoked manually, not part of request path).

**Health:**
- Location: `apps/api/src/api/v1/endpoints/health.py` — `GET /api/v1/health` (mounted without extra prefix in `api.py`).

## Error Handling

**Strategy:** Mix of explicit `HTTPException` in controllers and endpoints, FastAPI validation errors for schema/query violations, and a catch-all handler on the app for uncaught exceptions.

**Patterns:**
- Controllers translate “not found” repository results into `HTTPException(status_code=404, ...)` (e.g. `plate_controller.py`).
- `main.py` `global_exception_handler`: logs with traceback; in development returns more detail when `ENVIRONMENT`/`DEBUG` allow it; production returns generic 500 JSON.

## Cross-Cutting Concerns

**Logging:** Standard library `logging` with module-level `logger = logging.getLogger(__name__)` in controllers, deps, and device controller.

**Validation:** Pydantic on schemas; additional rules in controllers (e.g. file type/size for uploads in `access_log_controller.py`); plate rules in `utils/plate.py`.

**Authentication:** OAuth2 bearer tokens; JWT decode in `deps.get_current_user` with `TokenPayload` type check (`type == "access"`); password hashing and token creation in `apps/api/src/api/v1/core/security.py`.

**Rate limiting:** `slowapi` — login path uses limiter from `apps/api/src/api/v1/core/limiter.py` (see `endpoints/auth.py`).

---

*Architecture analysis: 2026-04-04*
