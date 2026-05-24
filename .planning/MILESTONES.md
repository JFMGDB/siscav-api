# Milestones

## v1.0 API brownfield hardening (shipped: 2026-04-05)

**Phases:** 4 (security/auth, whitelist + logs, gate + device honesty, operations hygiene)  
**Plans:** 11  
**Requirements v1:** 14/14 delivered

**Key accomplishments:**

1. **Security & auth:** ingest `POST /access_logs/` with `X-Device-Key` when configured; refresh token at `POST /api/v1/login/refresh-token`; block weak `SECRET_KEY` in production; `is_admin`, admin routes (image, gate) and aligned docs.
2. **Whitelist & audit:** normalized plate CRUD, multipart ingest with metadata persistence, filtered listing, image download admin-only.
3. **Gate & devices:** explicit simulated vs HTTP live gate response; demo device API with 501 when disabled and honest `demo` field.
4. **Operations:** removed dangerous session/SQLite shortcuts, pinned dependencies, removed duplicate `crud/` package.
5. **Quality:** pytest suite maintained green; Postman/docs aligned to real API.

## Phase 5: SonarQube CI (completed: 2026-05-03)

Static analysis and coverage reporting integrated into `.github/workflows/ci.yml`. Setup guide: `.github/SONAR_SETUP.md`.

---

*Detailed milestone audit files removed during cleanup; see git history for phase-level artifacts.*
