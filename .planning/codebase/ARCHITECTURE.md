# Architecture

**Analysis Date:** 2026-04-10

## Pattern Overview

**Overall:** Layered FastAPI service with versioned API surface (`/api/v1`), dependency injection, and a **Router → Controller → Repository** flow for persistence-backed features.

**Key Characteristics:**
- HTTP routing lives in `endpoints/`; route handlers stay thin and delegate to controllers.
- Business rules, validation orchestration, and `HTTPException` mapping live in `controllers/`.
- SQLAlchemy data access uses static methods on `repositories/` classes (no repository instances required).
- Request/response shapes are Pydantic models in `schemas/`; ORM entities are in `models/` inheriting from `Base` in `apps/api/src/api/v1/db/base.py`.
- Cross-cutting infrastructure (settings, JWT/password helpers, rate limiting) lives under `core/`.

## Layers

**HTTP / API surface (FastAPI routers):**
- Purpose: Define routes, OpenAPI metadata, `Depends()` wiring, and map DTOs via `response_model`.
- Location: `apps/api/src/api/v1/endpoints/`
- Contains: One `APIRouter` module per domain (`auth.py`, `whitelist.py`, `access_logs.py`, `devices.py`, `gate_control.py`, `health.py`).
- Depends on: `controllers/` (via `deps.py`), `schemas/`, FastAPI primitives.
- Used by: Aggregator `apps/api/src/api/v1/api.py`, included from `apps/api/src/main.py`.

**Application / use-case (controllers):**
- Purpose: Encode domain logic, call repositories, raise `HTTPException` with appropriate status codes, use `logging` where needed.
- Location: `apps/api/src/api/v1/controllers/`
- Contains: Classes such as `PlateController`, `AuthController`, `AccessLogController`; some controllers omit DB (`GateController`, `DeviceController` — stubs/simulations).
- Depends on: `Session` from `get_db`, `repositories/`, `core/config.py`, `core/security.py`, `utils/`, `models/` types.
- Used by: Endpoints through factories in `apps/api/src/api/v1/deps.py`.

**Data access (repositories):**
- Purpose: Encapsulate SQLAlchemy queries and transactions (`commit`/`rollback`/`refresh` patterns where applicable).
- Location: `apps/api/src/api/v1/repositories/`
- Contains: Classes with `@staticmethod` methods taking `Session` as first argument (e.g. `AuthorizedPlateRepository.get_by_id` in `authorized_plate_repository.py`).
- Depends on: `models/`, SQLAlchemy `Session`, `select()` / `scalar()` / `scalars()`.
- Used by: Controllers only (not directly from endpoints).

**Persistence models (ORM):**
- Purpose: Map tables to Python classes using SQLAlchemy 2.0 style (`Mapped`, `mapped_column`).
- Location: `apps/api/src/api/v1/models/`
- Contains: `User`, `AuthorizedPlate`, `AccessLog` (and related table definitions).
- Depends on: `apps/api/src/api/v1/db/base.py` (`Base`).
- Used by: Repositories, Alembic metadata (`target_metadata` in `apps/api/src/alembic/env.py`).

**Contracts (Pydantic schemas):**
- Purpose: Validate and serialize API inputs/outputs; separate from ORM models.
- Location: `apps/api/src/api/v1/schemas/`
- Contains: e.g. `AuthorizedPlateCreate`, `AccessLogRead`, `Token`, `TokenPayload`.
- Depends on: Pydantic only.
- Used by: Endpoints and controllers.

**Infrastructure:**
- **Configuration:** `apps/api/src/api/v1/core/config.py` — `Settings` built from environment (see docstring for `DATABASE_URL` resolution order); `get_settings()` is LRU-cached.
- **Security:** `apps/api/src/api/v1/core/security.py` — Argon2 via passlib, JWT encode/decode helpers using `python-jose`.
- **Rate limiting:** `apps/api/src/api/v1/core/limiter.py` — shared `slowapi` `Limiter`; login applies `@limiter.limit("5/minute")` in `apps/api/src/api/v1/endpoints/auth.py`.
- **DB session:** `apps/api/src/api/v1/db/session.py` — `get_db()` generator for per-request `Session`.

