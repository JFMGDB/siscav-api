# siscav-api: Backend do Sistema de Controle de Acesso de Veículos

[![CI Pipeline](https://github.com/JFMGDB/siscav-api/actions/workflows/ci.yml/badge.svg)](https://github.com/JFMGDB/siscav-api/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: Academic](https://img.shields.io/badge/license-Academic-green.svg)](https://unicap.br)

Este é o repositório backend para o "Sistema de Controle de Acesso de Veículos".

> **⚠️ Status do Projeto:** Este projeto está em **desenvolvimento inicial**. A documentação abaixo descreve a arquitetura planejada e funcionalidades que estão sendo implementadas.

## Visão Geral

A arquitetura geral do projeto é dividida em dois repositórios distintos: `siscav-api` (este) e `siscav-web` (frontend).

Este repositório (`siscav-api`) contém toda a lógica do lado do servidor e tem como núcleo a **API Central**:

1.  **API Central (`apps/api`):** Um serviço backend robusto construído com **FastAPI**. Ele serve como o "cérebro" do sistema, utilizando um banco de dados **PostgreSQL** para:
    * Autenticar administradores.
    * Validar placas de veículos recebidas contra uma "whitelist".
    * Registrar cada tentativa de acesso (com foto).
    * Enviar comandos de acionamento para o portão.
> Nota: O **script IoT** (ALPR + comunicação com a API) está planejado para um repositório/pasta separado e ainda não está presente neste repositório.

## Principais Funcionalidades (Planejadas)

* **Autenticação:** Sistema seguro de login para administradores baseado em **JWT**.
* **Gerenciamento (CRUD):** Endpoints completos para Criar, Ler, Atualizar e Deletar placas na lista de veículos autorizados (whitelist).
* **Registro de Acesso:** Endpoint para o dispositivo IoT submeter dados (placa, imagem), com cada tentativa sendo registrada de forma persistente no banco de dados.
* **Visualização de Logs:** Endpoint para o frontend buscar o histórico de logs de acesso, com suporte a filtragem por placa, intervalo de datas e status.
* **Controle Remoto:** Endpoint que permite a um administrador autenticado acionar a abertura do portão remotamente através do painel web.
* **Segurança:** Implementa limitação de taxa (rate limiting) no endpoint de login para prevenir força bruta e exige comunicação criptografada (HTTPS) do dispositivo IoT.

### Funcionalidades Implementadas

- ✅ Estrutura básica do projeto FastAPI
- ✅ Endpoint raiz (`/`)
- ✅ Endpoint de health check (`/api/v1/health`)
- ✅ Pipeline de CI/CD com GitHub Actions
- ✅ Linting automatizado com Ruff
- ✅ Testes unitários com Pytest 
- ✅ CI com GitHub Actions (lint + testes)
- ⏳ Autenticação JWT (em desenvolvimento)
- ⏳ CRUD de placas autorizadas (em desenvolvimento)
- ⏳ Sistema de logs de acesso (em desenvolvimento)
- ⏳ Integração com dispositivo IoT (em desenvolvimento)

## Stack Tecnológica

* **Backend:** Python, FastAPI
* **Banco de Dados:** PostgreSQL
* **ORM e Migrações:** SQLAlchemy, Alembic
* **Validação de Dados:** Pydantic
* **Autenticação:** JWT (com `passlib` para hashing)
* **ALPR (IoT):** `easyocr`
* **DevOps:** Docker, Docker Compose, GitHub Actions

## Estrutura do Projeto

A estrutura de diretórios deste repositório segue uma abordagem orientada a domínio para máxima clareza e manutenibilidade.

```bash
siscav-api/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline de CI (lint + testes)
├── apps/
│   ├── api/                # Serviço Backend FastAPI
│   │   └── src/            # Código-fonte da API
│   │       ├── api/
│   │       │   └── v1/
│   │       │       ├── endpoints/  # Roteadores (auth.py, whitelist.py...)
│   │       │       ├── core/       # Config (config.py), Segurança (security.py)
│   │       │       ├── crud/       # Funções de interação com o DB (CRUD)
│   │       │       ├── db/         # Sessão e base do SQLAlchemy
│   │       │       ├── models/     # Modelos SQLAlchemy (Tabelas)
│   │       │       └── schemas/    # Modelos Pydantic (Validação)
│   │       ├── alembic/            # Migrações de banco de dados (Alembic)
│   │       └── main.py         # Ponto de entrada da aplicação FastAPI
│   └── (iot-device)        # Planejado (fora deste repo por ora)
├── db/
│   └── sql/
│       └── supabase/        # Scripts SQL para migração manual no Supabase
│           ├── 01_enable_extensions.sql
│           ├── 02_types.sql
│           ├── 03_tables.sql
│           └── 04_indexes.sql
├── docs/                   # Documentação do projeto
│   ├── Arquitetura - Critérios de Aceite e Devops.md
│   ├── Arquitetura e Backlog do projeto.md
│   ├── Especificação de Projeto.md
│   └── DB_MIGRATION_SUPABASE.md   # Guia para migração manual no Supabase
├── tests/                  # Testes unitários
│   ├── __init__.py
│   └── test_main.py        # Testes da API principal
├── .gitignore
├── .dockerignore
├── alembic.ini             # Configuração do Alembic
├── pyproject.toml          # Dependências e configuração do projeto
├── ruff.toml               # Configuração do linter Ruff
├── Dockerfile.dev          # Ambiente de desenvolvimento da API
├── docker-compose.yml      # Orquestração para dev/local/Supabase
├── requirements.txt        # Dependências de runtime
├── requirements-dev.txt    # Dependências de desenvolvimento/CI
├── CHANGELOG.md            # Registro de mudanças
└── README.md
```

## Guia de Instalação (Getting Started)

> **Nota:** Agora há suporte completo a Docker Compose para desenvolvimento. Você também pode executar localmente com Python, se preferir.

### Pré-requisitos

* Python 3.13+
* pip ou uv (gerenciador de pacotes Python)

### Instalação Local (Desenvolvimento Atual)

1. **Clonar o Repositório**

```bash
git clone https://github.com/JFMGDB/siscav-api.git
cd siscav-api
```

2. **Criar Ambiente Virtual**

```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

3. **Instalar Dependências**

```bash
pip install -r requirements-dev.txt
```

4. **Executar a Aplicação**

```bash
cd apps/api/src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará acessível em http://localhost:8000.

5. **Testar os Endpoints**

- **Raiz:** http://localhost:8000/
- **Health Check:** http://localhost:8000/api/v1/health
- **Documentação Swagger:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Guia de Instalação com Docker (Desenvolvimento)

Este guia detalha como configurar e executar o ambiente de desenvolvimento local usando Docker e Docker Compose (FND-02).

### Pré-requisitos

* Docker
* Docker Compose

### 1. Clonar o Repositório

```bash
git clone https://github.com/JFMGDB/siscav-api.git
cd siscav-api
```

### 2. Configuração do Ambiente (.env) — escolha UMA opção

Opção A) Local (PostgreSQL no Docker): crie `.env.local` com:

```ini
# PostgreSQL (serviço local "db")
POSTGRES_USER=siscav_user
POSTGRES_PASSWORD=siscav_password
POSTGRES_DB=siscav_db

# Observação: a aplicação monta automaticamente o DATABASE_URL a partir das variáveis POSTGRES_*
# (host padrão: db, porta: 5432). Não é necessário definir DATABASE_URL aqui.

# JWT
SECRET_KEY=change_me_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
```

Opção B) Remota (Supabase): crie `.env.supabase` com:

