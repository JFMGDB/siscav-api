# External Integrations

**Analysis Date:** 2026-04-04

## APIs & External Services

**Gate / hardware actuator (optional):**
- User-configured HTTP endpoint — when `GATE_ACTUATOR_URL` is set, the API sends `POST` with JSON `{"action": "open"}` and expects HTTP 2xx (`apps/api/src/api/v1/controllers/gate_controller.py`).
- Timeout from `GATE_ACTUATOR_TIMEOUT_SECONDS` (default 5, clamped 1–120 in `apps/api/src/api/v1/core/config.py`).
- If URL is unset, responses use `integration=simulated` (no network call).

**IoT access-log ingest (incoming):**
- Devices call `POST /api/v1/access_logs/` with multipart image + form field `plate` (`apps/api/src/api/v1/endpoints/access_logs.py`).
- Optional shared secret: header `X-Device-Key` must match `DEVICE_INGEST_KEY` when that env var is set; in development without a key, ingest may be allowed (`apps/api/src/api/v1/deps.py` `verify_device_ingest_key`).

**Demo “device” HTTP API:**
- Routes under `/api/v1/devices/` return simulated Bluetooth data when `IOT_DEVICE_DEMO_API` is true; in `production`/`prod` the default is off unless explicitly enabled (`apps/api/src/api/v1/core/config.py`, `apps/api/src/api/v1/endpoints/devices.py`).
- Real Bluetooth is documented as browser-side (Web Bluetooth), not server-side.

## Data Storage

**Databases:**
- PostgreSQL — primary target; connection via `DATABASE_URL` or composed from `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, optional `POSTGRES_HOST` (default `db`), `POSTGRES_PORT` (`apps/api/src/api/v1/core/config.py`).
- SQLAlchemy engine: `create_engine(settings.database_url, pool_pre_ping=True)` in `apps/api/src/api/v1/db/session.py`.

**Hosted Postgres (Supabase):**
- Documented pattern: `DATABASE_URL` with `postgresql+psycopg2://...supabase.co:5432/...?sslmode=require` in `env.supabase.example`.
- Manual DDL path: `db/sql/supabase/00_complete_setup.sql` (Supabase SQL Editor); Alembic remains the in-repo migration source under `apps/api/src/alembic/versions/`.

**SQLite:**
- Fallback when no `DATABASE_URL` and incomplete `POSTGRES_*` (`sqlite:///./siscav_dev.db` in `apps/api/src/api/v1/core/config.py`); `alembic.ini` default URL also points at SQLite for offline tooling.
- UUID column abstraction for PG vs SQLite: `apps/api/src/api/v1/db/base.py` `GUID` TypeDecorator.

**File Storage:**
- Local filesystem — uploaded access-log images stored under `UPLOAD_DIR` (default `uploads`), size cap `MAX_FILE_SIZE_MB` (`apps/api/src/api/v1/core/config.py`); served by admin-only image route in `apps/api/src/api/v1/endpoints/access_logs.py`.

**Caching:**
- None detected in application code.

## Authentication & Identity

**Auth Provider:**
- Custom — no third-party IdP; users in relational DB with Argon2-hashed passwords (`apps/api/src/api/v1/core/security.py`).
- OAuth2-style password flow: token URL `/api/v1/login/access-token` (`apps/api/src/api/v1/deps.py` `OAuth2PasswordBearer`).
- JWT access and refresh tokens issued in auth layer (`apps/api/src/api/v1/core/security.py`, `apps/api/src/api/v1/endpoints/auth.py`); claims include `sub` (user UUID string) and `type` (`access` vs `refresh`).
- Admin-only operations gated with `is_admin` on `User` (`deps` helpers such as `get_current_admin_user`).

## Monitoring & Observability

**Error Tracking:**
- None — standard `logging` in handlers and controllers (e.g. `apps/api/src/main.py` global exception handler).

**Logs:**
- Python logging; Alembic logging configured via `alembic.ini` sections.

## CI/CD & Deployment

**Hosting:**
- Not defined in repository (no `Dockerfile` or `docker-compose*.yml` detected at workspace root).

**CI Pipeline:**
- GitHub Actions — `.github/workflows/ci.yml`: checkout, Python 3.13, `pip install -r requirements-dev.txt`, `ruff check` / `ruff format --check`, `pytest` with `DATABASE_URL: ""` to exercise SQLite fallback in tests.

## Environment Configuration

**Required env vars (production):**
- `SECRET_KEY` — must be strong and not `change_me_in_development` when `ENVIRONMENT` is `production` or `prod` (`apps/api/src/api/v1/core/config.py`).
- `DATABASE_URL` or full set of `POSTGRES_*` for real Postgres deployments.

**Common optional vars:**
- `DEVICE_INGEST_KEY` — required behavior for non-dev when set; see `env.local.example`.
- `GATE_ACTUATOR_URL`, `GATE_ACTUATOR_TIMEOUT_SECONDS`, `IOT_DEVICE_DEMO_API`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `ALGORITHM`, `DEBUG`, `ENVIRONMENT`.

**Secrets location:**
- Operator-managed (env on host, platform secrets, or local `.env` files not committed); example files `env.local.example`, `env.supabase.example` illustrate shape only.

## Webhooks & Callbacks

**Incoming:**
- None labeled as webhooks; device ingest is a normal authenticated (or dev-relaxed) REST `POST` to `/api/v1/access_logs/`.

**Outgoing:**
- Single integration: optional `POST` to `GATE_ACTUATOR_URL` from gate trigger (`apps/api/src/api/v1/controllers/gate_controller.py`).

## Browser / frontend coupling

**CORS:**
- `CORSMiddleware` allows local dev origins (ports 3000, 5173, 8000) on localhost and 127.0.0.1 (`apps/api/src/main.py`).

---

*Integration audit: 2026-04-04*
