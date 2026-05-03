---
title: "Phase 1 — Security foundations (six quick tasks)"
phase: 1
phase_slug: security-critical-foundations
requirements_addressed:
  - SEC-01
  - SEC-02
  - SEC-03
wave: 1
depends_on: []
files_modified:
  - apps/api/src/api/v1/core/config.py
  - apps/api/src/main.py
  - apps/api/src/api/v1/deps.py
  - apps/api/src/api/v1/endpoints/access_logs.py
  - apps/api/src/api/v1/controllers/access_log_controller.py
  - apps/api/src/api/v1/utils/image_validate.py
  - requirements.txt
  - env.local.example
  - tests/
autonomous: true
---

# Plan 01 — Security-critical foundations

**Intent:** Ship SEC-01, SEC-02, SEC-03 in **six tasks**, each designed to finish in **under 10 minutes** for a developer already set up on the repo (no long research, no broad refactors).

**Constraint (user):** Six tasks, each &lt; 10 minutes at first execution.

**Canonical refs:** `.planning/BUGS.md` (BUG-003, BUG-004, BUG-005), `.planning/ROADMAP.md` Phase 1 success criteria.

## must_haves (phase goal — backward verification)

1. With `DEBUG` not truthy and `SECRET_KEY` still `change_me_in_development`, the process **refuses to start** with a clear error mentioning `SECRET_KEY`.
2. `POST /api/v1/access_logs/` returns **401** (or 403) when the device credential header is missing or wrong.
3. A request with `Content-Type: image/jpeg` but **non-image bytes** is **rejected** before persisting a file under `upload_dir`.

## Verification (after all tasks)

- `pytest tests/ -q` passes (or targeted new tests pass).
- Manual: `curl` POST access_logs without header → 401; with correct header + tiny valid JPEG → 201/200 as today.

---

## Task 01 — SEC-01: `debug` flag + fail-fast default `SECRET_KEY` (~8 min)

<objective>
Prevent production-like runs from using the development default JWT secret unless `DEBUG` explicitly allows local work.
</objective>

<read_first>
- `apps/api/src/api/v1/core/config.py`
- `apps/api/src/main.py`
</read_first>

<action>
1. In `Settings` (`config.py`), add a boolean field **`debug`** resolved from env: true if `DEBUG` is set case-insensitively to one of `1`, `true`, `yes` (default false). Keep existing `secret_key` default string exactly **`change_me_in_development`** unchanged for dev.
2. In `main.py`, register a **lifespan** context manager (FastAPI `lifespan=` parameter). On startup, call `get_settings()` and if `settings.secret_key == "change_me_in_development"` **and** `not settings.debug`, raise **`RuntimeError`** with message containing both substrings **`SECRET_KEY`** and **`DEBUG`** so operators know the fix.
3. Remove any duplicate `FastAPI()` construction — use a single `app = FastAPI(..., lifespan=lifespan)`.
</action>

<acceptance_criteria>
- `grep -n "change_me_in_development" apps/api/src/api/v1/core/config.py` shows the default.
- `grep -n "lifespan" apps/api/src/main.py` matches the lifespan function.
- `grep -n "RuntimeError" apps/api/src/main.py` shows the fail-fast branch.
- Starting the app without `SECRET_KEY` and without `DEBUG=true` exits/fails at startup (document for manual check or add a tiny test in Task 06 that imports app with env patched).
</acceptance_criteria>

---

## Task 02 — SEC-02: `DEVICE_INGEST_API_KEY` in Settings + env template (~6 min)

<objective>
Add a single shared secret for IoT ingest, loaded from environment, default unset/empty.
</objective>

<read_first>
- `apps/api/src/api/v1/core/config.py`
- `env.local.example`
</read_first>

<action>
1. Add **`device_ingest_api_key: str`** to `Settings` with default `os.getenv("DEVICE_INGEST_API_KEY", "")` (empty string if unset).
2. Append to **`env.local.example`** a commented line documenting `DEVICE_INGEST_API_KEY=` for device POSTs to `/api/v1/access_logs/`, and note it is **required** for ingest outside local debug if you enforce it in Task 03.
</action>

<acceptance_criteria>
- `grep -n "device_ingest_api_key" apps/api/src/api/v1/core/config.py` finds the field.
- `grep -n "DEVICE_INGEST_API_KEY" env.local.example` finds documentation.
</acceptance_criteria>

---

## Task 03 — SEC-02: FastAPI dependency `verify_device_ingest_key` + wire POST (~9 min)

<objective>
Require header **`X-Device-Key`** on `create_access_log` matching `settings.device_ingest_api_key` when key is configured; allow relaxed behavior only when key is empty **and** `debug` is true (local dev).
</objective>

<read_first>
- `apps/api/src/api/v1/deps.py`
- `apps/api/src/api/v1/endpoints/access_logs.py`
</read_first>