```ini
# SQLAlchemy (string do Supabase com SSL)
DATABASE_URL=postgresql+psycopg2://<usuario>:<senha>@<host>:5432/<db>?sslmode=require

# JWT (pode diferir por ambiente)
SECRET_KEY=another_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Não é necessário definir POSTGRES_USER/PASSWORD/DB para essa opção
```

### 3. Executar a Aplicação (Desenvolvimento)

Opção A) Local (sobe API + Postgres com profile "local"):

```bash
docker compose --env-file .env.local --profile local up -d --build
```

Opção B) Supabase (sobe apenas a API, sem serviço de DB local):

```bash
docker compose --env-file .env.supabase up -d --build
```

A API estará acessível em http://localhost:8000.

#### Escolha explícita do ambiente (.env) e perfis

- O arquivo `docker-compose.yml` define o serviço `db` com `profiles: ["local"]`. Isso significa:
  - Com `.env.local` + `--profile local`: sobem `api` + `db` (Postgres local).
  - Com `.env.supabase` (sem `--profile local`): sobe somente `api` (usa o Postgres do Supabase via `DATABASE_URL`).

Exemplos de uso:

```bash
# Ambiente local (API + Postgres local)
docker compose --env-file .env.local --profile local up -d --build

# Ambiente Supabase (somente API)
docker compose --env-file .env.supabase up -d --build
```

