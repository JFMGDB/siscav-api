# Codebase Concerns

**Analysis Date:** 2026-04-04

## Tech Debt

**Public registration rate limit tuned for tests:**
- Issue: `POST /api/v1/register` uses `@limiter.limit("100/minute")` with an inline comment stating it was temporarily increased for tests.
- Files: `apps/api/src/api/v1/endpoints/auth.py`
- Impact: Easier account-creation abuse and mailbox flooding relative to a stricter production default (e.g. aligned with login at `5/minute`).
- Fix approach: Lower the limit for non-development environments (or use configuration via `Settings`) and document the intended production value.

**Gate actuator HTTP client:**
- Issue: `GateController` uses `urllib.request.urlopen` instead of a shared async-capable client with structured timeouts/retries.
- Files: `apps/api/src/api/v1/controllers/gate_controller.py`
- Impact: Synchronous network I/O blocks a worker under slow or failing actuators; harder to extend with auth headers, mTLS, or retry policies.
- Fix approach: Introduce an httpx-based client (project already lists `httpx` for dev/tests in `pyproject.toml`) with explicit connect/read timeouts and optional retries.

**Configuration without pydantic-settings:**
- Issue: Settings are assembled manually from `os.getenv` in `apps/api/src/api/v1/core/config.py` (documented as intentional to minimize dependencies).
- Impact: No unified validation story for env vars (typos fail silently or at runtime); harder to document required vars in one schema.
- Fix approach: Either adopt `pydantic-settings` or add a startup validation pass that fails fast on missing critical vars in production.

**Orphan / demo ML script in API tree:**
- Issue: `apps/api/src/api/v1/ml/recognize-plate.py` is a standalone OpenCV/EasyOCR script (including `winsound`), not imported by the FastAPI app.
- Files: `apps/api/src/api/v1/ml/recognize-plate.py`
- Impact: Confusing layout, platform-specific code, and dependencies not reflected in the main API dependency set unless someone runs it manually.
- Fix approach: Move to a separate `tools/` or `scripts/` package with its own requirements, or remove if obsolete.

**Removed IoT client application:**
- Issue: Git history shows deletion of `apps/iot-device/` and related Arduino assets; documentation elsewhere may still reference those paths.
- Impact: Onboarding docs and external checklists can point to missing code; hardware integration is API-side only until a new client exists.
- Fix approach: Align `README.md` and `docs/` with the current repo layout and link to replacement integration guidance if any.

## Known Bugs

**`scripts/debug_token.py` path bootstrap:**
- Issue: The script inserts `Path(__file__).parent` (the `scripts/` directory) into `sys.path`, while imports use `apps.api.src...`, which typically requires the repository root on `PYTHONPATH`.
- Files: `scripts/debug_token.py`
- Trigger: Running the script from `scripts/` without setting `PYTHONPATH` to the repo root.
- Workaround: Run from repository root with `PYTHONPATH` set to the workspace root, or fix the script to insert the repo root (e.g. parent of `scripts/`).

## Security Considerations

**Whitelist management is not admin-only:**
- Issue: All CRUD routes under `/api/v1/whitelist/` depend on `get_current_user`, not `get_current_admin_user`.
- Files: `apps/api/src/api/v1/endpoints/whitelist.py`, `apps/api/src/api/v1/deps.py`
- Current mitigation: Any authenticated user can list, create, update, and delete authorized plates.
- Recommendations: Restrict mutating operations (and possibly reads) to administrators, or introduce roles/tenant scoping if multi-tenant access is required.

**Access log listing exposes sensitive operational data to any authenticated user:**
- Issue: `GET /api/v1/access_logs/` requires only `get_current_user`; responses include plate text and metadata (images are admin-only via `GET /api/v1/access_logs/images/{image_filename}`).
- Files: `apps/api/src/api/v1/endpoints/access_logs.py`
- Current mitigation: Image download is gated by `get_current_admin_user` in `get_access_log_image`.
- Recommendations: Treat log payloads as privileged; align list access with admin or a dedicated “viewer” role, and consider redaction for non-admin users.

