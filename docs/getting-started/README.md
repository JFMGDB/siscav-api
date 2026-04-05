# Getting started — SISCAV API

Esta seção cobre o **primeiro contato com o backend** deste repositório (API FastAPI em `apps/api/src/`).

## Documentos recomendados

1. **[Guia de instalação](../installation.md)** — dependências, ambiente, PostgreSQL/Supabase/SQLite, Alembic.
2. **[Como iniciar o servidor](../init-server-guide.md)** — Uvicorn, URLs úteis, script `scripts/start_server.ps1`.
3. **[Troubleshooting](./troubleshooting.md)** — problemas comuns da API e do ambiente Python.

## Início rápido (resumo)

```bash
git clone <seu-remote> siscav-api
cd siscav-api
python -m venv venv
# Ative o venv (Windows: .\venv\Scripts\Activate.ps1)
pip install -r requirements-dev.txt
```

Na **raiz** do repositório (onde está `alembic.ini`):

```bash
export PYTHONPATH=.    # PowerShell: $env:PYTHONPATH = $PWD
alembic upgrade head
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000
```

Windows (PowerShell), a partir da raiz:

```powershell
.\scripts\start_server.ps1
```

- API: http://localhost:8000  
- Swagger: http://localhost:8000/docs  
- Health: http://localhost:8000/api/v1/health  

## Dados de demonstração (opcional)

Com o banco migrado, a partir da raiz com `PYTHONPATH` definido:

```bash
cd apps/api/src
python seed_demo.py
```

Credenciais padrão do seed estão no docstring de `apps/api/src/seed_demo.py` — **não use em produção**.

## Cliente IoT / ALPR

Não há mais pasta `apps/iot-device/` neste repositório. Para integrar um dispositivo, leia **[`docs/iot/README.md`](../iot/README.md)**.

## Próximos passos

- [Documentação da API](../api/README.md)
- [Integração frontend](../api/FRONTEND_INTEGRATION.md)
- [Arquitetura](../architecture/README.md)
