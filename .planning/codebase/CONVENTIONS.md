# Coding Conventions

**Analysis Date:** 2026-04-10

## Naming Patterns

**Files:**
- Python modules: `snake_case.py` (e.g. `access_log_controller.py`, `user_repository.py`).
- Standalone script outside the package tree: `apps/api/src/api/v1/ml/recognize-plate.py` uses a hyphen (atypical; prefer `snake_case` for new modules).

**Functions:**
- `snake_case` for functions and methods (PEP 8; enforced by Ruff rule set `N` in `ruff.toml`).

**Variables:**
- `snake_case` for locals and module-level names.

**Types / classes:**
- `PascalCase` for classes: Pydantic schemas (`UserCreate`, `UserRead` in `apps/api/src/api/v1/schemas/user.py`), SQLAlchemy models (`User` in `apps/api/src/api/v1/models/user.py`), controllers, repositories.
- Enum-style values: Pydantic/schema enums follow the domain (e.g. `AccessStatus` in `apps/api/src/api/v1/schemas/access_log.py`).

**API routes:**
- Path segments use kebab-case or REST-style lowercase (e.g. `/api/v1/login/access-token` in `apps/api/src/api/v1/endpoints/auth.py`).

## Code Style

**Formatting:**
- **Ruff** formatter (`ruff format`) — configuration in `ruff.toml` `[format]`: double quotes, 4-space indent, Unix (`lf`) line endings, max line length **100** (same as `[tool.ruff]` / project standard).
- CI runs `ruff format --check .` (see `.github/workflows/ci.yml`).

**Linting:**
- **Ruff** linter (`ruff check`) with broad rule categories (`E`, `W`, `F`, `I`, `N`, `UP`, `B`, …) defined in `ruff.toml` `[lint] select`.
- **Ignored globally:** `E501` (line length handled by formatter), `B008` (FastAPI `Depends()` in defaults), `TRY003`, `PLR0913`.
- **Per-file:** `__init__.py` — `F401`, `F403`; `tests/**/*.py` — `T20` (print), `PLR2004` (magic numbers).
- **Excluded from lint:** Alembic migrations `alembic/versions/*.py` (see `ruff.toml` `exclude`).
- Cyclomatic complexity cap: **10** (`[lint.mccabe]` in `ruff.toml`).

**Static typing (editor/CI):**
- **Pyright** config: `pyrightconfig.json` — `include`: `apps`, Python **3.13**, `extraPaths`: `apps` for import resolution.

## Import Organization

**Order (enforced by Ruff isort rules, `I`):**
1. Future (if any)
2. Standard library
3. Third-party (FastAPI, SQLAlchemy, Pydantic, etc.)
4. First-party: package name **`apps`** (`known-first-party` in `ruff.toml`)
5. Local folder

**Path style:**
- Imports use the **`apps`** package root (e.g. `from apps.api.src.main import app` in tests, `from apps.api.src.api.v1.deps import get_current_user`).
- Prefer explicit imports over wildcards except where `__init__.py` re-exports are intentional (unused-import rules relaxed there).

## Error Handling

**HTTP API layer:**
- Use **`fastapi.HTTPException`** with `status` constants from `fastapi.status` where appropriate (e.g. `apps/api/src/api/v1/endpoints/auth.py`: `400` for bad credentials).
- Dependencies validate JWT and raise `HTTPException` with **403** for invalid token, **404** if user missing (`apps/api/src/api/v1/deps.py`).
- JWT decode failures: catch `JWTError` and Pydantic `ValidationError`, map to a single 403 response with detail `"Could not validate credentials"` (`apps/api/src/api/v1/deps.py`).

**Controllers:**
- Business rules signal errors via **`HTTPException`** (e.g. 404/400/409/413) — unit tests assert `pytest.raises(HTTPException)` and `exc_info.value.status_code` (see `tests/unit/test_controllers.py`, `tests/unit/test_deps.py`).

**Configuration:**
- Avoid raising in `Settings` construction for missing env; defaults are applied in `apps/api/src/api/v1/core/config.py` (e.g. `SECRET_KEY` default for dev).

## Logging

**Framework:** Python **`logging`** (not structlog).

**Patterns:**
- Module logger: `logger = logging.getLogger(__name__)` in controllers such as `apps/api/src/api/v1/controllers/auth_controller.py`, `plate_controller.py`, `device_controller.py`, `access_log_controller.py`.
- Levels: `debug` for verbose flow, `info` for success paths, `warning` for auth/plate validation issues, `error` with `exc_info=True` on unexpected failures (`plate_controller.py`).
- **Do not** use `print` in application code under Ruff `T20`; a legacy script `apps/api/src/api/v1/ml/recognize-plate.py` uses prints (excluded from typical API lint scope by location — new code should use logging).

## Comments

**When to comment:**
- Module docstrings at top of file are common and often in **Portuguese** (e.g. `apps/api/src/api/v1/deps.py`, `apps/api/src/api/v1/core/config.py`).
- Public FastAPI endpoints use docstrings describing args, returns, and raises (`apps/api/src/api/v1/endpoints/auth.py`).

**Docstrings:**
- Google-style narrative is used in several modules; keep endpoint and dependency docstrings aligned with actual behavior.

## Function Design

**Size:** McCabe complexity limited to **10** (`ruff.toml`); split large functions when the linter complains.

**Parameters:**
- FastAPI dependencies use **`typing.Annotated`** with `Depends()` (`apps/api/src/api/v1/deps.py`, `apps/api/src/api/v1/endpoints/auth.py`).

**Return values:**
- Endpoints declare `response_model` where applicable; controllers return ORM models or dicts consistent with schemas.

## Module Design

**Exports:**
- Package `__init__.py` files may re-export; Ruff allows unused imports there via per-file ignores (`ruff.toml`).

**Barrel files:**
- Endpoints are registered from `apps/api/src/api/v1/api.py`; prefer adding routers there when introducing new endpoint modules.

**Configuration access:**
- Use **`get_settings()`** from `apps/api/src/api/v1/core/config.py` (cached with `@lru_cache`). In tests that need fresh env, call **`get_settings.cache_clear()`** (`tests/unit/test_core_config.py`).

---

*Convention analysis: 2026-04-10*
