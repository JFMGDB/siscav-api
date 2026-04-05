# Phase 4: Operations & dependency hygiene - Context

**Gathered:** 2026-04-04  
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the repo **safe for shared and production-like use**: no accidental **debug/agent file I/O** or **silent SQLite `create_all`**, **reproducible installs** via pinned or lockfile-synced dependencies, and **no duplicate data-access path** via deprecated **`crud/`** (OPS-01, OPS-02, OPS-03).

Out of scope: new product features, auth redesign, gate hardware. **In scope:** `session.py` bootstrap, `requirements.txt` / `pyproject.toml` alignment, removal of dead `crud` package, documentation for operators/developers on migrations.

**Prior phases:** Phases 1–3 delivered security, audit honesty, gate/device honesty; Phase 4 does not change those behaviors except where debug/bootstrap code interferes with ops clarity.

</domain>

<decisions>
## Implementation Decisions

### OPS-01 — Debug instrumentation and SQLite discipline

- **D-01:** **Remove** the entire `#region agent log` block from **`apps/api/src/api/v1/db/session.py`** (JSON append to `debug-0c9557.log` and conditional **`Base.metadata.create_all`** on empty SQLite). Replace with **no side-effect** engine creation: `create_engine` + `sessionmaker` only. If transient diagnostics are needed later, use **`logging`** at DEBUG behind `LOG_LEVEL` — not ad hoc repo-root files.
- **D-02:** **Runtime app** must not call **`create_all`** for SQLite (or any DB) on import. **Canonical schema path:** **Alembic** (`alembic upgrade head`). **Tests** may keep **`Base.metadata.create_all`** in **`tests/conftest.py`** (or equivalent) — that is explicit test setup, not production bootstrap.
- **D-03:** Update **`docs/`** (e.g. `docs/installation.md`, `docs/setup_database_guide.md`, or **`README.md`** root if that is the install entry) with a short **“Primeiro arranque / SQLite local”** note: create DB file + run migrations; no reliance on implicit `create_all` at server start.
- **D-04:** **`config.py`:** Confirm no remaining agent-log regions (CONCERNS may still mention historical noise — align **`.planning/codebase/CONCERNS.md`** after edits).

### OPS-02 — Reproducible dependencies

- **D-05:** Pin **runtime** dependencies with **compatible `==` versions** in **`requirements.txt`** (used by Docker/CI/docs that reference it) **and** mirror the same constraint style in **`pyproject.toml`** `[project] dependencies` (either pins or narrow ranges — **prefer pins** matching one Python version in CI, e.g. 3.12/3.13 as documented).
- **D-06:** Pin **`[project.optional-dependencies] dev`** (pytest, ruff, etc.) the same way **or** add a dedicated **`requirements-dev.txt`** with pins — **Claude's discretion:** single source of truth minimal drift; if both files exist, document which CI uses (`pip install -r requirements.txt` vs `pip install -e ".[dev]"`).
- **D-07:** After pinning, run **`pytest`** (unit + integration) to confirm no import/API breakage. Document in **`docs/installation.md`** (or README) the install one-liner.

### OPS-03 — Deprecated `crud/` package

- **D-08:** **Delete** the package **`apps/api/src/api/v1/crud/`** (all `crud_*.py` files and **`__init__.py`** if present) after **`grep`** confirms **no** imports from `apps.api.src.api.v1.crud` in repo code (including tests). If any stray reference appears, redirect to **`repositories/`** / **`controllers/`** then delete.
- **D-09:** Remove **`crud`** from **architecture/docs** that list it as an active layer (search `docs/` and `.planning/codebase/` for “crud”).
- **D-10:** Update **`.planning/codebase/CONCERNS.md`** to remove or rewrite the “deprecated crud” tech-debt item as **resolved**.

### Claude's Discretion

- Exact version numbers (take from `pip freeze` in the execution environment or conservative known-good set).
- Whether to add **`uv.lock`** in a follow-up; Phase 4 minimum is **pinned `requirements.txt` + aligned `pyproject.toml`**.
- Optional: lower **`register`** rate limit (CONCERNS) — **defer** to a small sub-task only if trivial; otherwise **Deferred ideas**.

### Folded Todos

_None._

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning

- `.planning/ROADMAP.md` — Phase 4 goal, OPS-01–OPS-03.
- `.planning/REQUIREMENTS.md` — OPS-* acceptance text.
- `.planning/codebase/CONCERNS.md` — Current debt list (agent log, crud, unpinned deps).

### Code / config

- `apps/api/src/api/v1/db/session.py` — Engine/session (OPS-01).
- `apps/api/src/api/v1/core/config.py` — Settings (verify no debug regions).
- `apps/api/src/alembic/` — Migrations (canonical schema).
- `requirements.txt` — Runtime pins target.
- `pyproject.toml` — Project metadata + optional dev deps.
- `apps/api/src/api/v1/crud/` — Removal target (OPS-03).
- `tests/conftest.py` — Allowed `create_all` for tests.

### Docs

- `docs/installation.md`, `docs/setup_database_guide.md`, or root `README.md` — Install/migration narrative.

</canonical_refs>

<code_context>
## Existing Code Insights

- **`session.py`:** Lines 14–41 contain agent log + SQLite `create_all` — primary OPS-01 target.
- **`crud/`:** Three deprecated modules emitting `DeprecationWarning`; no application imports found in prior grep.
- **`requirements.txt`:** Unpinned list; **`pyproject.toml`** duplicates logical deps without pins.
- **Tests:** In-memory SQLite + `create_all` in `conftest` — keep; distinct from app `session.py`.

</code_context>

<specifics>
## Specific Ideas

- Prefer **delete** over long-lived deprecation shims for `crud/` (no known consumers).
- Pins should match what **CI** runs (check `.github` or local pytest workflow if present).

</specifics>

<deferred>
## Deferred Ideas

- **`uv.lock` / Poetry** adoption as primary lockfile.
- **Register rate limit** production value (CONCERNS) — security polish; not required for OPS-* closure.
- **Removing `#region` from other historical files** — only `session.py` confirmed in codebase grep.

### Reviewed Todos (not folded)

_None._

</deferred>

---

*Phase: 04-operations-dependency-hygiene*  
*Context gathered: 2026-04-04*
