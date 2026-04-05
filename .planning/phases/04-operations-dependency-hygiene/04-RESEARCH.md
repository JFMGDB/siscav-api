# Phase 4: Operations & dependency hygiene — Research

**Date:** 2026-04-04  
**Status:** Complete

## RESEARCH COMPLETE

### Findings (for planning)

1. **`session.py` (OPS-01)**  
   - Lines 14–41: `#region agent log` performs SQLite introspection, conditional `Base.metadata.create_all(bind=engine)`, and appends JSON to repo-root `debug-0c9557.log` via `Path(__file__).resolve().parents[6]`.  
   - Imports `text` from SQLAlchemy only for that block; `import os` only for the log payload. After removal, drop unused imports.  
   - Production path must be: `create_engine` + `sessionmaker` only; schema via **`alembic upgrade head`**.

2. **`config.py`**  
   - Current tree has **no** `#region agent log` in `apps/api/src/api/v1/core/config.py`. **`.planning/codebase/CONCERNS.md` is stale** listing config — plans should correct CONCERNS to match reality.

3. **Tests**  
   - `tests/conftest.py` uses in-memory SQLite and `Base.metadata.create_all(bind=engine)` on a **separate** test engine — this is acceptable per CONTEXT; do not remove.

4. **Dependencies (OPS-02)**  
   - CI (`.github/workflows/ci.yml`) uses **Python 3.13**, `pip install -r requirements-dev.txt`, which includes `-r requirements.txt`.  
   - Pin **direct** runtime deps in `requirements.txt` and mirror in `pyproject.toml` `[project] dependencies`.  
   - Pin dev tools in `requirements-dev.txt` (after `-r requirements.txt`).  
   - Versions verified from local `pip freeze` after install (2026-04-04): see PLAN 04-02 frontmatter / tasks.

5. **`crud/` (OPS-03)**  
   - Directory contains only `crud_user.py`, `crud_access_log.py`, `crud_authorized_plate.py` (no `__init__.py` in listing).  
   - Repo-wide grep: **no** `api.v1.crud` imports in `.py` files.  
   - Docs still reference `crud/` in `.planning/codebase/STRUCTURE.md`, `ARCHITECTURE.md`, `docs/development/coding-standards.md`, and historical project-management docs — update or remove examples.

6. **Docs gap**  
   - `docs/installation.md` “Opção C: SQLite” implies automatic setup; after removing `create_all`, operators need explicit **create DB file (if file-based SQLite) + `alembic upgrade head`** on first run.

### Validation architecture

Nyquist validation is **disabled** for this project (`nyquist_validation_enabled: false`); no `VALIDATION.md` for Phase 4.
