# Roadmap: SISCAV API

## Milestones

- ✅ **[v1.0 — API brownfield hardening](milestones/v1.0-ROADMAP.md)** — Fases 1–4 entregues em 2026-04-05 (11 planos). Arquivo: [requisitos v1.0](milestones/v1.0-REQUIREMENTS.md), [auditoria](milestones/v1.0-MILESTONE-AUDIT.md).

## Fases ativas / próximo ciclo

O milestone **v1.0** está fechado. **Fase 5 (SonarQube)** foi **concluída** (2026-05-03). Novo trabalho estruturado: **`/gsd-new-milestone`** e `REQUIREMENTS.md`.

## Backlog

### Phase 999.1: Interface — câmara Wi‑Fi/USB e pré-visualização em tempo real (BACKLOG)

**Goal:** O utilizador, através da interface, liga a câmara por Wi‑Fi ou USB e vê o vídeo em tempo real (pré-visualização), como requisito de produto para um cliente web ou app de operador.

**Requirements:** TBD (entrega API repo: docs + guia Next.js; código UI noutro Git)

**Plans:** 2/2 com SUMMARY; [VERIFICATION](phases/999.1-ui-camera-wifi-usb-live-preview/999.1-VERIFICATION.md) **passed** (2026-04-05)

Plans:

- [x] [999.1-01-PLAN.md](phases/999.1-ui-camera-wifi-usb-live-preview/999.1-01-PLAN.md) — [SUMMARY](phases/999.1-ui-camera-wifi-usb-live-preview/999.1-01-SUMMARY.md)
- [x] [999.1-02-PLAN.md](phases/999.1-ui-camera-wifi-usb-live-preview/999.1-02-PLAN.md) — [SUMMARY](phases/999.1-ui-camera-wifi-usb-live-preview/999.1-02-SUMMARY.md)

### Phase 5: SonarQube — análise estática e quality gates no CI

**Goal:** Integrar **SonarQube** (SonarCloud ou servidor self-hosted) para análise contínua de Python/FastAPI, cobertura de testes onde aplicável, e **quality gate** alinhado à equipa; segredos (`SONAR_TOKEN`) apenas em CI seguro.

**Requirements:** SONAR-01, SONAR-02, SONAR-03, SONAR-04 (ver [05-CONTEXT.md](phases/05-sonarqube-static-analysis-and-quality-gates-in-ci/05-CONTEXT.md))

**Depends on:** — (não depende da fase 999.1)

**Plans:** 2/2 com SUMMARY; [VERIFICATION](phases/05-sonarqube-static-analysis-and-quality-gates-in-ci/05-VERIFICATION.md) **passed** (2026-05-03)

Plans:

- [x] [05-01-PLAN.md](phases/05-sonarqube-static-analysis-and-quality-gates-in-ci/05-01-PLAN.md) — [SUMMARY](phases/05-sonarqube-static-analysis-and-quality-gates-in-ci/05-01-SUMMARY.md)
- [x] [05-02-PLAN.md](phases/05-sonarqube-static-analysis-and-quality-gates-in-ci/05-02-PLAN.md) — [SUMMARY](phases/05-sonarqube-static-analysis-and-quality-gates-in-ci/05-02-SUMMARY.md)

---

*Última atualização: 2026-05-03 — fase 5 SonarQube executada (planos 05-01, 05-02)*
