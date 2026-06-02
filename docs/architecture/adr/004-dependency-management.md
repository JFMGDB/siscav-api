# ADR 004: Dependency Management and Configuration

## Status

Accepted

## Context

The SISCAV API backend declared dependencies in multiple places:

- `pyproject.toml` (PEP 621 metadata and optional extras)
- `requirements.txt`, `requirements-dev.txt`, `requirements-ml.txt` (pip install paths used in docs and CI)
- `uv.lock` (optional lockfile for contributors who use uv locally)

Runtime, development, and ML/OCR stacks had overlapping definitions. `pyproject.toml` lacked `[build-system]`, so editable installs (`pip install -e ".[dev]"`) were unreliable. `pyrightconfig.json` targeted Python 3.12 while the project requires 3.13. `alembic.ini` still exposed a SQLite URL even though migrations resolve the database URL in `env.py` (see ADR 003).

## Decision

### Single source of truth

1. **`pyproject.toml`** is the authoritative declaration of direct dependencies:
   - `[project.dependencies]` — production / runtime
   - `[project.optional-dependencies] dev` — pytest, coverage, ruff, httpx
   - `[project.optional-dependencies] ml` — numpy, opencv-python-headless, easyocr (optional OCR/classification stack)

2. **`requirements.txt`**, **`requirements-dev.txt`**, and **`requirements-ml.txt`** support **pip** installs and **CI** (`pip install -r requirements-dev.txt`). When changing direct dependencies, update `pyproject.toml` **and** the matching `requirements*.txt` in the same change (no wrapper scripts in the repo).

3. **`uv.lock`** is **optional** — only for contributors who choose `uv sync` locally. CI does not use `uv` or `uv.lock`.

### CI (pip only)

GitHub Actions uses **Python 3.13** and:

```bash
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
pytest ...
```

No `uv` in the CI pipeline.

### Local development (document both paths)

Contributors may use **either** pip or uv. Documentation must show equivalent commands for install, lint, format, tests, migrations, and server.

| Task | pip / venv | uv |
|------|------------|-----|
| Install dev deps | `pip install -r requirements-dev.txt` | `uv sync --locked --extra dev` |
| Editable install | `pip install -e ".[dev]"` | (included in `uv sync`) |
| Lint | `ruff check .` | `uv run ruff check .` |
| Format check | `ruff format --check .` | `uv run ruff format --check .` |
| Tests | `pytest` | `uv run pytest` |
| Migrations | `alembic upgrade head` | `uv run alembic upgrade head` |
| Server | `uvicorn apps.api.src.main:app --reload` | `uv run uvicorn apps.api.src.main:app --reload` |
| ML optional | `pip install -r requirements-ml.txt` | `uv sync --extra ml` |

Set `PYTHONPATH=.` at the repository root when using plain `alembic` / `uvicorn` without `uv run`.

### Updating dependencies (maintainers)

1. Edit `[project.dependencies]` and/or `[project.optional-dependencies]` in `pyproject.toml`.
2. Update `requirements.txt` / `requirements-dev.txt` (and `requirements-ml.txt` if the `ml` extra changed) so CI and pip-only docs stay aligned.
3. Optionally run `uv lock` and commit `uv.lock` if your team uses uv locally — not required for CI.

Local install without touching `requirements*.txt` is fine for day-to-day work: `pip install -e ".[dev]"`.

### Version pinning policy

| Scope | Policy | Rationale |
|-------|--------|-----------|
| Runtime (`[project.dependencies]`) | Exact pins (`==`) in pyproject | Clear direct dependency contract |
| `requirements*.txt` | Pinned graph for pip/CI; updated alongside `pyproject.toml` | Reproducible `pip install -r` in Actions |
| Dev (`dev` extra) | Exact pins (`==`) | Stable CI and local tooling |
| ML (`ml` extra) | Minimum versions (`>=`) in pyproject; direct lines in `requirements-ml.txt` | Heavy transitive tree; full ML graph via `uv sync --extra ml` when needed |

ML dependencies are **not** installed in CI unless explicitly added later.

### Build and package layout

- `[build-system]` uses `setuptools` with package discovery for the `apps` namespace.
- Application imports remain `from apps.api.src...` with repository root on `PYTHONPATH` (or editable install).

### Tool configuration

- **pytest / coverage**: `[tool.pytest.ini_options]` and `[tool.coverage.*]` in `pyproject.toml`
- **ruff**: `ruff.toml` at repository root (intentionally separate)
- **pyright**: `pyrightconfig.json` aligned with Python 3.13 and repo-root import paths
- **alembic**: `alembic.ini` holds `script_location` and logging; `sqlalchemy.url` is a **placeholder** only — real URL from `get_migration_database_url()` in `apps/api/src/alembic/database_url.py`

## Consequences

- **CI** stays on pip + `requirements-dev.txt`; no uv dependency in Actions.
- **Docs** (`installation.md`, `README.md`, `commands.md`) describe pip and uv side by side for local work.
- Maintainers who change dependencies edit `pyproject.toml` and the corresponding `requirements*.txt` in one commit (optional `uv.lock` for uv users only).
- Closes **CFG-01** and **OPS-03** (pinned exported requirements for CI).

## References

- [pip install extras](https://pip.pypa.io/en/stable/cli/pip_install/)
- [uv projects and lockfiles](https://docs.astral.sh/uv/concepts/projects/) (optional local tool)
- [Alembic configuration](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- ADR 002 (optional ML dependencies)
- ADR 003 (Alembic URL resolution)