**Device ingest key optional in development:**
- Issue: When `DEVICE_INGEST_KEY` is unset, `verify_device_ingest_key` allows requests if `environment` is development-like; otherwise it returns 401.
- Files: `apps/api/src/api/v1/deps.py`, `apps/api/src/api/v1/core/config.py`
- Current mitigation: Production-style `ENVIRONMENT` values require a configured key.
- Recommendations: Ensure deployment checklists always set `DEVICE_INGEST_KEY` in staging/production; avoid exposing dev instances with empty key to untrusted networks.

**JWT refresh tokens are not revocable server-side:**
- Issue: Refresh tokens are stateless JWTs; compromise of a refresh token allows renewal until expiry without server invalidation.
- Files: `apps/api/src/api/v1/endpoints/auth.py`, `apps/api/src/api/v1/core/security.py`
- Current mitigation: Expiry (`REFRESH_TOKEN_EXPIRE_DAYS`) and rate limits on refresh/login endpoints.
- Recommendations: Add a refresh-token family/version store, logout-all, or rotation with reuse detection for higher assurance.

**CORS allowlist is hardcoded:**
- Issue: `CORSMiddleware` in `apps/api/src/main.py` lists fixed localhost origins only.
- Impact: A real production frontend on another origin will be blocked unless code is changed; conversely, wildcards are not used (good), but configurability is missing.
- Recommendations: Drive `allow_origins` from environment or `Settings` with safe defaults.

**Development error responses may leak internals:**
- Issue: Global exception handler returns exception type/message and optional traceback when `ENVIRONMENT` is development and `DEBUG` is true.
- Files: `apps/api/src/main.py`
- Current mitigation: Production branch returns a generic message.
- Recommendations: Keep `DEBUG` false in shared/staging environments; never enable traceback responses on internet-facing staging mirrors of prod data.

**Gate actuator URL:**
- Issue: `GATE_ACTUATOR_URL` is passed to `urlopen` without scheme allowlisting; misconfiguration could point at unexpected targets (operator-controlled, not end-user-controlled).
- Files: `apps/api/src/api/v1/controllers/gate_controller.py`, `apps/api/src/api/v1/core/config.py`
- Recommendations: Validate URL scheme (`http`/`https` only) and optionally pin host allowlist in configuration.

**Demo seed credentials in repository:**
- Issue: `apps/api/src/seed_demo.py` documents and creates `admin@siscav.com` / `admin123`.
- Impact: Risk if seed script or matching credentials are ever run against a reachable environment.
- Recommendations: Force password override via env for non-local use; document that demo credentials must not be used in production.

## Performance Bottlenecks

**Access log image upload reads entire body into memory:**
- Problem: `AccessLogController.create_access_log` uses `file.file.read()` up to `MAX_FILE_SIZE_MB`.
- Files: `apps/api/src/api/v1/controllers/access_log_controller.py`
- Cause: Single buffer allocation per request (acceptable within configured cap) but scales with concurrent large uploads.
- Improvement path: Stream to disk with a capped reader, or push uploads to object storage with presigned URLs.

**No lifecycle policy for local upload files:**
- Problem: Images are written under `UPLOAD_DIR` (`uploads` by default) with no retention or cleanup job in the API.
- Files: `apps/api/src/api/v1/controllers/access_log_controller.py`, `apps/api/src/api/v1/core/config.py`
- Cause: Disk usage grows with every ingest.
- Improvement path: Scheduled cleanup, quotas, or external object storage with lifecycle rules.

**Rate limiting keyed by IP only:**
- Problem: `slowapi` uses `get_remote_address` in `apps/api/src/api/v1/core/limiter.py`.
- Cause: Clients behind large NATs share one bucket; distributed attacks across IPs are less constrained per account.
- Improvement path: Combine IP limits with user-based limits where a token is present.

## Fragile Areas

