# Phase 4: Operations & dependency hygiene - Discussion Log

> **Audit trail only.** Decisions are in `04-CONTEXT.md`.

**Date:** 2026-04-04  
**Phase:** 4 — Operations & dependency hygiene  
**Mode:** Builder defaults applied in one pass (no interactive gray-area multi-select). Revise `04-CONTEXT.md` before `/gsd-plan-phase 4` if you want different locks (e.g. keep env-gated `create_all` for DX).

**Areas considered**

1. **Agent log / SQLite bootstrap** — Default: **remove** block from `session.py`; app uses **Alembic** only; tests keep explicit `create_all`.
2. **Dependency pinning** — Default: **`==` pins** in `requirements.txt` **and** aligned `pyproject.toml`; optional `requirements-dev.txt`.
3. **`crud/` package** — Default: **delete** after import grep; update CONCERNS/docs.

## Deferred

- `uv.lock` as primary artifact  
- Register rate limit tweak  
