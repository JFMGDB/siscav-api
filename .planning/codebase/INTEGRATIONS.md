# External Integrations

**Analysis Date:** 2026-04-04

## APIs & External Services

**Third-party SaaS SDKs in application code:**
- **Not detected** — No imports of Supabase client libraries, Stripe, AWS SDKs, or similar inside `apps/api/src/` (integration with Supabase is at the **database connection** layer only).

**IoT / device direction:**
- **Inbound HTTP** — Devices and clients call REST endpoints under `/api/v1` (see `apps/api/src/api/v1/api.py`): `devices`, `whitelist`, `access_logs`, `gate_control`, etc.
- **Gate / relay:** `apps/api/src/api/v1/controllers/gate_controller.py` documents that production should talk to hardware via HTTP/WebSocket/MQTT; the current `trigger_gate` implementation returns a **simulated success** without calling an external network service.

**Frontend / browser:**
- **CORS** — `apps/api/src/main.py` allows specific local origins (e.g. `http://localhost:3000`, `5173`, `8000`) for SPA dev servers.
- **Web Bluetooth** — Device endpoints (`apps/api/src/api/v1/endpoints/devices.py`) are documented as cooperating with the **browser Web Bluetooth API** on the client; the API does not speak Bluetooth itself.

## Data Storage

**Databases:**
- **PostgreSQL** — Primary target in production-style setups. Connection via SQLAlchemy `create_engine(settings.database_url, pool_pre_ping=True)` in `apps/api/src/api/v1/db/session.py`.
- **Supabase (hosted PostgreSQL)** — Documented in `docs/installation.md`, `docs/setup_database_guide.md`, and `apps/api/docs/database/supabase-migration.md`. Use a `DATABASE_URL` pointing at Supabase’s Postgres endpoint with `sslmode=require` (pattern described in `env.supabase.example` and docs — do not commit real credentials).
- **SQLite** — Development fallback when `DATABASE_URL` and required `POSTGRES_*` variables are absent (`apps/api/src/api/v1/core/config.py`). `session.py` can auto-create tables from SQLAlchemy metadata on empty SQLite for local convenience.

**Schema provisioning:**
- **Alembic** — Python migrations under `apps/api/src/alembic/versions/`.
- **Raw SQL** — Supplementary scripts in `db/sql/supabase/` (e.g. `db/sql/supabase/00_complete_setup.sql`) for manual execution in Supabase Studio or `psql`.

**File Storage:**
- **Local filesystem** — `upload_dir` / `max_file_size_mb` in `apps/api/src/api/v1/core/config.py` (`UPLOAD_DIR`, `MAX_FILE_SIZE_MB`). No S3/blob SDK detected in `apps/`.

**Caching:**
- **None as a separate service** — Rate limiting uses `slowapi` with default in-memory storage unless configured otherwise (`apps/api/src/api/v1/core/limiter.py`).

## Authentication & Identity

**Auth Provider:**
- **Custom JWT (local)** — Not OAuth2 against Google/GitHub/etc. Access and refresh tokens are issued with `python-jose` (`apps/api/src/api/v1/core/security.py`). Validation uses `SECRET_KEY` and `ALGORITHM` from settings (`apps/api/src/api/v1/core/config.py`).

**HTTP auth style:**
- **OAuth2 password flow (FastAPI)** — `OAuth2PasswordRequestForm` and token URL `/api/v1/login/access-token` in `apps/api/src/api/v1/endpoints/auth.py`; bearer dependency `OAuth2PasswordBearer` in `apps/api/src/api/v1/deps.py`.

**User credentials:**
- **Argon2 password hashes** stored in the database via repositories/controllers (see `security.py` and user model under `apps/api/src/api/v1/models/user.py`).

## Monitoring & Observability

**Error Tracking:**
- **None integrated** — No Sentry or similar in dependencies or `main.py`.

**Logs:**
- **Standard library `logging`** — Used in `apps/api/src/main.py` (global exception handler) and `apps/api/src/api/v1/deps.py`. No structured logging stack mandated in code.

## CI/CD & Deployment

**Hosting:**
- **Not defined in code** — No Dockerfile or `docker-compose*.yml` found at repo root in the current tree; deployment is environment-specific.

**CI Pipeline:**
- **GitHub Actions** — `.github/workflows/ci.yml` runs Ruff and pytest with `DATABASE_URL: ""` to exercise SQLite fallback in tests.

## Environment Configuration

**Required env vars (typical):**
- **`DATABASE_URL`** OR full **`POSTGRES_USER`**, **`POSTGRES_PASSWORD`**, **`POSTGRES_DB`** (optional `POSTGRES_HOST`, `POSTGRES_PORT`) — See `apps/api/src/api/v1/core/config.py`.
- **`SECRET_KEY`** — JWT signing; must be strong in production.
- Optional: **`ALGORITHM`**, **`ACCESS_TOKEN_EXPIRE_MINUTES`**, **`REFRESH_TOKEN_EXPIRE_DAYS`**, **`UPLOAD_DIR`**, **`MAX_FILE_SIZE_MB`**, **`ENVIRONMENT`**, **`DEBUG`**.

**Secrets location:**
- Local or host-specific `.env` / `.env.supabase` files (gitignored); examples only in `env.local.example` and `env.supabase.example`. Never commit secrets.

## Webhooks & Callbacks

**Incoming:**
- **None named as webhooks** — Standard REST POST/GET endpoints only; no dedicated webhook signature verification layer detected.

**Outgoing:**
- **None implemented** — No `httpx`/`requests` usage under `apps/` for callbacks to external systems; gate control remains a stub until device messaging is added.

---

*Integration audit: 2026-04-04*