**Database URL resolution and production safety:**
- Files: `apps/api/src/api/v1/core/config.py`, `apps/api/src/api/v1/db/session.py`
- Why fragile: Missing `DATABASE_URL` and `POSTGRES_*` falls back to SQLite (`sqlite:///./siscav_dev.db`). Production validation currently asserts `SECRET_KEY` via `assert_production_secrets_valid` in `apps/api/src/main.py` but does not forbid SQLite or warn on accidental dev DB.
- Safe modification: Add production checks that `database_url` is a Postgres URL when `ENVIRONMENT` is production.
- Test coverage: CI sets `DATABASE_URL: ""` and relies on fallback; behavior is covered indirectly but production misconfiguration is not asserted in tests.

**Alembic head vs. optional column `is_admin`:**
- Files: `apps/api/src/alembic/versions/20260404_0002_add_user_is_admin.py`, `apps/api/src/seed_demo.py`
- Why fragile: Deployments that stop at an older revision will lack `is_admin`, breaking admin-gated routes and seed assumptions.
- Safe modification: Run migrations to head before serving traffic; document revision `20260404_0002` as required for admin features.

**Authorization logic split across endpoints:**
- Files: `apps/api/src/api/v1/endpoints/*.py`, `apps/api/src/api/v1/deps.py`
- Why fragile: Easy to add a new route with `get_current_user` when `get_current_admin_user` was intended (already inconsistent for whitelist vs. gate/image).
- Safe modification: Centralize route policies (e.g. dependency factories or router-level defaults) and add integration tests per resource class.

## Scaling Limits

**Local filesystem for images:**
- Current capacity: Bounded by server disk and `MAX_FILE_SIZE_MB` per upload.
- Limit: Single-node storage and backup/HA become operational concerns at volume.
- Scaling path: S3-compatible storage, CDN for image delivery, and database keys instead of absolute paths in `image_storage_key`.

**Synchronous gate trigger:**
- Current capacity: One outbound HTTP call per request, worker-blocked for up to `GATE_ACTUATOR_TIMEOUT_SECONDS` (1–120s).
- Limit: Traffic spikes can exhaust worker pool if many concurrent triggers occur.
- Scaling path: Queue + worker, or async outbound notification with idempotency keys.

## Dependencies at Risk

**`python-jose` for JWT:**
- Risk: The library has had maintenance and security attention concerns in the ecosystem relative to alternatives.
- Impact: JWT parsing/verification bugs or lack of timely patches affect all auth.
- Migration plan: Evaluate `PyJWT` or `authlib` with equivalent algorithm support and regression tests in `tests/unit/test_core_security.py` and auth integration tests.

## Missing Critical Features

**No server-side audit trail for security-sensitive actions:**
- Problem: Gate trigger, whitelist changes, and admin image access are not persisted as an immutable audit log.
- Blocks: Forensics and compliance-style review of who changed access control or opened the gate.

**No automated refresh-token invalidation on password change or user delete:**
- Problem: Outstanding JWTs remain valid until expiry after credential rotation.
- Blocks: Immediate lockout semantics without additional infrastructure.

## Test Coverage Gaps

**Alembic migrations omitted from coverage configuration:**
- What's not measured: Revision files under `apps/api/src/alembic/versions/` are in `omit` in `pyproject.toml` `[tool.coverage.run]`.
- Files: `pyproject.toml`, migration modules
- Risk: Low for runtime logic; higher for undetected migration mistakes if not exercised by integration tests.
- Priority: Medium — add migration smoke tests (upgrade head against a throwaway DB) if schema drift becomes frequent.

**Production-only configuration paths:**
- What's not tested: `assert_production_secrets_valid` failure path and production CORS/origin configuration are not exercised in default CI.
- Files: `apps/api/src/main.py`, `apps/api/src/api/v1/core/config.py`
- Risk: Misconfigured production startup or blocked frontends discovered only at deploy time.
- Priority: Medium.

---

*Concerns audit: 2026-04-04*
