# SISCAV API

Backend do **Sistema de Controle de Acesso Veicular (SISCAV)** — API FastAPI para whitelist de placas, registro de tentativas de acesso (com upload de imagem), autenticação JWT e acionamento opcional de portão via HTTP.

## Documentação

A documentação viva do projeto está em **[`docs/`](docs/README.md)**:

| Recurso | Caminho |
|--------|---------|
| Índice da documentação | [`docs/README.md`](docs/README.md) |
| Instalação e visão geral | [`docs/installation.md`](docs/installation.md) |
| Iniciar o servidor | [`docs/init-server-guide.md`](docs/init-server-guide.md) |
| Integração frontend / tokens | [`docs/api/FRONTEND_INTEGRATION.md`](docs/api/FRONTEND_INTEGRATION.md) |
| Frontend operador (Next.js — repo separado) | [`docs/frontend/`](docs/frontend/README.md) (guia câmara USB/Wi‑Fi: [camera-preview-nextjs.md](docs/frontend/camera-preview-nextjs.md)) |
| Testes com curl | [`docs/api_curl_tests_guide.md`](docs/api_curl_tests_guide.md) |
| Postman | [`docs/SISCAV_API.postman_collection.json`](docs/SISCAV_API.postman_collection.json) + [`docs/SISCAV_API.postman_environment.json`](docs/SISCAV_API.postman_environment.json) |
| OpenAPI (com a API rodando) | `http://localhost:8000/docs` |

## Início rápido

```bash
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
# Na raiz do repo (onde está alembic.ini):
set PYTHONPATH=.   # Linux/Mac: export PYTHONPATH=.
alembic upgrade head
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000
```

No Windows, a partir da raiz: `.\scripts\start_server.ps1`.

## Código

- Aplicação: `apps/api/src/` (`main.py`, `api/v1/…`)
- Testes: `tests/`
- Migrações Alembic: `apps/api/src/alembic/` (config em `alembic.ini` na raiz)

## Repositório

Este repositório concentra-se na **API**. Um cliente IoT/ALPR em Python que existia em `apps/iot-device/` foi removido do tree atual; dispositivos devem integrar via `POST /api/v1/access_logs/` (ver [`docs/iot/README.md`](docs/iot/README.md)).
