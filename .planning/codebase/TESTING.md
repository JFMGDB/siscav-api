# Testing Patterns

**Analysis Date:** 2026-04-04

## Test Framework

**Runner:**
- **pytest** (declared in `pyproject.toml` optional `dev` deps and `requirements-dev.txt`).
- Config: `[tool.pytest.ini_options]` in `pyproject.toml` (not a separate `pytest.ini`).

**Assertion library:**
- Plain `assert` statements (pytest style).

**Run commands:**
```bash
pytest                           # All tests under tests/ (testpaths)
pytest tests/unit                 # Unit tests only
pytest tests/integration          # Integration tests only
pytest tests/unit/test_controllers_auth.py -v
pytest --cov=apps --cov-report=term-missing   # Coverage (pytest-cov + pyproject coverage settings)
```

## Test File Organization

**Location:**
- **Unit:** `tests/unit/` with one file per area: `test_controllers_*.py`, `test_repositories_*.py`, `test_core_*.py`, `test_deps.py`, `test_utils_plate.py`.
- **Integration:** `tests/integration/` with `test_endpoints*.py` grouped by domain (auth, devices, gate, whitelist, access logs).
- **Top-level:** `tests/test_main.py`, `tests/test_access_logs.py`, `tests/test_auth_whitelist.py` (smoke-style API checks).
- **Scripts / manual:** `tests/scripts/` (`test_server_context.py`, `test_auth_flow.py`, `test_register.py`)—treat as auxiliary, not the main suite.

**Naming:**
- Files: `test_*.py` or `*_test.py` (configured in `pyproject.toml`).
- Classes: `Test*` (e.g. `TestAuthEndpoints`, `TestAuthController`).
- Functions: `test_*`.

**Structure:**
```
tests/
├── conftest.py              # Shared integration fixtures + app DB override
├── test_main.py
├── integration/
│   ├── test_endpoints.py    # Large module with its own SQLite override + client
│   └── test_endpoints_*.py
├── unit/
│   └── test_*.py
└── scripts/
```

## Test Structure

**Suite organization:**
- Prefer **classes** grouping related cases: `class TestAuthEndpoints`, `class TestGetCurrentUser`, `class TestPlateController`.
- Docstrings on classes and tests in Portuguese, mirroring app docs.

**Patterns:**
- **Setup:** Pytest fixtures (`@pytest.fixture`) for `client`, `db_session`, `test_user`, `auth_token` in `tests/conftest.py`.
- **Teardown:** `yield` fixtures close DB sessions; integration `conftest` registers `app.dependency_overrides[get_db]`.
- **Assertions:** Status codes and JSON keys for HTTP; `pytest.raises(HTTPException)` for expected API-layer errors in unit tests.

**Example (integration HTTP):**
```python
# tests/integration/test_endpoints_auth.py
response = client.post(
    "/api/v1/login/access-token",
    data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
)
assert response.status_code == 200
assert "access_token" in response.json()
```

**Example (unit dependency):**
```python
# tests/unit/test_deps.py
with pytest.raises(HTTPException) as exc_info:
    get_current_user(token=invalid_token, db=db_session)
assert exc_info.value.status_code == 403
```

## Mocking

**Framework:** `unittest.mock` (`patch`, `Mock`, `MagicMock`) and pytest **`monkeypatch`**.

**Patterns:**
- **Environment:** `patch.dict(os.environ, {...})` in `tests/unit/test_core_config.py` to exercise `get_settings()` / `DATABASE_URL` behavior without real secrets.
- **Patch target:** Patch where the name is **used**, not where it is defined—e.g. `patch("apps.api.src.api.v1.controllers.access_log_controller.get_settings")` in `tests/unit/test_controllers.py` so `AccessLogController` sees mocked upload settings and temp dirs via `tmp_path`.
- **Settings mutation:** `monkeypatch.setattr(settings, "max_file_size_mb", 1)` in `tests/unit/test_controllers_access_log.py` for size limits.

**What to mock:**
- `get_settings` when tests need isolated filesystem paths or limits.
- OS environment for configuration unit tests.

**What NOT to mock (typical in this repo):**
- Integration tests use real `TestClient` against the full `app` with SQLite in memory and dependency overrides (`tests/conftest.py`, `tests/integration/test_endpoints.py`).
- Many unit tests use a **real in-memory SQLite** session with `Base.metadata.create_all` rather than mocking SQLAlchemy.

## Fixtures and Factories

**Test data:**
- Shared constants: `TEST_USER_EMAIL`, `TEST_USER_PASSWORD` in `tests/conftest.py`.
- Per-file fixtures duplicate `db_session` + `sample_user` / `test_user` in several unit files (`test_controllers.py`, `test_deps.py`) instead of only using `conftest.py`—when adding tests, prefer extending `conftest.py` to avoid drift.

**Location:**
- Primary shared fixtures: `tests/conftest.py`.
- Local `@pytest.fixture` in heavy unit modules when isolation from global app override is required.

## Coverage

**Requirements:** No enforced percentage in CI documented in-repo from this audit; tooling is configured.

**Configuration:**
- `[tool.coverage.run]` in `pyproject.toml`: `source = ["apps"]`, omits tests, venvs, and `alembic/versions`.
- `[tool.coverage.report]` excludes standard boilerplate lines (pragma, `TYPE_CHECKING`, etc.).

**View coverage:**
```bash
pytest --cov=apps --cov-report=html
```

## Test Types

**Unit tests:**
- Controllers, repositories, `deps`, security, config, utils; heavy use of SQLite `:memory:` + `StaticPool` (`tests/unit/test_controllers.py`, `test_deps.py`).

**Integration tests:**
- HTTP API via `TestClient`; authentication headers `Authorization: Bearer {token}`; OAuth2 form login for token endpoint (`tests/integration/test_endpoints_auth.py`).

**E2E tests:**
- Not a separate Playwright/Cypress stack; "integration" here means in-process FastAPI + DB.

## Markers

**Registered in `pyproject.toml`:** `slow`, `integration`, `unit`, `smoke` with `--strict-markers`.

**Current usage:** No `@pytest.mark.integration` (or other markers) found under `tests/` via search—tests are not categorized by marker yet. **Prescriptive:** Add `@pytest.mark.integration` to files under `tests/integration/` and `@pytest.mark.unit` to `tests/unit/` when you need selective runs (`pytest -m integration`).

## Common Patterns

**Async testing:**
- Not prominent; app handlers may be async but tests call synchronous `TestClient` methods.

**Error testing:**
- `pytest.raises(HTTPException)` + `exc_info.value.status_code` for expected failures (`test_controllers.py`, `test_deps.py`).

**File uploads in tests:**
- `starlette.datastructures.UploadFile` with `BytesIO` payload (`tests/unit/test_controllers.py`).

---

*Testing analysis: 2026-04-04*