<action>
1. In `deps.py`, add async or sync dependency **`verify_device_ingest`** (name as you prefer) that:
   - Reads header **`X-Device-Key`** (use `Header(..., alias="X-Device-Key")` or `Request.headers.get`).
   - If `settings.device_ingest_api_key` is **non-empty**: require header present and equal (string compare); else raise **`HTTPException(status.HTTP_401_UNAUTHORIZED)`** with detail mentioning device key.
   - If `settings.device_ingest_api_key` is **empty** and `settings.debug` is **true**: allow (local dev without key).
   - If **empty** and **not** `debug`: raise **401** (forces explicit key in staging/prod).
2. Add `Depends(verify_device_ingest)` to **`create_access_log`** in `access_logs.py` only (not list/get image routes).
3. Document the header in the route docstring.
</action>

<acceptance_criteria>
- `grep -n "X-Device-Key\|verify_device" apps/api/src/api/v1/deps.py apps/api/src/api/v1/endpoints/access_logs.py` shows wiring.
- With `DEVICE_INGEST_API_KEY=secret` and `DEBUG=false`, POST without header returns 401 (covered in Task 06 or manual).
</acceptance_criteria>

---

## Task 04 — SEC-03: Add `Pillow` + `image_validate.py` helper (~8 min)

<objective>
Decode bytes as a real raster image using Pillow; keep dependency minimal (one line in requirements).
</objective>

<read_first>
- `requirements.txt`
- `apps/api/src/api/v1/utils/plate.py` (style reference only)
</read_first>

<action>
1. Add **`pillow`** to `requirements.txt` (alphabetically or after existing deps — one line).
2. Create **`apps/api/src/api/v1/utils/image_validate.py`** with function **`assert_image_bytes(content: bytes) -> None`** that:
   - Opens `BytesIO(content)` with `PIL.Image.open`, calls `.verify()` (or load and verify) to ensure it is a valid image.
   - Raises **`ValueError`** with message containing **`not a valid image`** on failure.
3. Do **not** import PIL at module import time in a way that breaks if unused — importing inside function is OK.
</action>

<acceptance_criteria>
- `grep -n "^pillow" requirements.txt` matches.
- `image_validate.py` contains `def assert_image_bytes` and `PIL` or `Image`.
</acceptance_criteria>

---

## Task 05 — SEC-03: Call validator in `AccessLogController.create_access_log` (~7 min)

<objective>
Reject spoofed `Content-Type` before writing to disk.
</objective>

<read_first>
- `apps/api/src/api/v1/controllers/access_log_controller.py`
- `apps/api/src/api/v1/utils/image_validate.py`
</read_first>

<action>
1. After reading **`file_content`** and **after** size check (keep order: type hint from `content_type` can stay first, then read, size, then **assert_image_bytes(file_content)**), call **`assert_image_bytes(file_content)`**.
2. On **`ValueError`**, raise **`HTTPException(status.HTTP_400_BAD_REQUEST, detail=...)`** with detail containing **`image`**.
3. Only write to disk **after** validation passes.
</action>

<acceptance_criteria>
- `grep -n "assert_image_bytes" apps/api/src/api/v1/controllers/access_log_controller.py` matches.
- Invalid bytes path returns 400, not 201.
</acceptance_criteria>

---

## Task 06 — Tests: startup secret, device key, fake image (~10 min)

<objective>
Automate acceptance for Tasks 01–05 without full manual QA.
</objective>

<read_first>
- `tests/conftest.py` if present; else `tests/test_access_logs.py`
- `tests/integration/test_endpoints.py` (patterns)
</read_first>

<action>
1. Add tests (new file or extend existing) using **`httpx.AsyncClient` + `app` fixture** or **`TestClient`**, with **`monkeypatch`** / env overrides:
   - **Startup:** With `DEBUG=false`, `SECRET_KEY=change_me_in_development`, importing/creating app should fail OR lifespan should raise — pick one pattern consistent with Starlette test client (may need `lifespan` context when using newer FastAPI).
   - **Device key:** With `DEVICE_INGEST_API_KEY=testkey`, `DEBUG=false`, POST `/api/v1/access_logs/` without `X-Device-Key` → **401**.
   - **Image:** With valid key header, upload a tiny **valid** JPEG bytes vs **invalid** bytes (e.g. `b"not an image"`) with `Content-Type: image/jpeg` → invalid returns **400**.
2. Keep tests fast; mock DB only if existing tests do — follow repo patterns.
</action>

<acceptance_criteria>
- `pytest` on the new/modified test file exits **0**.
- At least three new test functions covering the three bullets above.
</acceptance_criteria>

---

## PLANNING COMPLETE

- **Plans:** 1 file (`01-PLAN.md`)
- **Tasks:** 6 (each scoped for &lt;10 min)
- **Waves:** Single wave; run tasks **01 → 06** in order
