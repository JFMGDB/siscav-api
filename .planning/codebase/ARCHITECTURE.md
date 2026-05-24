# Architecture

**Analysis Date:** 2026-04-04

## Pattern Overview

**Overall:** Layered monolith — a single FastAPI application with explicit horizontal slices (versioned API package) and vertical layering: HTTP surface → application services (“controllers”) → data access (“repositories”) → persistence (SQLAlchemy models).

**Key Characteristics:**
- **API versioning:** All business routes live under `apps.api.src.api.v1` and are mounted at `/api/v1` from `apps/api/src/main.py`.
- **Dependency injection:** FastAPI `Depends` in `apps/api/src/api/v1/deps.py` wires database sessions, JWT user resolution, device ingest key checks, and controller factories.
- **Thin routers, fat controllers:** `endpoints/*.py` mostly delegate to controller methods; controllers orchestrate validation, filesystem I/O, and repository calls.
- **Repository classes as static method namespaces:** Repositories in `apps/api/src/api/v1/repositories/` expose `@staticmethod` functions taking `Session`; they are not instantiated per request (controllers typically assign `self.foo_repository = FooRepository` for readability).

## Layers

**HTTP / presentation (FastAPI routers):**
- Purpose: Route definitions, OpenAPI metadata, `Query`/`Form`/`File` binding, and composing `Depends` for auth and controllers.
- Location: `apps/api/src/api/v1/endpoints/`
- Contains: One `APIRouter` per domain file (`auth.py`, `whitelist.py`, `access_logs.py`, `gate_control.py`, `devices.py`, `health.py`).
- Depends on: Controllers, `deps`, Pydantic schemas for response models.
- Used by: `apps/api/src/api/v1/api.py` aggregates routers into `api_router`.

**Application / domain orchestration (“controllers”):**
- Purpose: Business rules, HTTP-facing errors (`HTTPException`), coordination of multiple repositories, file uploads under `upload_dir`, and external HTTP calls (gate actuator).
- Location: `apps/api/src/api/v1/controllers/`
- Contains: `AuthController`, `PlateController`, `AccessLogController`, `GateController`, `DeviceController`.
- Depends on: `Session`, `get_settings()`, repositories (as class references), `apps/api/src/api/v1/utils/plate.py` for plate normalization.
- Used by: Endpoints via `Depends(get_*_controller)` from `deps.py`.

**Data access (repositories):**
- Purpose: SQLAlchemy 2.x queries (`select`, `scalars`, filters, pagination); no HTTP types here.
- Location: `apps/api/src/api/v1/repositories/`
- Contains: `UserRepository`, `AuthorizedPlateRepository`, `AccessLogRepository`.
- Depends on: Models, `Session`, occasionally schema enums (e.g. `AccessStatus` for filters).
- Used by: Controllers (and `deps.get_current_user` uses `UserRepository.get_by_id` directly).

**Persistence (ORM models):**
- Purpose: Table mapping and relationships.
- Location: `apps/api/src/api/v1/models/`
- Contains: `User`, `AuthorizedPlate`, `AccessLog` (`__init__.py` re-exports all three).
- Depends on: `apps/api/src/api/v1/db/base.py` (`Base`, `GUID` type decorator for PostgreSQL/SQLite portability).
- Used by: Repositories, Alembic (`apps/api/src/alembic/env.py` imports model modules so `Base.metadata` is complete).

**Infrastructure / cross-cutting:**
- Purpose: Settings, security primitives, DB session factory, rate limiting.
- Location: `apps/api/src/api/v1/core/config.py`, `apps/api/src/api/v1/core/security.py`, `apps/api/src/api/v1/core/limiter.py`, `apps/api/src/api/v1/db/session.py`.
- Depends on: Environment variables (documented in `config.py` module docstring); `.env` files are not read by this analysis.
- Used by: Entire stack; `main.py` calls `assert_production_secrets_valid()` before importing the app router.

**Contracts (Pydantic schemas):**
- Purpose: Request/response and token payload shapes; separation from ORM models.
- Location: `apps/api/src/api/v1/schemas/`

## Data Flow

**Authenticated JSON API (whitelist, list logs, register):**

1. Client sends `Authorization: Bearer <JWT>` to an endpoint in `endpoints/`.
2. `deps.get_current_user` decodes JWT with `python-jose`, validates `TokenPayload` (`apps/api/src/api/v1/schemas/token.py`), loads `User` via `UserRepository.get_by_id`.
3. Endpoint injects `AccessLogController` or `PlateController` with `get_db()` → `Session`.
4. Controller calls repository static methods; repository returns ORM entities or lists.
5. Controller or endpoint maps to Pydantic `*Read` models for the JSON response.

