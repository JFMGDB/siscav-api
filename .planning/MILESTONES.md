# Milestones

## v1.0 API brownfield hardening (shipped: 2026-04-05)

**Phases:** 4 (security/auth, whitelist + logs, gate + device honesty, operations hygiene)  
**Plans:** 11  
**Requirements v1:** 14/14 (ver [auditoria](milestones/v1.0-MILESTONE-AUDIT.md))

**Key accomplishments:**

1. **Segurança e auth:** ingest `POST /access_logs/` com `X-Device-Key` quando configurado; refresh com rate limit alinhado ao login; bloqueio de `SECRET_KEY` fraca em produção; `is_admin`, rotas admin (imagem, gate) e documentação alinhada (SEC-01–03, AUTH-01–02).
2. **Whitelist e auditoria:** CRUD de placas normalizado, ingestão multipart com persistência de metadados, listagem com filtros/ordenação, download de imagem só para admin (WL-01, LOG-01–03).
3. **Gate e dispositivos:** resposta explícita simulado vs HTTP live para cancela; API demo de dispositivo com 501 quando desligada e campo `demo` honesto (GATE-01, DEV-01).
4. **Operações:** remoção de atalhos de sessão/SQLite perigosos, dependências fixadas, remoção do pacote `crud/` duplicado (OPS-01–03).
5. **Qualidade:** suíte pytest (centenas de testes) mantida verde ao longo das fases; Postman/docs alinhados à API real.

**Arquivos:** [ROADMAP v1.0](milestones/v1.0-ROADMAP.md) · [REQUIREMENTS v1.0](milestones/v1.0-REQUIREMENTS.md) · [Audit v1.0](milestones/v1.0-MILESTONE-AUDIT.md)

---
