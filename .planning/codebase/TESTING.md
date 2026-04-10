# Testing Patterns

**Analysis Date:** 2026-04-10

## Test Framework

**Runner:**
- **pytest** — configuration in `pyproject.toml` under `[tool.pytest.ini_options]` (not a separate `pytest.ini`).
- Discovery: `testpaths = ["tests"]`, files `test_*.py` / `*_test.py`, classes `Test*`, functions `test_*`.

**Assertion library:**
- Plain **`assert`** statements (pytest style).

**Run commands:**
```bash
pytest -v
pytest tests/unit/test_core_security.py -v
pytest --cov=apps --cov-report=term-missing
```

**CI (`.github/workflows/ci.yml`):**
- `DATABASE_URL: ""` is set so runtime can fall back appropriately for tests.
- Full suite: `pytest -v --cov=apps --cov-report=term-missing`.
- Lint gate: `ruff check --output-format=github .` and `ruff format --check .`.

**Dev dependencies:**
- Listed in `pyproject.toml` `[project.optional-dependencies] dev` and mirrored in `requirements-dev.txt`: `pytest`, `pytest-cov`, `ruff`, `httpx`.

## Test File Organization

**Location:**
- **Top-level** `tests/` for smoke/API flows: `tests/test_main.py`, `tests/test_auth_whitelist.py`, `tests/test_access_logs.py`.
- **Unit** tests under `tests/unit/`: `test_controllers.py`, `test_core_config.py`, `test_core_security.py`, `test_deps.py`, `test_repositories.py`, `tests/unit/test_utils_plate.py`.
- **Integration** tests under `tests/integration/`: `tests/integration/test_endpoints.py`.

**Naming:**
- Files: `test_<area>.py` or `test_<module>.py`.
- Test functions: `test_<behavior>`.
- Grouping: optional classes named `Test<Feature>` (e.g. `TestPasswordHashing` in `tests/unit/test_core_security.py`, `TestAuthEndpoints` in `tests/integration/test_endpoints.py`).

**Structure:**
```
tests/
├── __init__.py
├── test_main.py
├── test_access_logs.py
├── test_auth_whitelist.py
├── integration/
│   └── test_endpoints.py
└── unit/
    ├── test_controllers.py
    ├── test_core_config.py
    ├── test_core_security.py
    ├── test_deps.py
    ├── test_repositories.py
    └── test_utils_plate.py
```

## Test Structure

**Suite organization:**
```python
class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""

    def test_login_success(self, test_user):
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
```

**Patterns:**
- **Fixtures:** `@pytest.fixture` for in-memory DB sessions, users, tokens, `tmp_path` upload dirs (`tests/integration/test_endpoints.py`, `tests/unit/test_controllers.py`).
- **Module-level app setup:** Several modules override `get_db` on the **global** `app` and assign `app.dependency_overrides[get_db] = override_get_db` once at import time (`tests/integration/test_endpoints.py`, `tests/test_auth_whitelist.py`, `tests/test_access_logs.py`). **Implication:** importing multiple such modules in one process can conflict; run tests in isolation or refactor to session-scoped fixtures if flakiness appears.
- **Docstrings:** Portuguese descriptions on tests mirroring production docs.

**Pytest CLI defaults (`pyproject.toml`):**
- `-ra`, `--strict-markers`, `--strict-config`, `--showlocals` on failure.

**Markers (registered, rarely used in files):**
- `slow`, `integration`, `unit`, `smoke` — defined under `[tool.pytest.ini_options] markers` in `pyproject.toml`. **Current tests do not apply `@pytest.mark.*`**; to use markers, decorate tests and run with `-m integration` etc.

## Mocking

**Framework:** **`unittest.mock`** — `patch`, `Mock`, `MagicMock` as needed.

**Patterns:**
```python
from unittest.mock import patch

with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"}):
    url = _resolve_database_url()
    assert url == "postgresql://test:test@localhost/test"
```
(`tests/unit/test_core_config.py`)

```python
with patch(
    "apps.api.src.api.v1.controllers.access_log_controller.get_settings"
) as mock_settings:
    mock_settings.return_value.upload_dir = str(upload_dir)
    mock_settings.return_value.max_file_size_mb = 10
    controller = AccessLogController(db_session)
    log = controller.create_access_log(plate="ABC-1234", file=file)
```
(`tests/unit/test_controllers.py` — patch **where the name is used**, i.e. controller module’s reference to `get_settings`.)

**Dependency injection in tests:**
- `get_current_user` is tested by calling it **directly** with `token=` and `db=` (bypassing FastAPI `Depends`) in `tests/unit/test_deps.py`.

**What to mock:**
- Environment (`os.environ` via `patch.dict`).
- `get_settings` when filesystem or upload paths must be isolated (`tmp_path` + mocked settings).
- JWT encoding for expired-token cases (`jose.jwt.encode` in `tests/unit/test_deps.py`).

**What NOT to mock:**
- Prefer **real SQLite in-memory** sessions with `StaticPool` and `Base.metadata.create_all` for repositories and controllers when fast and deterministic (`tests/unit/test_repositories.py`, `tests/unit/test_controllers.py`).

## Fixtures and Factories

**Test data:**
- Users created with `User` model and `get_password_hash` from `apps.api.src.api.v1.core.security`.
- Plates via `AuthorizedPlateRepository.create` or Pydantic `AuthorizedPlateCreate` through controllers.

**Location:**
- Fixtures colocated in the same test module; no central `conftest.py` at `tests/` root in this repo.

**Settings cache:**
- When tests change env vars affecting `Settings`, call **`get_settings.cache_clear()`** before/after (`tests/unit/test_core_config.py`).

## Coverage

**Requirements:**
- **pytest-cov** with **`--cov=apps`** in CI (`.github/workflows/ci.yml`).
- `[tool.coverage.run]` in `pyproject.toml`: `source = ["apps"]`, omits tests, caches, venvs, Alembic versions.

**View coverage:**
```bash
pytest --cov=apps --cov-report=term-missing
pytest --cov=apps --cov-report=html
```

**Exclude lines** from coverage reports via `[tool.coverage.report] exclude_lines` in `pyproject.toml` (pragma, repr, abstract methods, `TYPE_CHECKING`, etc.).

## Test Types

**Unit tests:**
- Pure functions (`tests/unit/test_utils_plate.py`), security helpers (`tests/unit/test_core_security.py`), config resolution (`tests/unit/test_core_config.py`), repositories (`tests/unit/test_repositories.py`), controllers with SQLite (`tests/unit/test_controllers.py`), deps (`tests/unit/test_deps.py`).

**Integration tests:**
- **`fastapi.testclient.TestClient`** against full `app` from `apps/api.src.main` with DB override (`tests/integration/test_endpoints.py`).
- **`httpx`** is a declared dev dependency for Starlette/FastAPI test client compatibility.

**E2E tests:**
- Not present as separate Playwright/Cypress; closest is broad HTTP integration in `tests/integration/test_endpoints.py`.

## Common Patterns

**Async testing:**
- Endpoints under test are synchronous; `TestClient` calls are synchronous. **No** `pytest-asyncio` in current dependencies.

**Error testing:**
```python
with pytest.raises(HTTPException) as exc_info:
    get_current_user(token=invalid_token, db=db_session)
assert exc_info.value.status_code == 403
```
(`tests/unit/test_deps.py`)

**HTTP integration:**
```python
client = TestClient(app)
response = client.get("/api/v1/health")
assert response.status_code == 200
assert response.json() == {"status": "ok"}
```
(`tests/test_main.py`, `tests/integration/test_endpoints.py`)

---

*Testing analysis: 2026-04-10*
