# Phase 5 — Technical research: SonarQube / SonarCloud + GitHub Actions (Python)

**Date:** 2026-05-03  
**Question:** What do we need to know to plan Sonar integration for this repo?

## RESEARCH COMPLETE

### Stack facts (this repo)

- **CI:** `.github/workflows/ci.yml` — Python 3.13, `pip install -r requirements-dev.txt`, **ruff**, **pytest** with `pytest -v --cov=apps --cov-report=term-missing`.
- **Code layout:** Application under `apps/` (API in `apps/api/src/`), tests under `tests/`.
- **Coverage today:** terminal only; **no XML** for external tools until we add `--cov-report=xml:coverage.xml` (or equivalent path).

### Recommended integration path

| Topic | Recommendation | Rationale |
|-------|----------------|-----------|
| **Hosting** | **SonarCloud** for GitHub-hosted OSS/small teams | No server ops; GitHub OAuth; free tier for public repos. Self-hosted **SonarQube** documented as alternate (`SONAR_HOST_URL` pointing to internal instance). |
| **GitHub Action** | **`SonarSource/sonarqube-scan-action@v5`** | Current Sonar direction for CI; works for **both** SonarCloud and SonarQube Server via `SONAR_HOST_URL` + `SONAR_TOKEN`. Older `sonarcloud-github-action` is legacy. |
| **Auth in CI** | `SONAR_TOKEN` (repo **Secret**); `SONAR_HOST_URL` = `https://sonarcloud.io` for cloud (Secret or literal in workflow — literal is public knowledge) | Matches official docs; never commit raw tokens. |
| **Scanner config** | Root **`sonar-project.properties`** | `sonar.projectKey`, `sonar.organization` (SonarCloud), `sonar.sources`, `sonar.tests`, `sonar.python.version=3.13`, `sonar.python.coverage.reportPaths=coverage.xml`, sensible `sonar.exclusions` (Alembic generated migrations, `__pycache__`, venv if ever scanned). |
| **Coverage** | Add **`--cov-report=xml:coverage.xml`** to pytest in CI before scan | Sonar Python analyzer consumes Cobertura XML; path must match `sonar.python.coverage.reportPaths`. |
| **Quality gate vs CI** | **Initial rollout:** omit `sonar.qualitygate.wait=true` (or equivalent) so the first analyses do not block merges while the project is onboarded; **document** toggling `qualitygate.wait` when the team is ready | Matches phase CONTEXT (“conservador no dia 1”); SONAR-03 satisfied via documented policy. |
| **PR decoration** | Optional: workflow `permissions` may need `pull-requests: read` or `write` per SonarCloud doc for decoration | Add when enabling PR analysis; start minimal (`contents: read`) if only branch analysis. |
| **Fork PRs** | Secrets are unavailable on forks; expect scan skip or use documented limitations | Call out in operator doc. |

### Pitfalls

1. **Wrong project key / org** — analysis uploads to wrong project or fails; keys must match SonarCloud project setup exactly.
2. **Coverage path mismatch** — `coverage.xml` not at repo root or not generated before scan → 0% coverage in Sonar.
3. **Monorepo paths** — sources are `apps`, not repo root; set `sonar.sources=apps` and ensure test paths align (`sonar.tests=tests`).
4. **Blocking gate on day one** — strict gate + legacy debt → red pipeline; defer `qualitygate.wait` until baseline is clean.

### Validation Architecture

_Not used — `workflow.nyquist_validation` is false for this workspace; no `05-VALIDATION.md` required._

---

*Research for Phase 5 — SonarQube static analysis and quality gates in CI.*
