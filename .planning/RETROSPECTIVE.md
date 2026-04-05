# Retrospective — SISCAV API planning

## Milestone v1.0 — API brownfield hardening

**Shipped:** 2026-04-05  
**Phases:** 4 · **Plans:** 11

### What was built

Hardening de uma API já existente: segurança de ingestão e JWT, whitelist e trilho de auditoria completo, honestidade de integração de cancela e API de demo de dispositivo, higiene operacional (sessão, dependências, remoção de `crud/`).

### What worked

- Fases largas (3–5) com planos numerados e `VERIFICATION.md` por fase facilitaram fecho com auditoria.
- Testes de integração cobrindo auth → whitelist → ingest → list → admin image → gate.

### What was inefficient

- `REQUIREMENTS.md` ficou desfasado dos checkboxes até à auditoria final — corrigido antes do arquivo.
- Contagem “5 fases” no CLI ao incluir 999.1 backlog; milestone v1.0 reporta **4** fases entregues.

### Lessons

- Após cada fase, alinhar traceability em `REQUIREMENTS.md` ou confiar na auditoria para sincronizar no fecho do marco.

---

## Cross-milestone trends

_(Preencher após v1.1+.)_
