# Codebase Concerns

**Analysis Date:** 2026-04-10

## Tech Debt

**Deprecated CRUD layer alongside repositories/controllers:**
- Issue: Three modules remain marked deprecated with `DeprecationWarning` while parallel `repositories/` and `controllers/` implementations are canonical. Dead code paths increase confusion and maintenance surface.
- Files: `apps/api/src/api/v1/crud/crud_user.py`, `apps/api/src/api/v1/crud/crud_access_log.py`, `apps/api/src/api/v1/crud/crud_authorized_plate.py`
- Impact: Contributors may import deprecated APIs; duplicate logic can diverge over time.
- Fix approach: Remove CRUD modules after confirming no remaining imports (grep the codebase), or re-export thin wrappers only if external compatibility is required.

**pyproject.toml vs pinned requirements drift:**
- Issue: `[project.dependencies]` in `pyproject.toml` lists `passlib[bcrypt]` while `requirements.txt` and runtime hashing use Argon2 via `passlib[argon2]` (see `apps/api/src/api/v1/core/security.py`). CI and Docker install from `requirements*.txt`, not `[project]`.
- Files: `pyproject.toml`, `requirements.txt`, `apps/api/src/api/v1/core/security.py`
- Impact: Misleading documentation of the real stack; tooling that reads only `pyproject.toml` may install wrong extras.
- Fix approach: Align `pyproject.toml` with `requirements.txt` (Argon2) or document a single source of truth and sync both.

**Refresh token configuration without implementation:**
- Issue: `Settings` exposes `refresh_token_expire_days` (`apps/api/src/api/v1/core/config.py`) and `env.local.example` documents `REFRESH_TOKEN_EXPIRE_DAYS`, but there is no refresh-token endpoint or JWT issuance for refresh tokens anywhere under `apps/api/src/api/v1/endpoints/` or `auth_controller.py`.
- Files: `apps/api/src/api/v1/core/config.py`, `env.local.example`, `apps/api/src/api/v1/controllers/auth_controller.py`
- Impact: Operators may assume refresh flows exist; clients cannot implement standard refresh behavior without custom work.
- Fix approach: Either implement refresh tokens and document them in OpenAPI, or remove unused settings and env vars to avoid false expectations.

**Gate and device domains are stubs:**
- Issue: `GateController.trigger_gate()` always returns success without I/O. `DeviceController` returns fixed mock Bluetooth data.
- Files: `apps/api/src/api/v1/controllers/gate_controller.py`, `apps/api/src/api/v1/controllers/device_controller.py`
- Impact: Production behavior for IoT control is not implemented; integration tests may pass while hardware never moves.
- Fix approach: Replace stubs with real transports (HTTP client to device, MQTT, etc.), configuration per device, and failure handling.

**Standalone ML script outside dependency and import conventions:**
- Issue: `apps/api/src/api/v1/ml/recognize-plate.py` uses OpenCV, EasyOCR, NumPy, and Windows-only `winsound`; filename uses a hyphen (not importable as a normal module). These libraries are not listed in `requirements.txt` / `pyproject.toml` for the API service.
- Files: `apps/api/src/api/v1/ml/recognize-plate.py`
- Impact: OCR pipeline is not part of the deployable API; running the script requires a separate environment; cross-platform deployment (Linux servers/CI) is not supported as-is.
- Fix approach: Move to a dedicated package or `scripts/` with its own `requirements-ml.txt`, rename to `recognize_plate.py` if imported, or integrate behind a documented optional extra.

## Known Bugs

**Not detected** via code comments (`TODO`/`FIXME` grep across `*.py` returned no matches). Runtime defects would need reproduction in staging or production logs.

## Security Considerations

**Default JWT signing secret:**
- Risk: If `SECRET_KEY` is unset, `apps/api/src/api/v1/core/config.py` defaults to `"change_me_in_development"`, producing predictable tokens.
- Files: `apps/api/src/api/v1/core/config.py`
- Current mitigation: Operators can set `SECRET_KEY` via environment (see `docker-compose.yml` pass-through, `env.local.example`).
- Recommendations: Fail fast in non-debug environments when the default is still in use; document mandatory rotation for production.

**Unauthenticated access-log ingestion:**
- Risk: `POST /api/v1/access_logs/` (`apps/api/src/api/v1/endpoints/access_logs.py`) has no `Depends(get_current_user)` or device credential. Any client can upload images and create DB rows, enabling log spam and disk consumption under `upload_dir`.
- Files: `apps/api/src/api/v1/endpoints/access_logs.py`, `apps/api/src/api/v1/controllers/access_log_controller.py`
- Current mitigation: File size cap via `MAX_FILE_SIZE_MB` and `content_type` starting with `image/`; path traversal blocked for image reads in `get_image_path()`.
- Recommendations: API keys or signed requests for devices, per-device rate limits, optional IP allowlists, or mTLS for edge devices.

**Upload validation relies on client-reported MIME type:**
- Risk: `content_type` can be spoofed; there is no magic-byte / PIL validation of image format in `AccessLogController.create_access_log()`.
- Files: `apps/api/src/api/v1/controllers/access_log_controller.py`
- Current mitigation: Extension and storage as uploaded bytes under a UUID filename.
- Recommendations: Verify file signatures and reject non-images after decode.

**No role-based access control:**
- Risk: `User` model (`apps/api/src/api/v1/models/user.py`) has no roles field. Any authenticated user can manage whitelist, list access logs, trigger gate (stub), and use device endpoints.
- Files: `apps/api/src/api/v1/models/user.py`, `apps/api/src/api/v1/endpoints/whitelist.py`, `apps/api/src/api/v1/endpoints/gate_control.py`
- Current mitigation: Not applicable beyond “must be logged in.”
- Recommendations: Add roles or claims in JWT and enforce on sensitive routes.

