# Testing Patterns

**Analysis Date:** 2026-04-04

## Test Framework

**Runner:**
- **pytest** `9.0.2` (declared in `pyproject.toml` under `[project.optional-dependencies]` `dev`).
- Configuration: `[tool.pytest.ini_options]` in `pyproject.toml` (not a separate `pytest.ini`).

**Assertion library:**
- Plain `assert` statements (pytest style).

**Related tools:**
- **httpx** for async-capable HTTP client (listed as dev dependency; integration tests use Starlette/FastAPI `TestClient`).
- **pytest-cov** for coverage (`pyproject.toml` dev dependencies).

**Run commands (from repository root, with dev extras installed):**
```bash
pytest
pytest tests/unit/
pytest tests/integration/
pytest tests/test_main.py -v
pytest --cov=apps --cov-report=term-missing
```

`pyproject.toml` `[tool.pytest.ini_options]` sets `testpaths = ["tests"]`, discovers `test_*.py` / `*_test.py`, classes `Test*`, functions `test_*`, and includes `addopts`: `-ra`, `--strict-markers`, `--strict-config`, `--showlocals`.

## Test File Organization

**Location:**
- **Shared fixtures and app wiring:** `tests/conftest.py` (loaded automatically for tests under `tests/`).
- **Unit tests:** `tests/unit/` — controllers, repositories, `deps`, `core` config/security, utils.
- **Integration tests:** `tests/integration/` — HTTP flows against the full FastAPI app with overridden DB.
- **Top-level tests:** `tests/test_main.py`, `tests/test_access_logs.py`, `tests/test_auth_whitelist.py` (smoke/API checks without the `unit/` prefix).
- **Ad-hoc scripts:** `tests/manual/` (manual or debug helpers; not the main pytest suite).

**Naming:**
- Files: `test_<area>.py` or `test_<layer>_<feature>.py` (e.g. `test_controllers_auth.py`, `test_endpoints_gate_control.py`).
- Classes: `Test<Subject>` (e.g. `TestAuthEndpoints` in `tests/integration/test_endpoints_auth.py`).
- Methods: `test_<behavior>` with Portuguese or English docstrings describing the scenario.

**Structure (prescriptive for new tests):**
- Place fast, isolated logic tests under `tests/unit/`.
- Place multi-endpoint or middleware/rate-limit behavior under `tests/integration/`.
- Reuse `tests/conftest.py` fixtures when possible instead of duplicating DB setup.

## Test Structure

**Suite organization:**
```python
class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""

    def test_login_success(self, client: TestClient, test_user: User):
        response = client.post(...)
        assert response.status_code == 200
```

(Pattern from `tests/integration/test_endpoints_auth.py`.)

**Fixtures (`tests/conftest.py`):**
- Sets `os.environ` defaults for `DEVICE_INGEST_KEY` and `ENVIRONMENT` **before** importing the app (order matters).
- In-memory **SQLite** engine with `StaticPool` and `check_same_thread=False` for SQLAlchemy.
- `Base.metadata.create_all` at import time; `db_session` fixture **drops and recreates** tables per test for isolation.
- `app.dependency_overrides[get_db] = override_get_db` so all `TestClient` requests use the test engine.
- `client`, `test_user`, `admin_user`, `auth_token`, `admin_auth_token`, and autouse `_reset_login_rate_limiter` for SlowAPI.

**Patterns:**
- Prefer typed fixture parameters (`client: TestClient`, `db_session: Session`) where used.
- Import shared constants from `tests.conftest` when asserting login emails/passwords (`TEST_USER_EMAIL` in `test_endpoints_auth.py`).

## Mocking

**Framework:** standard library `unittest.mock` (`Mock`, `MagicMock`, `patch`) and pytest’s `monkeypatch`.

**Patterns:**

*Patch target is where the name is used:*
```python
@patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
def test_trigger_gate_live_upstream_2xx(self, mock_urlopen: MagicMock, client, admin_auth_token, monkeypatch):
    ...
```

(From `tests/integration/test_endpoints_gate_control.py`.)

*Environment isolation:*
```python
with patch.dict(os.environ, {"DATABASE_URL": "postgresql://..."}):
    result = _resolve_database_url()
```

(From `tests/unit/test_core_config.py`.)

*HTTPException assertions:*
```python
with pytest.raises(HTTPException) as exc_info:
    get_current_user(token=invalid_token, db=db_session)
assert exc_info.value.status_code == 403
```

(From `tests/unit/test_deps.py`.)

**What to mock:**
- External HTTP (`urlopen` on the gate controller module path).
- `os.environ` for settings resolution and feature flags.
- Settings cache: call `get_settings.cache_clear()` after changing env (`test_endpoints_gate_control.py`).

**What not to mock (typical unit tests in this repo):**
- Database when using `db_session` / local SQLite — use real sessions and ORM commits like `tests/unit/test_controllers_auth.py`.

## Fixtures and Factories

**Test data:**
- Users created inline with `User(...)` and `get_password_hash` from `apps.api.src.api.v1.core.security`, or via fixtures `test_user` / `admin_user` in `conftest.py`.

**Location:**
- Shared: `tests/conftest.py`.
- Test-local: small `db_session` / `test_user` fixtures duplicated in `tests/unit/test_deps.py` for isolation from global conftest overrides (pattern: own in-memory engine in the fixture).

## Coverage

**Configuration:**
- `[tool.coverage.run]` in `pyproject.toml`: `source = ["apps"]`, omits tests, venvs, and `alembic/versions`.
- `[tool.coverage.report]` excludes common non-counted lines (pragma, `TYPE_CHECKING`, etc.).

**Requirements:** No enforced CI threshold documented in these files; use `pytest-cov` locally for gaps.

**View coverage:**
```bash
pytest --cov=apps --cov-report=html
```

## Test Types

**Unit tests:**
- Controllers with real SQLAlchemy session against SQLite (`tests/unit/test_controllers_auth.py`).
- Repositories, utils, security, config resolution.

**Integration tests:**
- Full app + `TestClient` + overridden `get_db` (`tests/integration/*.py`).
- Rate limiting and auth headers exercised end-to-end.

**E2E:** Not a separate framework; closest is integration tests against running app semantics via `TestClient`.

## Common Patterns

**Async testing:** Not required for current tests; `TestClient` is synchronous.

**Markers:** Registered in `pyproject.toml` (`slow`, `integration`, `unit`, `smoke`). Usage is sparse; `tests/integration/test_endpoints.py` uses `@pytest.mark.usefixtures("test_user")`. When adding markers, register them in `pyproject.toml` to satisfy `--strict-markers`.

**Duplicate `TestClient` at module level:** `tests/test_main.py` constructs `client = TestClient(app)` at import time without `conftest` overrides — prefer `conftest`-based `client` fixture for tests that need the SQLite override and consistent env.

---

*Testing analysis: 2026-04-04*
