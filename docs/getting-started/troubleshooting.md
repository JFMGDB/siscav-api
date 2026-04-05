# Troubleshooting — API SISCAV e ambiente

Foco no **backend deste repositório** (`apps/api/src/`). Cliente ALPR/IoT em projeto separado: veja [`docs/iot/README.md`](../iot/README.md).

---

## Não consigo importar `apps` / erro ao subir o Uvicorn

### Sintomas

- `ModuleNotFoundError: No module named 'apps'`
- `Could not import module 'main'`

### Soluções

1. Na **raiz** do repositório (onde está `alembic.ini`):
   - Linux/macOS: `export PYTHONPATH=.`
   - PowerShell: `$env:PYTHONPATH = (Get-Location).Path`
   - Depois: `uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000`

2. Ou entre em `apps/api/src` e use: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

3. Windows: na raiz, `.\scripts\start_server.ps1` (define `PYTHONPATH` e chama o Uvicorn).

---

## Banco de dados / Alembic

### Sintoma

`sqlalchemy.exc.OperationalError` ou tabelas inexistentes.

### Soluções

- Com SQLite ou Postgres configurado, na raiz com `PYTHONPATH` se necessário: `alembic upgrade head`
- Confira `DATABASE_URL` ou `POSTGRES_*` em `apps/api/src/api/v1/core/config.py` e variáveis de ambiente
- Guia longo: [`docs/installation.md`](../installation.md)

---

## Migração `is_admin` / erro em rotas admin

O modelo `User` inclui `is_admin`. Se o banco foi criado antes dessa coluna, aplique migrações até a revisão mais recente em `apps/api/src/alembic/versions/`.

---

## JWT / 401 / 403

- Login: `POST /api/v1/login/access-token` (form `username` = email, `password`)
- Header: `Authorization: Bearer <access_token>`
- Access token expira (padrão em `ACCESS_TOKEN_EXPIRE_MINUTES`); use refresh conforme [`docs/api/FRONTEND_INTEGRATION.md`](../api/FRONTEND_INTEGRATION.md)

---

## Ingestão `POST /api/v1/access_logs/` retorna 401

Se `DEVICE_INGEST_KEY` estiver definido no servidor (ambiente não-development), o cliente deve enviar `X-Device-Key` com o mesmo valor. Ver `apps/api/src/api/v1/deps.py`.

---

## Rate limit no login

Mensagem do tipo `Rate limit exceeded`. Aguarde a janela ou ajuste limites em desenvolvimento (`apps/api/src/api/v1/core/limiter.py`, `endpoints/auth.py`).

---

## Anexo: NumPy / OpenCV / EasyOCR (projeto de borda **separado**)

Se você mantém um **outro** repositório com ALPR em Python e encontrar falha de compilação do NumPy no Windows:

- Prefira Python 3.11 ou 3.12 com wheels pré-compilados: `pip install --only-binary :all: numpy`
- Atualize pip: `python -m pip install --upgrade pip`
- Ferramentas de build C++ (Visual Studio Build Tools) só se realmente precisar compilar da fonte

**Não** existe mais `apps/iot-device/scripts/` neste repositório; adapte os caminhos ao seu projeto.

---

## Links

- [Iniciar servidor](../init-server-guide.md)
- [Instalação completa](../installation.md)
- [Índice da documentação](../README.md)
