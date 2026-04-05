# Codebase Concerns

**Analysis Date:** 2026-04-04

## Tech Debt

**Debug / agent instrumentation (resolved in Phase 4):**
- Previously: ad hoc JSON append to `debug-0c9557.log` from `session.py` at engine init.
- **Status:** Removed from `apps/api/src/api/v1/db/session.py`. `config.py` had no remaining `#region agent log` in the tree at time of fix; use structured `logging` if new diagnostics are needed.

**SQLite bootstrap via `create_all` at import time (resolved in Phase 4):**
- Previously: `session.py` could call `Base.metadata.create_all` for empty SQLite DBs.
- **Status:** Removed. Schema is applied only via **Alembic** (`alembic upgrade head` from `apps/api`); see `docs/installation.md` and `docs/setup_database_guide.md` for SQLite primeiro arranque.

**Deprecated CRUD modules (removed in Phase 4):**
- **Status:** The `apps/api/src/api/v1/crud/` package was deleted after confirming no imports. Use **repositories** + **controllers** only.

**Unpinned runtime dependencies (resolved in Phase 4):**
- **Status:** Runtime and dev direct dependencies use `==` pins in `requirements.txt`, `requirements-dev.txt`, and `pyproject.toml`. CI installs via `pip install -r requirements-dev.txt` (Python 3.13 on GitHub Actions).

**Register rate limit marked temporary:**
- Issue: `register` uses `@limiter.limit("100/minute")` with comment "Temporariamente aumentado para testes".
- Files: `apps/api/src/api/v1/endpoints/auth.py`
- Impact: Open registration remains cheap to abuse at high volume compared to login’s `5/minute`.
- Fix approach: Lower the limit for production and keep a higher limit only under a test profile or env flag.

**IoT / gate / device integration (post Phase 3):**
- Current behavior: `GateController` returns `integration: "simulated"` when `GATE_ACTUATOR_URL` is unset, or performs HTTP POST to that URL and maps failures to 502/503. Device routes expose `demo: true` on responses when `IOT_DEVICE_DEMO_API` is enabled (default off in production → **501**).
- Files: `gate_controller.py`, `device` schemas/endpoints, `config.py`, `deps.py` (`verify_device_demo_api_enabled`).
- Remaining gap: no MQTT/WebSocket actuator channel; Bluetooth remains client-side (Web Bluetooth). See roadmap Phase 4+ for ops hygiene.

## Known Bugs / Documentation Mismatches

**“Administrador” vs any authenticated user:**
- Issue: Docstrings in `gate_control.py` and `access_logs.py` (image GET) describe administrator-only actions, but dependencies only use `get_current_user`. The `User` model has no role or `is_admin` field (`apps/api/src/api/v1/models/user.py`).
- Files: `apps/api/src/api/v1/endpoints/gate_control.py`, `apps/api/src/api/v1/endpoints/access_logs.py`, `apps/api/src/api/v1/models/user.py`
- Impact: Any logged-in user can trigger the gate endpoint and fetch stored images; docs overstate restrictions.
- Fix approach: Add roles or claims to JWT/User and enforce in dependencies, or correct the API documentation to match behavior.

## Security Considerations

**Unauthenticated creation of access logs:**
- Issue: `POST /api/v1/access_logs/` (`create_access_log`) does not depend on `get_current_user` or device credentials; it accepts multipart image + plate from the network.
- Files: `apps/api/src/api/v1/endpoints/access_logs.py`
- Impact: Spam, disk fill, and falsified access history unless the network layer restricts callers; inconsistent with authenticated list/image endpoints.
- Fix approach: Require API key, mutual TLS, or signed device tokens for ingestion; align with threat model for edge devices.

**Default JWT signing secret:**
- Issue: `Settings.secret_key` defaults to `"change_me_in_development"` when `SECRET_KEY` is unset.
- Files: `apps/api/src/api/v1/core/config.py`, `apps/api/src/api/v1/core/security.py`
- Impact: Deployments without env configuration accept forgeable tokens.
- Fix approach: Fail fast at startup if `SECRET_KEY` is missing or equals the default when `ENVIRONMENT=production` (or similar).

**Refresh token endpoint without the same brute-force limits as login:**
- Issue: `login_access_token` is limited to `5/minute`; `refresh_access_token` has no `@limiter.limit`.
- Files: `apps/api/src/api/v1/endpoints/auth.py`
- Impact: More room for refresh-token guessing or abuse if tokens leak (mitigated by JWT crypto, but rate limits still reduce noise and cost).
- Fix approach: Apply conservative rate limits to refresh as well.

