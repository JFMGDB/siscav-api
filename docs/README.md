# Documentação do projeto SISCAV

Documentação técnica e operacional do **SISCAV API** — backend FastAPI para controle de acesso veicular baseado em placas, com registro auditável e integração opcional com atuador de portão.

**Última revisão estrutural:** 2026-04-05 (alinhada ao repositório atual: sem `apps/iot-device/` no tree).

## Visão geral

O produto deste repositório é a **API central**: autenticação (JWT + refresh), CRUD de placas autorizadas, ingestão de logs de acesso (multipart: imagem + placa), listagens com filtros, e endpoint administrativo para acionar portão (simulado ou HTTP externo). Reconhecimento de placa em câmera (OpenCV/EasyOCR) **não** faz parte do código da API; um cliente de borda pode chamar a API documentada em [`docs/api/`](api/) e [`docs/iot/README.md`](iot/README.md).

## Estrutura da documentação

### [Getting started](./getting-started/)

- [README — primeiro passos (API)](./getting-started/README.md)
- [Troubleshooting (API e ambiente)](./getting-started/troubleshooting.md)
- **Instalação completa:** [Guia de instalação](./installation.md) (raiz de `docs/`)

### [Instalação (guia longo)](./installation.md)

Instalação da API, banco (PostgreSQL / Supabase / SQLite), Alembic, variáveis de ambiente e verificação.

### [Iniciar o servidor](./init-server-guide.md)

Uvicorn, health check, Swagger e script PowerShell em `scripts/start_server.ps1`.

### [API](./api/)

- [README da pasta API](./api/README.md)
- [Integração frontend](./api/FRONTEND_INTEGRATION.md) — tokens, refresh, CORS
- Documentação técnica detalhada: [`../apps/api/docs/technical-documentation.md`](../apps/api/docs/technical-documentation.md)
- **Postman:** [`SISCAV_API.postman_collection.json`](SISCAV_API.postman_collection.json), [`SISCAV_API.postman_environment.json`](SISCAV_API.postman_environment.json)
- [Guia de testes com curl](./api_curl_tests_guide.md)

### [Database](./database/)

Visão geral; detalhes de modelo em [`../apps/api/docs/database/data-model.md`](../apps/api/docs/database/data-model.md) e Supabase em [`../apps/api/docs/database/supabase-migration.md`](../apps/api/docs/database/supabase-migration.md).

### [IoT / cliente de borda](./iot/README.md)

Contrato HTTP com a API para dispositivos que enviam placas e imagens. **Não** há mais aplicação IoT em `apps/iot-device/` neste repositório.

### [Hardware](./hardware/README.md)

Referência histórica; firmware Arduino que existia em `arduino/` não está mais no tree atual.

### [Operations](./operations/README.md)

Operação da API (logs, Postman, ambiente), sem dependência de pasta `apps/iot-device/`.

### [Development](./development/)

- [Padrões de código e arquitetura](./development/coding-standards.md)

### [Architecture](./architecture/)

- [Resumo executivo](./architecture/executive-summary.md)
- [Critérios de aceite / DevOps](./architecture/acceptance-criteria-devops.md)

### [Requirements](./requirements/)

- [Especificação de projeto](./requirements/project-specification.md)

### [Project management](./project-management/)

Status e cards Trello podem citar caminhos antigos (`apps/iot-device/`); tratar como histórico.

### [Presentation](./presentation/)

Materiais de apresentação.

### [Archive](./archive/)

Documentos arquivados e decisões antigas.

## Guias por perfil

### Desenvolvedor backend

1. [installation.md](./installation.md) e [init-server-guide.md](./init-server-guide.md)
2. [apps/api/docs/technical-documentation.md](../apps/api/docs/technical-documentation.md)
3. [development/coding-standards.md](./development/coding-standards.md)
4. Testes: `pytest` na raiz (ver [`.planning/codebase/TESTING.md`](../.planning/codebase/TESTING.md) se usar o mapa GSD)

### Frontend

1. [api/FRONTEND_INTEGRATION.md](./api/FRONTEND_INTEGRATION.md)
2. OpenAPI em `/docs` com a API rodando

### Integração de dispositivo / parceiro

1. [iot/README.md](./iot/README.md)
2. [api_curl_tests_guide.md](./api_curl_tests_guide.md) e coleção Postman em `docs/`

### Gestor / produto

1. [requirements/project-specification.md](./requirements/project-specification.md)
2. [architecture/executive-summary.md](./architecture/executive-summary.md)

## Stack (referência rápida)

Valores pinados em [`pyproject.toml`](../pyproject.toml) na raiz — exemplos: FastAPI, Uvicorn, SQLAlchemy 2.x, Alembic, Pydantic, Argon2, JWT (`python-jose`), SlowAPI. CI em [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) usa Python 3.13 com `requirements-dev.txt`.

## Manutenção

Ao alterar endpoints ou env vars, atualize: `apps/api/docs/`, `docs/installation.md`, `docs/init-server-guide.md` e, se aplicável, Postman em `docs/`.

## Contribuindo

Mantenha links relativos ao repositório atual; evite referências a `apps/iot-device/` ou `app/` como prefixo da API (o pacote é `apps.api.src`).
