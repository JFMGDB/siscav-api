# SISCAV API

## Current state (v1.0 shipped)

**Milestone v1.0** (“API brownfield hardening”) foi concluído em **2026-04-05**: API FastAPI com JWT, ingestão protegida de logs de acesso, whitelist, imagens de auditoria (admin), gate com integração HTTP opcional ou modo simulado, demo de dispositivo honesto, migrações Alembic e testes automatizados. Ver [.planning/MILESTONES.md](MILESTONES.md) e [.planning/milestones/v1.0-MILESTONE-AUDIT.md](milestones/v1.0-MILESTONE-AUDIT.md).

## What this is

SISCAV (Sistema de Controle de Acesso de Veículos) is a **central HTTP API** that supports automated vehicle access: operators authenticate, manage an authorized-plate whitelist, record access attempts with optional images, and trigger gate actions. The repository delivers a **FastAPI + SQLAlchemy** backend (`apps/api/src/`) with Alembic migrations, JWT auth, and integration tests. Edge ALPR/camera pipelines are **out of this repo** unless re-scoped; clients send plate + image to the API.

## Core value

**Trustworthy plate-based access decisions and an auditable log of every attempt** (authorized or denied), with a clear path to secure device-to-server communication and real gate hardware integration.

## Requirements

### Validated (v1.0)

- ✓ **REST API v1** under `/api/v1` with OpenAPI
- ✓ **User registration, JWT access/refresh, password reset** (conforme implementação atual)
- ✓ **Authorized plate whitelist CRUD** with normalized matching
- ✓ **Access log ingestion** (device key when configured) **and listing** with filters; **admin-only** stored image retrieval
- ✓ **Gate trigger** — simulated vs optional HTTP `GATE_ACTUATOR_URL` with explicit response
- ✓ **Device demo API** — feature-flagged; 501 when disabled; `demo` on schemas
- ✓ **Health check**, **Alembic migrations**, **pytest** unit + integration coverage
- ✓ **Operations hygiene** — no ad hoc `create_all` in session bootstrap; pinned deps; `crud/` removed
- ✓ **SonarQube / SonarCloud CI hook** — `sonar-project.properties`, pytest `coverage.xml`, scan condicional no GitHub Actions; setup em `.github/SONAR_SETUP.md` (Phase 5, 2026-05-03)

### Active (next milestones)

- [ ] **Deeper edge integration** — MQTT, comandos assinados, multi-site (além do POST HTTP opcional)
- [ ] **Product UI** — dashboard ou app de operador (ver backlog **999.1** no [ROADMAP](ROADMAP.md): câmara Wi‑Fi/USB + pré-visualização em tempo real)
- [ ] **v2 ideas** em arquivo de requisitos futuros (OAuth social, etc.) quando `REQUIREMENTS.md` for recriado

### Out of scope

- **On-device ALPR** (RF-001–RF-003 no hardware) — deliverable separado; a API consome placa + imagem dos clientes.
- **Full operator SPA in this repo** — ainda fora; CORS preparado para dev; backlog 999.1 captura intenção de UI/câmara.

## Context

- **Brownfield:** `.planning/codebase/` (STACK, ARCHITECTURE, CONCERNS).
- **Product:** acesso veicular privado, trilho de auditoria, cancela por relé — `docs/requirements/project-specification.md`.
- **Stack:** Python 3.10+ (CI 3.13), FastAPI, SQLAlchemy, PostgreSQL ou SQLite em dev.
- **Planning:** [.planning/ROADMAP.md](ROADMAP.md); arquivo v1.0 em `.planning/milestones/`.

## Constraints

- Manter FastAPI / SQLAlchemy / Alembic salvo fase explícita de migração de stack.
- Preservar contratos da API cobertos por testes e `docs/api/`.
- Produção: sem `SECRET_KEY` por omissão nem ingestão pública sem modelo de ameaça documentado.

## Key decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| GSD planning no repo API existente | Brownfield com mapa de código + spec | ✓ v1.0 fechado com fases 1–4 |
| Ingestão com `X-Device-Key` + exceção dev documentada | Threat model por ambiente | ✓ SEC-01 |
| Gate e device “honestos” (simulated / 501) | Operadores não confundem mock com hardware | ✓ GATE-01, DEV-01 |
| IoT em repo separado | Foco API-first | ✓ Mantido |

## Next milestone goals

1. Definir **v1.1** (ou **v2.0**) com `/gsd-new-milestone`: novo `REQUIREMENTS.md`, roadmap e fases.
2. Opcional: promover **999.1** (UI + câmara) para fase ativa quando existir frontend ou arquitetura escolhida.

## Evolution

Atualizar este documento em cada transição de milestone.

<details>
<summary>Histórico (pré v1.0)</summary>

Secções antigas de “Active” listavam itens já fechados nas fases 1–4 (SEC, OPS, whitelist, logs). Esses itens encontram-se agora em **Validated (v1.0)**.

</details>

---
*Last updated: 2026-05-03 — SonarQube (fase 5) implementada e verificada*