**Legacy / transitional:**
- Location: `apps/api/src/api/v1/crud/`
- Purpose: Older module-style CRUD; **deprecated** in favor of repositories/controllers (see deprecation banner in `apps/api/src/api/v1/crud/crud_user.py`). Prefer new code in `repositories/` and `controllers/`.

## Data Flow

**Authenticated request (example — whitelist list):**

1. Client calls `GET /api/v1/whitelist/` with `Authorization: Bearer <JWT>`.
2. `reusable_oauth2` + `get_current_user` in `apps/api/src/api/v1/deps.py` decode JWT (`settings.secret_key`, `settings.algorithm`), load `User` via `UserRepository.get_by_id`.
3. `get_plate_controller` provides `PlateController(db)`.
4. `PlateController.get_all` calls `AuthorizedPlateRepository.get_all(self.db, ...)`.
5. Repository returns ORM rows; FastAPI serializes to `response_model=list[AuthorizedPlateRead]`.

**Login:**

1. `POST /api/v1/login/access-token` with OAuth2 form (`apps/api/src/api/v1/endpoints/auth.py`).
2. `AuthController.authenticate` uses `UserRepository` + `verify_password` from `security.py`.
3. On success, `create_access_token_for_user` issues JWT via `create_access_token`.

**IoT access log ingest (unauthenticated POST, list/images protected):**

1. `POST /api/v1/access_logs/` accepts multipart image + plate (`access_logs.py`).
2. `AccessLogController.create_access_log` validates image type/size, normalizes plate, checks whitelist via `AuthorizedPlateRepository`, writes file under `settings.upload_dir`, persists row via `AccessLogRepository` (`access_log_controller.py`).

**State Management:**
- No global application state for domain data; per-request `Session` from `get_db()`. FastAPI `app.state.limiter` holds the rate limiter instance (`main.py`).

## Key Abstractions

**`APIRouter` aggregation:**
- Purpose: Single mount point for all v1 routes.
- Examples: `apps/api/src/api/v1/api.py` exports `api_router`; `main.py` does `app.include_router(api_router, prefix="/api/v1")`.

**Dependency providers (`deps.py`):**
- Purpose: Centralize OAuth2 scheme, `get_current_user`, and controller factories for `Depends()`.
- Pattern: Use `Annotated[..., Depends(...)]` in endpoints; lazy import for `DeviceController` to avoid cycles.

**Repository static API:**
- Purpose: Thin, testable data layer without instantiating repository objects in controllers.
- Examples: `apps/api/src/api/v1/repositories/authorized_plate_repository.py`, `user_repository.py`, `access_log_repository.py`.

**Settings singleton:**
- Purpose: One resolved config object per process via `get_settings()` in `config.py`.

## Entry Points

**ASGI application:**
- Location: `apps/api/src/main.py`
- Triggers: Uvicorn loads `apps.api.src.main:app` (see `docker-compose.yml` `command`).
- Responsibilities: Instantiate `FastAPI`, attach rate-limit exception handler and `SlowAPIMiddleware`, CORS, root `GET /`, include `api_router` at `/api/v1`.

**CLI / migrations:**
- Alembic env: `apps/api/src/alembic/env.py` — sets `sqlalchemy.url` from `DATABASE_URL` or `get_settings().database_url`; imports all models so `Base.metadata` is complete.
- Config file: `alembic.ini` at repo root points `script_location` to `apps/api/src/alembic`.

## Error Handling

**Strategy:** Raise `fastapi.HTTPException` from controllers (and `deps.py` for auth failures) with explicit `status` codes; repositories propagate DB errors to controllers which may wrap in `HTTPException` (e.g. create path in `plate_controller.py`).

**Patterns:**
- Auth: 403/404 from `get_current_user` (`deps.py`).
- Validation / conflicts: 400/409 from controllers (e.g. duplicate plate).
- File upload: 400/413 from `AccessLogController`.

## Cross-Cutting Concerns

**Logging:** Standard library `logging` in controllers (`logging.getLogger(__name__)`).

**Validation:** Pydantic schemas on inputs; extra rules in controllers (e.g. Brazilian plate validation via `apps/api/src/api/v1/utils/plate.py`).

**Authentication:** OAuth2 password flow + JWT bearer; token URL `/api/v1/login/access-token` aligned with `OAuth2PasswordBearer` in `deps.py`.

---

*Architecture analysis: 2026-04-10*