**CORS allowlist is development-oriented:**
- Risk: `main.py` hardcodes localhost/127.0.0.1 origins. Production frontends on other hosts are not supported without code changes.
- Files: `apps/api/src/main.py`
- Current mitigation: Credentials restricted to listed origins (not `*`).
- Recommendations: Drive allowed origins from settings/environment for deployment flexibility.

## Performance Bottlenecks

**Full in-memory read of upload body:**
- Problem: `file.file.read()` loads the entire upload before enforcing `max_file_size_mb` in `AccessLogController.create_access_log()`.
- Files: `apps/api/src/api/v1/controllers/access_log_controller.py`
- Cause: Size check happens after full read.
- Improvement path: Enforce a streaming limit (e.g., read in chunks with cumulative cap) or rely on reverse-proxy `client_max_body_size` / ASGI limits.

**SQLite fallback vs PostgreSQL in production:**
- Problem: `config.py` falls back to `sqlite:///./siscav_dev.db` when no Postgres URL is configured. Models use PostgreSQL-specific types (`PGUUID`, enums) aligned with Alembic migrations targeting Postgres.
- Files: `apps/api/src/api/v1/core/config.py`, `apps/api/src/api/v1/models/*.py`, `apps/api/src/alembic/versions/20251102_0001_initial_models.py`
- Cause: Dual-target behavior is convenient for quick runs but not identical to production.
- Improvement path: Treat SQLite as test-only (document explicitly), or use portable types in models if SQLite must remain a first-class dev DB.

## Fragile Areas

**Docker Compose service coupling:**
- Files: `docker-compose.yml`
- Why fragile: The `api` service declares `depends_on: db` with a health condition. The `db` service uses `profiles: ["local"]`. Running Compose without the `local` profile may leave `db` undefined while `api` still expects it, depending on Compose version and invocation.
- Safe modification: Document required profiles (`--profile local`) for local Postgres; for Supabase-only flows, use a compose override or split files so `api` does not depend on a missing service.

**Alembic URL resolution vs app runtime:**
- Files: `apps/api/src/alembic/env.py`, `apps/api/src/api/v1/core/config.py`
- Why fragile: Migrations use `DATABASE_URL` or `get_settings().database_url`; manual `alembic` runs must use the same DB as the running app or migrations apply to the wrong database.
- Safe modification: Always set `DATABASE_URL` explicitly in deployment scripts; avoid mixing SQLite fallback for app with Postgres for migrations.

**Test coverage gaps**

- What's not tested: End-to-end behavior with real PostgreSQL (CI uses empty `DATABASE_URL` and SQLite fallback from config for pytest; integration tests use in-memory SQLite in `tests/integration/test_endpoints.py`).
- Files: `.github/workflows/ci.yml`, `tests/integration/test_endpoints.py`
- Risk: Postgres-specific behavior (constraints, enum types, connection pooling) may differ from SQLite-only CI.
- Priority: Medium

**Lint vs ML script:**
- Files: `ruff.toml`, `apps/api/src/api/v1/ml/recognize-plate.py`
- Why fragile: Ruff enables `T20` (print) globally except under `tests/**`. The ML script uses `print` for CLI-style output and may fail `ruff check` unless excluded or refactored to logging.
- Safe modification: Add a per-file ignore for `**/ml/**` or move the script out of linted application paths.

## Scaling Limits

**Local filesystem for images:**
- Current capacity: Images stored under `upload_dir` (default `uploads`) with paths recorded in `image_storage_key`.
- Limit: Single-disk, single-instance storage; no deduplication or object storage offload.
- Scaling path: Move to S3-compatible storage or Supabase Storage; store object keys instead of local paths.

**Rate limiting scope:**
- Current capacity: Login endpoint uses SlowAPI (`apps/api/src/api/v1/endpoints/auth.py`, `apps/api/src/api/v1/core/limiter.py`).
- Limit: Other endpoints (especially unauthenticated `access_logs` POST) lack comparable limits at the application layer.
- Scaling path: Add limits per route or global limits; use edge/WAF for abusive traffic.

## Dependencies at Risk

**Not assessed for CVEs in this pass.** Runtime pins are loose in `requirements.txt` (unpinned versions). CI installs latest compatible versions on each run, which can introduce unexpected upgrades.

- Risk: Unpinned dependencies can change behavior between CI runs.
- Impact: Flaky or sudden breakage on reinstall.
- Migration plan: Introduce lock files (`pip-tools`, `uv lock`) or pin minimum versions with periodic review.

## Missing Critical Features

**Production IoT integration:**
- Problem: Physical gate control and real Bluetooth/camera flows are not implemented (stubs only).
- Blocks: Safe, auditable remote opening and real device pairing from this API alone.

**Refresh token API:**
- Problem: Configuration suggests refresh tokens; no API delivers them.
- Blocks: Long-lived sessions without re-login using documented env vars alone.

## Test Coverage Gaps

**Controller and repository layers:**
- What's not tested: `tests/` cover health, auth, whitelist, access logs, config, security, deps, and repositories at varying levels; `plate_controller.py` (~210 lines) is among the larger modules—verify coverage reports (`pytest --cov`) for branches in update/delete and error paths.
- Files: `apps/api/src/api/v1/controllers/plate_controller.py`, `tests/unit/test_controllers.py`
- Risk: Regression in plate CRUD or validation logic.
- Priority: Medium

**Deprecated CRUD:**
- What's not tested: Deprecated modules may lack direct tests; if retained, accidental use is untested.
- Files: `apps/api/src/api/v1/crud/*.py`
- Risk: Low if unused; removal eliminates the gap.

---

*Concerns audit: 2026-04-10*
