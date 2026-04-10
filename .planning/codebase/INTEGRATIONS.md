# External Integrations

**Analysis Date:** 2026-04-10

## APIs & External Services

**HTTP API surface (this service):**
- FastAPI application exposes REST routes under `/api/v1` (see `apps/api/src/api/v1/api.py`). OpenAPI is provided by FastAPI by default (`/docs`, `/redoc` when enabled).
- No third-party SaaS HTTP clients (no `requests`, `httpx`, `boto3`, etc.) in application code under `apps/` — integrations are limited to database drivers and auth/crypto libraries.

**IoT / gate control (outbound, planned):**
- `apps/api/src/api/v1/controllers/gate_controller.py` — `trigger_gate()` is a stub returning success; docstring describes future HTTP/WebSocket/MQTT to devices. No live outbound integration implemented.

**Developer tooling (not runtime):**
- `httpx` appears in `pyproject.toml` / `requirements-dev.txt` for optional dev/CI use; tests use `fastapi.testclient.TestClient` (`tests/test_main.py`, `tests/integration/test_endpoints.py`, etc.), not httpx against external APIs.

## Data Storage

**Databases:**
- PostgreSQL — Primary target for production and local Docker. Connection via SQLAlchemy URL:
  - Explicit `DATABASE_URL` (e.g. Supabase-hosted Postgres pattern documented in `env.supabase.example` and `apps/api/src/api/v1/core/config.py` comments).
  - Or composed from `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, optional `POSTGRES_HOST` (default `db`), `POSTGRES_PORT` (default `5432`) — see `env.local.example` and `docker-compose.yml`.
- SQLite — Fallback when neither `DATABASE_URL` nor full `POSTGRES_*` set: `sqlite:///./siscav_dev.db` (`config.py`). Used for lightweight local runs and CI (`DATABASE_URL` cleared in `.github/workflows/ci.yml` so tests use fallback behavior as configured).

**ORM / migrations:**
- SQLAlchemy + Alembic (`apps/api/src/api/v1/db/session.py`, `apps/api/src/alembic/`).

**Supabase (managed Postgres):**
- Not a separate SDK: Supabase is used as a hosted PostgreSQL endpoint when `DATABASE_URL` points at the Supabase project. Supplemental DDL for manual setup lives in `db/sql/supabase/` and is documented in `docs/DB_MIGRATION_SUPABASE.md`.

**File Storage:**
- Local filesystem — `Settings.upload_dir` from `UPLOAD_DIR` env (default `uploads`) in `apps/api/src/api/v1/core/config.py`. Access log uploads processed in `apps/api/src/api/v1/controllers/access_log_controller.py` / `endpoints/access_logs.py`. No S3/blob SDK in codebase.

**Caching:**
- None detected (no Redis or in-memory cache layer in application code).

## Authentication & Identity

**Auth Provider:**
- Custom JWT — `python-jose` in `apps/api/src/api/v1/core/security.py` (`create_access_token`, HS256 by default via `ALGORITHM` env). OAuth2 password flow form in `apps/api/src/api/v1/endpoints/auth.py` (`OAuth2PasswordRequestForm`).
- Password storage — `passlib` with Argon2 in `security.py` (`verify_password`, `get_password_hash`).
- No OAuth2 social login, Auth0, Cognito, or Supabase Auth client in Python code — only DB-backed users and JWT.

**Rate limiting:**
- `slowapi` with client key `get_remote_address` (`apps/api/src/api/v1/core/limiter.py`); applied on login-related routes (e.g. `auth.py`).

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry, Rollbar, etc.).

**Logs:**
- Standard Python logging implied for Alembic (`apps/api/src/alembic/env.py` `fileConfig`); application-wide structured logging framework not present beyond FastAPI/Uvicorn defaults.

## CI/CD & Deployment

**Hosting:**
- Not pinned to a single platform in code. Docker images built from `Dockerfile.dev` for development-style runs.

**CI Pipeline:**
- GitHub Actions — `.github/workflows/ci.yml`: Python 3.13, pip cache from `requirements.txt` / `requirements-dev.txt`, `ruff check` + `ruff format --check`, `pytest` with coverage.

## Environment Configuration

**Required env vars (typical):**
- Database: `DATABASE_URL` **or** `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (and optionally `POSTGRES_HOST`, `POSTGRES_PORT`).
- JWT: `SECRET_KEY`, optional `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` — see `apps/api/src/api/v1/core/config.py`.
- Uploads: optional `UPLOAD_DIR`, `MAX_FILE_SIZE_MB`.

**Secrets location:**
- Supplied at deploy/runtime (env files, orchestrator secrets). Example key names only: `env.local.example`, `env.supabase.example`. Do not commit real secrets.

## Webhooks & Callbacks

**Incoming:**
- None dedicated as “webhooks” — standard REST endpoints only (`/api/v1/...`). Devices/clients call the API directly.

**Outgoing:**
- None implemented toward external callback URLs. Future IoT command path described in `gate_controller.py` only.

## Cross-origin clients

**Browsers:**
- CORS middleware in `apps/api/src/main.py` allows specific localhost origins (ports 3000, 5173, 8000) for frontend dev — not an external API integration but a browser security configuration.

---

*Integration audit: 2026-04-10*
