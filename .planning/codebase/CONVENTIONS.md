# Coding Conventions

**Analysis Date:** 2026-04-04

## Naming Patterns

**Files:**
- Use `snake_case` for Python modules: `auth_controller.py`, `user_repository.py`, `access_log.py` under `apps/api/src/api/v1/`.
- Endpoints live in `apps/api/src/api/v1/endpoints/` with names like `auth.py`, `plate.py`.
- Tests mirror scope: `test_controllers_auth.py`, `test_endpoints_auth.py` under `tests/unit/` and `tests/integration/`.

**Classes:**
- `PascalCase` for domain and framework-facing types: `AuthController`, `UserRepository`, `User`, `Settings` (`apps/api/src/api/v1/controllers/auth_controller.py`, `apps/api/src/api/v1/repositories/user_repository.py`).

**Functions and variables:**
- `snake_case` for functions, methods, and locals (`authenticate`, `get_by_email`, `override_get_db` in `tests/conftest.py`).

**Types:**
- Prefer modern union syntax `X | None` where used (e.g. `UserRepository.get_by_id` in `apps/api/src/api/v1/repositories/user_repository.py`).
- FastAPI dependencies use `typing.Annotated` for injection (`apps/api/src/api/v1/deps.py`).

## Code Style

**Formatting and linting:**
- **Ruff** is the formatter and linter. Configuration lives in `ruff.toml` at the repository root.
- **Line length:** 100 characters (`ruff.toml`).
- **Target Python:** `py313` in `ruff.toml` (align local interpreters with project expectations).
- **Quotes:** double quotes for Ruff format (`quote-style = "double"` in `ruff.toml`).
- **Indentation:** 4 spaces; Unix line endings (`ruff.toml`).

**Lint rule families:**
- Broad selection including pycodestyle (`E`, `W`), pyflakes (`F`), isort (`I`), pep8-naming (`N`), pyupgrade (`UP`), bugbear (`B`), pytest-style (`PT`), and others listed in `ruff.toml`.
- **Ignored globally:** e.g. `E501` (formatter handles length), `B008` (FastAPI `Depends()` in defaults), `TRY003`, `PLR0913`.
- **Per-file:** `__init__.py` may ignore unused imports (`F401`, `F403`); `tests/**/*.py` ignores print and magic-number rules (`T20`, `PLR2004`).

**Import organization (Ruff isort):**
1. `future`
2. Standard library
3. Third-party (e.g. `pytest`, `fastapi`, `sqlalchemy`)
4. **First-party:** `apps` (`known-first-party = ["apps"]` in `ruff.toml`)
5. Local folder

**Prescriptive rule:** Run `ruff check` and `ruff format` from the repo root before committing; keep new code consistent with existing modules under `apps/api/src/api/v1/`.

## Architecture-Aligned Patterns

**Layering:**
- **Endpoints** (`apps/api/src/api/v1/endpoints/*.py`): HTTP wiring, `APIRouter`, `Depends`, map to controllers.
- **Controllers** (`apps/api/src/api/v1/controllers/*.py`): business orchestration, logging, raise `HTTPException` for API errors where appropriate.
- **Repositories** (`apps/api/src/api/v1/repositories/*.py`): data access; many methods are `@staticmethod` and take `db: Session` as first argument (`UserRepository` in `apps/api/src/api/v1/repositories/user_repository.py`).
- **Schemas** (`apps/api/src/api/v1/schemas/`): Pydantic v2 models for request/response.
- **Models** (`apps/api/src/api/v1/models/`): SQLAlchemy ORM entities.
- **Dependencies** (`apps/api/src/api/v1/deps.py`): shared `Depends()` callables and security helpers.

**Adding a feature:** add or extend repository methods, controller methods, endpoint routes, and Pydantic schemas in those folders; register routes via `apps/api/src/api/v1/api.py` (router inclusion).

## Error Handling

**API layer:**
- Use `fastapi.HTTPException` with `status` constants (e.g. `status.HTTP_409_CONFLICT`, `status.HTTP_401_UNAUTHORIZED`) in controllers and endpoints (`auth_controller.py`, `auth.py` in endpoints).
- JWT and validation errors are often caught and re-raised as `HTTPException` with `from error` to preserve chaining (`apps/api/src/api/v1/endpoints/auth.py`).
- Database issues: catch SQLAlchemy exceptions where handled explicitly in controllers (e.g. `IntegrityError`, `SQLAlchemyError` in `auth_controller.py`).

**Application shell:**
- Global handler for uncaught exceptions in `apps/api/src/main.py` logs and returns JSON responses; validation errors use FastAPI’s `RequestValidationError` handler where configured.

**Prescriptive rule:** Prefer explicit status codes and stable `detail` strings for client-facing errors; use logging (`logger = logging.getLogger(__name__)`) for operational context, not for leaking secrets.

## Logging

**Framework:** standard library `logging`.

**Patterns:**
- Module-level `logger = logging.getLogger(__name__)` in controllers and deps (`auth_controller.py`, `deps.py`).
- Use `debug` / `info` / `warning` for auth and security-relevant flows; avoid logging passwords or tokens.

## Comments and Docstrings

**When to document:**
- Module docstrings summarize purpose (Portuguese is common in this codebase, e.g. `apps/api/src/api/v1/endpoints/auth.py`).
- Public class and method docstrings often include `Args`, `Returns`, and `Raises` sections (`AuthController` in `auth_controller.py`).

**Prescriptive rule:** Match the language and structure of the nearest sibling module when adding new endpoints or controllers.

## Function Design

**Size:** Ruff mccabe `max-complexity = 10` (`ruff.toml`); keep branching shallow or extract helpers (see private helpers like `_create_token_pair` in `apps/api/src/api/v1/endpoints/auth.py`).

**Parameters:** Explicit typed parameters; session-first pattern on repositories (`db: Session`, ...).

**Return values:** ORM entities or Pydantic schemas from controllers to endpoints; `Optional` / `| None` for missing records.

## Module Design

**Exports:** No heavy use of barrel `__init__.py` re-exports required; import concrete modules from `apps.api.src...`.

**Settings:** Use `get_settings()` from `apps/api/src/api/v1/core/config.py` (cached); tests call `get_settings.cache_clear()` when env changes (`tests/integration/test_endpoints_gate_control.py`).

---

*Convention analysis: 2026-04-04*
