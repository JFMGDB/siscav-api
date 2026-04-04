# Coding Conventions

**Analysis Date:** 2026-04-04

## Naming Patterns

**Files:**
- Application modules use `snake_case`: `auth_controller.py`, `user_repository.py`, `access_log.py`.
- Test modules mirror the area under test: `test_controllers_auth.py`, `test_endpoints_whitelist.py`, `test_repositories_user.py`.
- Single-word domain files: `deps.py`, `session.py`, `main.py`.

**Functions:**
- Use `snake_case` for functions and methods (`get_current_user`, `authenticate`, `create_access_log`).
- FastAPI route handlers and dependency callables follow the same rule.

**Classes:**
- Use `PascalCase` for controllers, repositories, Pydantic models, and SQLAlchemy models: `AuthController`, `UserRepository`, `UserCreate`, `User`.

**Variables:**
- `snake_case` for locals and parameters; type hints are used consistently in newer code (`Annotated`, `Optional`, `UUID`).

**Types:**
- Pydantic schemas group related DTOs with suffixes: `UserBase`, `UserCreate`, `UserRead` in `apps/api/src/api/v1/schemas/user.py`.
- Enums use PascalCase member names where used (e.g. `AccessStatus` in access-log flows).

## Code Style

**Formatting:**
- **Ruff** is the formatter and linter; config lives in `ruff.toml`.
- Line length target: **100** characters (`line-length = 100`); `E501` is ignored in lint because the formatter handles wrapping.
- **Double quotes**, **4 spaces**, **LF** line endings (`quote-style`, `indent-style`, `line-ending` in `ruff.toml`).
- Target Python: **py313** in Ruff; runtime docs in `apps/api/src/main.py` still mention Python 3.10+—align documentation with the toolchain you actually use.

**Linting:**
- Broad rule selection: pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, bugbear, pytest-style, tryceratops, etc. (`ruff.toml` `[lint] select`).
- Ignored globally: `B008` (FastAPI `Depends()` patterns), `TRY003`, `PLR0913`.
- Per-file: `__init__.py` allows unused imports (`F401`, `F403`); `tests/**/*.py` allows print and magic numbers (`T20`, `PLR2004`).
- **isort** first-party package: `apps` (`known-first-party` in `ruff.toml`).

## Import Organization

**Order:**
1. Future (if any)
2. Standard library
3. Third-party (`fastapi`, `sqlalchemy`, `pydantic`, `pytest`, etc.)
4. First-party: `apps.api.src...`
5. Local / test imports: e.g. `from tests.conftest import ...`

**Path style:**
- Application code imports from the `apps.api.src` package root, not relative paths between v1 modules in the samples checked (e.g. `from apps.api.src.api.v1.deps import ...` in tests).

**Path aliases:**
- No TypeScript-style aliases; Python package layout is the source of truth (`apps` as installable layout / `PYTHONPATH`).

## Error Handling

**Patterns:**
- **HTTP layer:** `HTTPException` with `status` from `fastapi.status` for client and auth errors (`apps/api/src/api/v1/deps.py`).
- **JWT / validation:** Catch `JWTError` and `ValidationError`, log with `logger.warning`, then raise `HTTPException` (403) without leaking internals (`deps.py`).
- **Controllers:** Business paths may return `None` (e.g. failed auth in `AuthController.authenticate`); operations that violate rules raise `HTTPException` (see `PlateController` tests in `tests/unit/test_controllers.py`).
- **Database:** `IntegrityError` / `SQLAlchemyError` handled in controllers where registration and persistence matter (`auth_controller.py`).
- **Global unhandled errors:** `global_exception_handler` on `app` in `apps/api/src/main.py` logs with `exc_info=True` and returns safe JSON; development mode can expose more detail via `ENVIRONMENT` / `DEBUG`.

**Prescriptive guidance for new code:**
- Prefer raising `HTTPException` at the boundary (deps, controllers) rather than returning error strings.
- Log failures with `logging.getLogger(__name__)`; include minimal context (no passwords or tokens).

## Logging

**Framework:** Standard library `logging`.

**Patterns:**
- Module logger: `logger = logging.getLogger(__name__)` (`deps.py`, `auth_controller.py`, `main.py`).
- Levels: `debug` for routine flow, `warning` for auth failures and invalid tokens, `error` for unhandled exceptions with `exc_info=True` in the global handler.

## Comments and Docstrings

**When to comment:**
- Module docstrings describe purpose in Portuguese (e.g. `deps.py`, test modules).
- Public dependency and controller methods use Google-style sections (`Args`, `Returns`, `Raises`) where documented (`deps.py`, `auth_controller.py`).

**Prescriptive guidance:**
- Match the language of the surrounding module (Portuguese is dominant in docstrings and descriptions).
- Do not add redundant comments on obvious lines; Ruff `ERA` (eradicate) discourages commented-out code.

## Function Design

**Size:** Ruff mccabe `max-complexity = 10` (`ruff.toml`).

**Parameters:**
- FastAPI dependencies use `Annotated[..., Depends(...)]` for injection (`deps.py`).

**Return values:**
- Controllers return domain objects or Pydantic read models; optional flows return `Optional[User]` etc.

## Module Design

**Exports:**
- No heavy use of barrel `__init__.py` re-exports observed; import concrete modules.

**Layering:**
- **Endpoints** → **controllers** → **repositories** (static-style repository classes referenced from controllers) → **models** / **schemas**.
- Shared wiring in `apps/api/src/api/v1/deps.py` and `apps/api/src/api/v1/db/session.py`.

---

*Convention analysis: 2026-04-04*