Alternar entre ambientes (recomendado):

```bash
# Derruba os serviços do ambiente atual (mantém volumes)
docker compose --env-file .env.local down

# Sobe no outro ambiente
docker compose --env-file .env.supabase up -d --build
```

Opcional — reset do banco local:

```bash
# Cuidado: remove os volumes, apagando os dados do Postgres local
docker compose --env-file .env.local down -v
```

### 4. Executar as Migrações (Alembic)

Após iniciar os contêineres, aplique as migrações:

```bash
# Local
docker compose --env-file .env.local exec api alembic upgrade head

# Supabase
docker compose --env-file .env.supabase exec api alembic upgrade head
```

Para criar novas migrações após alterar os `models.py`:

```bash
# Local
docker compose --env-file .env.local exec api alembic revision --autogenerate -m "Descrição da sua migração"

# Supabase
docker compose --env-file .env.supabase exec api alembic revision --autogenerate -m "Descrição da sua migração"
```

### 5. Comandos úteis

```bash
# Ver logs em tempo real (ex.: local)
docker compose --env-file .env.local logs -f api

# Acessar um shell no contêiner da API
docker compose --env-file .env.local exec api bash

# Parar e remover serviços (mantendo volumes)
docker compose --env-file .env.local down
```

Observações sobre variáveis de ambiente e exposição:

- O `docker-compose.yml` define apenas os nomes das variáveis para “pass-through”. Os valores vêm do arquivo passado via `--env-file`. Assim, nenhum valor sensível fica codificado no compose.
- Garanta que `.env.local` e `.env.supabase` estão listados no `.gitignore` para evitar commit de segredos.
- Em ambientes remotos, use `?sslmode=require` no `DATABASE_URL` do Supabase.

### Como o `DATABASE_URL` é resolvido

A aplicação resolve a URL do banco por prioridade (vide `apps/api/src/api/v1/core/config.py`):

1. Se `DATABASE_URL` estiver definido, usa exatamente esse valor.
   - `.env.supabase`: aponta para o Supabase (com `sslmode=require`).
   - `.env.local`: pode apontar para o Postgres do Docker (`db:5432`).
2. Se não houver `DATABASE_URL`, mas existir `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`,
   a URL é montada automaticamente usando `POSTGRES_HOST` (default `db`) e `POSTGRES_PORT` (default `5432`).
3. Caso nada disso exista, fallback para SQLite local: `sqlite:///./siscav_dev.db` (útil para execuções bare sem `.env`).

Isso permite alternar entre Supabase e Postgres local apenas trocando o arquivo `.env` passado ao Docker Compose.

---

## Migração manual para Supabase (sem Docker)

Quando houver impedimentos de rede/DNS no Docker, você pode aplicar o schema diretamente no Supabase.

- Guia detalhado: `docs/DB_MIGRATION_SUPABASE.md`
- Scripts SQL: `db/sql/supabase/`
  - `01_enable_extensions.sql` (pgcrypto, pg_trgm)
  - `02_types.sql` (ENUM `access_status`)
  - `03_tables.sql` (`users`, `authorized_plates`, `access_logs`)
  - `04_indexes.sql` (índices recomendados e opcionais com pg_trgm)

Passos no Supabase Studio (SQL Editor): execute os arquivos na ordem 01 → 04.