**CORS allowlist fixed to local dev hosts:**
- Issue: `CORSMiddleware` in `main.py` only lists `localhost` / `127.0.0.1` ports 3000, 5173, 8000.
- Files: `apps/api/src/main.py`
- Impact: Production frontends on other origins are blocked unless code changes; conversely, widening without env config risks misconfiguration.
- Fix approach: Drive `allow_origins` from configuration (env list), separate dev vs prod defaults.

**Upload validation relies on client `Content-Type`:**
- Issue: `AccessLogController.create_access_log` rejects non-`image/*` types but does not verify magic bytes; extension comes from `file.filename`.
- Files: `apps/api/src/api/v1/controllers/access_log_controller.py`
- Impact: Mislabeled uploads or unexpected content could be stored if other checks are weak.
- Fix approach: Use `python-magic` or Pillow sniffing; sanitize extensions.

**Verbose error responses in development:**
- Issue: Global exception handler returns exception type and message when `ENVIRONMENT` is `development`, and traceback when `DEBUG=true`.
- Files: `apps/api/src/main.py`
- Impact: Information disclosure if dev-like settings leak to a shared/staging host.
- Fix approach: Tie detailed errors to an explicit `DEBUG` flag only on trusted machines; keep staging generic.

**User lookup logging may leak operational data:**
- Issue: On missing user, `get_current_user` logs total user count in the database.
- Files: `apps/api/src/api/v1/deps.py`
- Impact: Logs may reveal deployment size or aid correlation attacks.
- Fix approach: Log only a generic “user not found” without counts in production log levels.

## Performance Bottlenecks

**Loading full images into memory for GET:**
- Issue: `get_access_log_image` reads the entire file into a byte string before returning `Response`.
- Files: `apps/api/src/api/v1/endpoints/access_logs.py`
- Impact: Large images under concurrent admins increase memory use.
- Fix approach: Use `FileResponse` or streaming response for big files.

**Synchronous file I/O in request path:**
- Issue: `create_access_log` reads full upload into memory and writes synchronously.
- Files: `apps/api/src/api/v1/controllers/access_log_controller.py`
- Impact: Under high device throughput, event loop workers block unless running multiple workers.
- Fix approach: Background tasks or object storage with async clients where applicable.

## Fragile Areas

**Hard-coded path depth for debug log:**
- Issue: `parents[6]` from `config.py` / `session.py` assumes a fixed nesting depth to reach repo root.
- Files: `apps/api/src/api/v1/core/config.py`, `apps/api/src/api/v1/db/session.py`
- Impact: Moving `apps/api` layout breaks logging path silently (caught by `except Exception: pass`).
- Fix approach: Use a known project-root marker or standard logging directory from env.

**Settings loaded once via `lru_cache`:**
- Issue: `get_settings()` caches `Settings`; `database_url` is resolved at class field default time in `Settings`.
- Files: `apps/api/src/api/v1/core/config.py`
- Impact: Changing environment variables at runtime in the same process without clearing cache does not refresh settings (uncommon but surprising in tests or dynamic config).
- Fix approach: Document immutability after first access; provide test helpers to clear cache.

## Dependencies at Risk

**`python-jose`:**
- Risk: The ecosystem has historically had security advisories; unpinned `python-jose[cryptography]` in `requirements.txt` can pull vulnerable releases.
- Impact: JWT verification or algorithm handling could be affected on bad versions.
- Migration plan: Pin to a known-good version after `pip audit` / GitHub advisory review, or migrate to maintained libraries (e.g. `PyJWT`) with explicit algorithm allowlists.

## Missing Critical Features

**Physical gate control and real device integration:**
- Problem: No backend path from `POST /api/v1/gate_control/trigger` to hardware; devices API is demonstrative only.
- Blocks: Production gate automation and honest status reporting.

**Authorization model for sensitive operations:**
- Problem: No role-based enforcement despite product language implying admin-only gate and image access.
- Blocks: Multi-tenant or least-privilege deployments.

## Test Coverage Gaps

**Open ingest endpoint behavior:**
- What’s not tested: There are no negative tests for forged device traffic or API-key enforcement; current integration tests expect `POST /api/v1/access_logs/` to succeed **without** `Authorization` (see `test_create_access_log_authorized` / `test_create_access_log_denied` in `tests/integration/test_endpoints_access_logs.py`).
- Files: `tests/integration/test_endpoints_access_logs.py`, `apps/api/src/api/v1/endpoints/access_logs.py`
- Risk: The test suite codifies “public ingest”; tightening auth later requires coordinated device and test updates; abuse scenarios are not covered.
- Priority: High for production hardening.

**Refresh token rate limiting:**
- What’s not tested: Absence of limiter on refresh vs login.
- Files: `tests/integration/test_endpoints_auth.py`, `apps/api/src/api/v1/endpoints/auth.py`
- Risk: Operational abuse patterns differ from covered login tests.
- Priority: Medium.

---

*Concerns audit: 2026-04-04*
