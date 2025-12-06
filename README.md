# siscav-api: Backend do Sistema de Controle de Acesso de Veículos

[![CI Pipeline](https://github.com/JFMGDB/siscav-api/actions/workflows/ci.yml/badge.svg)](https://github.com/JFMGDB/siscav-api/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
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
- ✅ Arquitetura MVC com separação de responsabilidades (SOLID, DRY)
- ✅ Endpoint raiz (`/`)
- ✅ Endpoint de health check (`/api/v1/health`)
- ✅ Autenticação JWT com rate limiting
- ✅ CRUD completo de placas autorizadas (whitelist)
- ✅ Sistema de logs de acesso com filtros
- ✅ Pipeline de CI/CD com GitHub Actions
- ✅ Linting automatizado com Ruff
- ✅ Testes unitários com Pytest
- ⏳ Integração completa com dispositivo IoT (parcialmente implementado)

## Stack Tecnológica

* **Backend:** Python, FastAPI
* **Banco de Dados:** PostgreSQL
* **ORM e Migrações:** SQLAlchemy, Alembic
* **Validação de Dados:** Pydantic
* **Autenticação:** JWT (com `passlib` para hashing)
* **Reconhecimento de Placas (IoT):** EasyOCR, OpenCV
* **DevOps:** GitHub Actions

## Código Fonte de Reconhecimento de Placas

O código relacionado ao reconhecimento automático de placas veiculares (processamento de imagem e OCR) está localizado em:

**`apps/iot-device/`** - Dispositivo IoT completo

### Componentes Principais:

- **`services/ocr.py`**: Serviço de OCR utilizando EasyOCR (Deep Learning) para extração de texto das placas
- **`services/plate_detector.py`**: Detecção de placas usando visão computacional (OpenCV) com algoritmos de detecção de bordas, operações morfológicas e análise de contornos
- **`services/camera.py`**: Serviço de captura de imagens da câmera
- **`services/api_client.py`**: Cliente HTTP para comunicação com a API central
- **`utils/plate_validator.py`**: Validação de formatos de placas brasileiras (antigo ABC1234 e Mercosul ABC1D23)
- **`utils/debounce.py`**: Sistema de debounce para evitar processamento duplicado da mesma placa
- **`main.py`**: Orquestração principal do fluxo de detecção, OCR e envio para API

### Tecnologias Utilizadas:

- **EasyOCR**: Biblioteca de OCR baseada em Deep Learning (CNN + RNN) para reconhecimento de caracteres
- **OpenCV**: Processamento de imagem para detecção de placas (Canny, morfologia, contornos)
- **NumPy**: Manipulação de arrays de imagem

### Documentação Relacionada:

- Guias de demonstração: `apps/iot-device/docs/`
- Documentação técnica IoT: `apps/iot-device/docs/`
- Documentação da API: `apps/api/docs/`
- Apresentação técnica: `docs/presentation/`

## Arquitetura

O projeto segue o padrão **MVC (Model-View-Controller)** com separação clara de responsabilidades, aplicando princípios **SOLID** e **DRY**:

- **Models**: Modelos SQLAlchemy definindo a estrutura do banco de dados
- **Views (Endpoints)**: Camada de roteamento HTTP, responsável apenas por receber requisições e retornar respostas
- **Controllers**: Camada de lógica de negócio, orquestrando operações e aplicando regras de negócio
- **Repositories**: Camada de acesso a dados, isolando operações de banco de dados

Para mais detalhes sobre a arquitetura, consulte: `docs/development/coding-standards.md`

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
│   │       │       ├── endpoints/  # Roteadores HTTP (Views - auth.py, whitelist.py...)
│   │       │       ├── controllers/ # Lógica de negócio (Service Layer)
│   │       │       ├── repositories/ # Acesso a dados (Data Access Layer)
│   │       │       ├── core/       # Config (config.py), Segurança (security.py)
│   │       │       ├── crud/       # DEPRECATED - Use repositories/ e controllers/
│   │       │       ├── db/         # Sessão e base do SQLAlchemy
│   │       │       ├── models/     # Modelos SQLAlchemy (Tabelas)
│   │       │       └── schemas/    # Modelos Pydantic (Validação)
│   │       ├── alembic/            # Migrações de banco de dados (Alembic)
│   │       └── main.py         # Ponto de entrada da aplicação FastAPI
│   └── iot-device/           # Dispositivo IoT para reconhecimento de placas
│       ├── services/         # Serviços de processamento
│       │   ├── camera.py     # Captura de imagens da câmera
│       │   ├── plate_detector.py  # Detecção de placas (visão computacional)
│       │   ├── ocr.py         # Reconhecimento de texto (EasyOCR)
│       │   └── api_client.py  # Cliente para comunicação com API
│       ├── utils/            # Utilitários
│       │   ├── plate_validator.py  # Validação de formatos de placas brasileiras
│       │   └── debounce.py    # Sistema de debounce para evitar duplicatas
│       ├── config.py         # Configurações do dispositivo
│       └── main.py           # Ponto de entrada do dispositivo IoT
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
├── alembic.ini             # Configuração do Alembic
├── pyproject.toml          # Dependências e configuração do projeto
├── ruff.toml               # Configuração do linter Ruff
├── requirements.txt        # Dependências de runtime
├── requirements-dev.txt    # Dependências de desenvolvimento/CI
├── CHANGELOG.md            # Registro de mudanças
└── README.md
```

## Guia de Instalação (Getting Started)

### Pré-requisitos

* Python 3.12
* pip ou uv (gerenciador de pacotes Python)

### Instalação Local (Desenvolvimento Atual)

1. **Clonar o Repositório**

```bash
git clone https://github.com/JFMGDB/siscav-api.git
cd siscav-api
```

2. **Criar Ambiente Virtual**

```bash
# Usando Python 3.12 especificamente
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

## Migração manual para Supabase

Você pode aplicar o schema diretamente no Supabase.

- Guia detalhado: `apps/api/docs/database/supabase-migration.md`
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

Motivação:

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
  - Certifique-se de que o seu editor/IDE está usando o interpretador do projeto (Python 3.12 no venv):
    - VS Code (Pylance): Ctrl+Shift+P → "Python: Select Interpreter" → selecione "Python 3.12.x ('venv': venv)".
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
    - VS Code: Ctrl+Shift+P → "Python: Select Interpreter" → escolha `./venv` (Python 3.12).
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
  - Rápido/simples com pip: `requirements.txt` (runtime) e `requirements-dev.txt` (dev/CI).
  - Alternativa via PEP 621: `pip install -e ".[dev]"` (já suportado por `pyproject.toml` em `[project.optional-dependencies].dev`).
- Usamos os `.txt` por:
  - Separação clara de deps de produção e de desenvolvimento.
  - Facilidade de uso em ambientes virtuais.


## Integração Contínua (CI) 

Este projeto utiliza **GitHub Actions** para integração contínua. O pipeline está configurado e funcional!

**Workflow:** `.github/workflows/ci.yml`