Após criar manualmente, sincronize o Alembic local sem tocar o banco:

```powershell
$env:DATABASE_URL='postgresql+psycopg2://<user>:<senha_urlenc>@<host>:5432/postgres?sslmode=require'
alembic stamp head
```

Observações:
- Se usar senha com caracteres especiais, faça URL-encode (`?` → `%3F`).
- Se aparecer erro de `gen_random_uuid()`, rode no Supabase: `CREATE EXTENSION IF NOT EXISTS pgcrypto;`.

---

## Sobre os arquivos de requisitos (requirements)

- `requirements.txt`: dependências de runtime — o mínimo necessário para a API rodar (produção).
- `requirements-dev.txt`: estende o base com `-r requirements.txt` e adiciona apenas ferramentas de desenvolvimento/teste (ex.: `pytest`, `ruff`, `httpx`).

Como usar:

```bash
# Ambiente de produção/execução simples
pip install -r requirements.txt

# Ambiente de desenvolvimento/CI
pip install -r requirements-dev.txt
```

No Docker:

- `Dockerfile.dev` instala `-r requirements-dev.txt` para oferecer hot-reload e tooling dentro do container de desenvolvimento.
- Em um futuro `Dockerfile` de produção, instale apenas `-r requirements.txt` para uma imagem menor e mais segura.

Motivação:

- Imagens mais enxutas em produção e builds mais rápidos (camadas de cache) em desenvolvimento.
- Separação clara entre dependências necessárias para executar a API e ferramentas usadas apenas em dev/CI.

---

## Testes

A suíte de testes está implementada com pytest. Para executá-los localmente:

```bash
# Com ambiente virtual ativado
pytest

# Com verbose e cobertura
pytest -v --cov=apps --cov-report=term-missing

# Executar testes específicos
pytest tests/test_main.py
```

## Troubleshooting

- Import "fastapi.testclient" could not be resolved
  - Certifique-se de que o seu editor/IDE está usando o interpretador do projeto (Python 3.13 no venv):
    - VS Code (Pylance): Ctrl+Shift+P → "Python: Select Interpreter" → selecione "Python 3.13.5 ('venv': venv)".
  - Instale as dependências de desenvolvimento no venv ativo:
    ```bash
    pip install -r requirements-dev.txt
    ```
  - Alternativa: troque o import no teste para Starlette (equivalente):
    ```python
    from starlette.testclient import TestClient
    ```

- Editor não resolve imports (e.g., "Import \"fastapi\" could not be resolved")
  - Selecione o interpretador do projeto no editor:
    - VS Code: Ctrl+Shift+P → "Python: Select Interpreter" → escolha `./venv` (Python 3.13).
  - Recarregue a janela do VS Code após ativar o venv e instalar as dependências.
  - Garanta que o terminal integrado esteja com o venv ativo ao rodar comandos (mostra `(venv)` no prompt).

- CI falhando por erros de Linting ou Formatação
  - Antes de commitar, rode os comandos localmente para corrigir os problemas:
    ```bash
    # Para corrigir erros de lint (ex: imports não utilizados, etc.)
    ruff check --fix .

    # Para corrigir erros de formatação de código (ex: espaçamento, quebras de linha)
    ruff format .
    ```

### Por que usar requirements .txt em vez de apenas pyproject.toml?

- Este projeto oferece ambos os caminhos:
  - Rápido/simples com pip: `requirements.txt` (runtime) e `requirements-dev.txt` (dev/CI), ideal para Docker cache e ambientes sem build backend.
  - Alternativa via PEP 621: `pip install -e ".[dev]"` (já suportado por `pyproject.toml` em `[project.optional-dependencies].dev`).
- No Docker/CI usamos os `.txt` por:
  - Cache eficiente por camadas ao copiar apenas os requirements.
  - Separação clara de deps de produção e de desenvolvimento.
  - Menor superfície de ferramentas no container de runtime.


## Integração Contínua (CI) 

Este projeto utiliza **GitHub Actions** para integração contínua. O pipeline está configurado e funcional!

**Workflow:** `.github/workflows/ci.yml`