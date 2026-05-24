# Roadmap: SISCAV API

## Milestones

- **v1.0 — API brownfield hardening** (shipped 2026-04-05) — Phases 1–4: security/auth, whitelist + logs, gate + device honesty, operations hygiene. 11 plans delivered. See [MILESTONES.md](MILESTONES.md).

## Completed work (summary)

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Security & authentication correctness | Done |
| 2 | Whitelist & access-log behavior | Done |
| 3 | Gate & device integration honesty | Done |
| 4 | Operations & dependency hygiene | Done |
| 5 | SonarQube static analysis in CI | Done (2026-05-03) |

Detailed phase plans and verification reports were removed during codebase cleanup; history is in git.

## Backlog

### Phase 999.1: Camera Wi-Fi/USB live preview (BACKLOG)

**Goal:** Operator UI connects camera via Wi-Fi or USB and shows live preview. Delivery is in a separate frontend repository (Next.js); this API repo provides auth and OCR endpoints only.

**Status:** Documented in `docs/api/frontend-integration.md`. No API-side streaming endpoints required.

### v1.1+ (TBD)

Use `/gsd-new-milestone` to define the next structured cycle. Open items tracked in [REQUIREMENTS.md](REQUIREMENTS.md) and [BUGS.md](BUGS.md).

---

*Last updated: 2026-05-24*
