# Phase 2: Whitelist & access log behavior - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.  
> Decisions are captured in `02-CONTEXT.md`.

**Date:** 2026-04-04  
**Phase:** 2 — Whitelist & access log behavior  
**Mode:** User replied **`defaults`** — recommended options applied for all proposed gray areas (no per-area interactive picks).

**Areas recorded:** Audit list vs images, Image policy confirmation, Whitelist validation, List API contract

---

## Who may list access logs (LOG-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Any authenticated user | `get_current_user` on `GET /access_logs/` | ✓ |
| Admin-only list | Align list with image policy | |

**User's choice:** `defaults` → any authenticated user for list JSON  
**Notes:** Matches LOG-02; consistent with current `list_access_logs` dependency.

---

## Image access policy (LOG-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Admin-only image GET | Phase 1 `get_current_admin_user` on `/images/{filename}` | ✓ |
| Any authenticated user | Operators without `is_admin` could fetch bytes | |

**User's choice:** `defaults` → admin-only for raw images  
**Notes:** Phase 2 confirms Phase 1; document if docs drift.

---

## Whitelist validation (WL-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Strict BR formats + unique normalized | Current Pydantic / controller behavior | ✓ |
| Fuzzy / provisional entries | OCR-tolerance, non-standard plates | |

**User's choice:** `defaults` → strict validation, unique `normalized_plate`  
**Notes:** Defer fuzzy matching to a future phase.

---

## Access log list contract (LOG-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Freeze current query params | `skip`, `limit`, `plate`, `status`, `start_date`, `end_date`, newest-first | ✓ |
| Extend filters / export in Phase 2 | New scope | |

**User's choice:** `defaults` → freeze v1 contract; defer exports and extra filters  
**Notes:** Implementation already exposes `start_date`/`end_date`; Phase 2 verifies and documents.

---

## Claude's Discretion

- OpenAPI wording, timezone edge-case test depth (see `02-CONTEXT.md`).

## Deferred Ideas

- Non-admin image access; fuzzy whitelist; export and pagination enhancements; magic-byte validation (unless planning pulls it in).