**Device access-log ingest (`POST /api/v1/access_logs/`):**

1. `verify_device_ingest_key` (`deps.py`) validates optional `X-Device-Key` against settings, or allows open ingest only in development when no key is set.
2. `AccessLogController.create_access_log` validates image, enforces max size from settings, normalizes plate, checks whitelist via `AuthorizedPlateRepository`, writes file to `upload_dir`, persists `AccessLog` via `AccessLogRepository`.

**Gate trigger (`POST /api/v1/gate_control/trigger`):**

1. `get_current_admin_user` ensures `User.is_admin`.
2. `GateController.trigger_gate` either returns a simulated response or POSTs JSON to `GATE_ACTUATOR_URL` using `urllib.request`, mapping failures to HTTP 502/503.

**Admin-only image download (`GET /api/v1/access_logs/images/{image_filename}`):**

1. `get_current_admin_user` gates access.
2. Endpoint resolves path via controller and returns raw bytes with a mapped `Content-Type` (logic split between `endpoints/access_logs.py` and controller path resolution).

**State Management:**
- Request-scoped SQLAlchemy `Session` only (generator in `get_db`); no in-memory global domain state. Upload files live on the filesystem under `UPLOAD_DIR`. Rate limiter state is handled by `slowapi` middleware.

## Key Abstractions

**`Base` and `GUID` (`db/base.py`):**
- Purpose: Single declarative metadata registry for Alembic and consistent UUID column behavior across PostgreSQL and SQLite.
- Pattern: SQLAlchemy 2.0 `DeclarativeBase` + custom `TypeDecorator`.

**`Settings` / `get_settings()` (`core/config.py`):**
- Purpose: Centralized, cached configuration (database URL resolution order, JWT parameters, upload limits, feature flags like `iot_device_demo_api`).
- Pattern: Pydantic `BaseModel` built from environment variables; `assert_production_secrets_valid()` guards production startup.

**`api_router` (`api/v1/api.py`):**
- Purpose: Single composition root for v1 routes with consistent prefixes (`/whitelist`, `/access_logs`, `/gate_control`, `/devices`) and tags for OpenAPI.

**`deps.py` dependency graph:**
- Purpose: Reusable security (`OAuth2PasswordBearer` token URL `/api/v1/login/access-token`), admin checks, device ingest policy, and controller construction.

## Entry Points

**ASGI application:**
- Location: `apps/api/src/main.py`
- Triggers: Uvicorn (or any ASGI server) loads `app = FastAPI(...)`.
- Responsibilities: `assert_production_secrets_valid()`, global exception handler, CORS, SlowAPI middleware and `RateLimitExceeded` handler, mount `api_router` at `/api/v1`, root `GET /` health-style message.

**Database migrations:**
- Location: `apps/api/src/alembic/env.py` with revision scripts in `apps/api/src/alembic/versions/`
- Triggers: Alembic CLI (typically with `DATABASE_URL` or settings-derived URL).
- Responsibilities: Align schema with `Base.metadata` after models are imported.

**Demo / operational scripts:**
- Location: `scripts/seed_demo.py` (data seeding; not part of the HTTP request path unless invoked manually).

## Error Handling

**Strategy:** Layered — repositories avoid raising HTTP errors; controllers raise `fastapi.HTTPException` for business and validation failures; `main.py` registers a catch-all `Exception` handler that exposes details in development and a generic message in production.

**Patterns:**
- Explicit status codes for gate actuator timeouts and non-2xx responses (`gate_controller.py`).
- JWT validation failures mapped to 403 in `get_current_user` (`deps.py`).
- Validation errors from Pydantic/JWT in auth flows handled in `endpoints/auth.py` (refresh/login paths).

## Cross-Cutting Concerns

**Logging:** Standard library `logging` in `main.py`, `deps.py`, and controllers (e.g. `access_log_controller.py`, `gate_controller.py`).

**Validation:** Pydantic v2 on schemas; additional checks in controllers (e.g. image `content_type`, file size).

**Authentication:** JWT access vs refresh types enforced in `deps.get_current_user` and refresh handling in `auth.py`; password hashing via `core/security.py` (used by auth flow). Device ingest uses header API key comparison with `secrets.compare_digest` when configured.

**Rate limiting:** `slowapi` limiter from `core/limiter.py` applied on login-related routes in `endpoints/auth.py`.

---

*Architecture analysis: 2026-04-04*
