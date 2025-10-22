# siscav-api: Backend do Sistema de Controle de Acesso de Veículos

[![CI Pipeline](https://github.com/JFMGDB/siscav-api/actions/workflows/ci.yml/badge.svg)](https://github.com/JFMGDB/siscav-api/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: Academic](https://img.shields.io/badge/license-Academic-green.svg)](https://unicap.br)

Este é o repositório backend para o "Sistema de Controle de Acesso de Veículos".

> **⚠️ Status do Projeto:** Este projeto está em **desenvolvimento inicial**. A documentação abaixo descreve a arquitetura planejada e funcionalidades que estão sendo implementadas.

## Visão Geral

A arquitetura geral do projeto é dividida em dois repositórios distintos: `siscav-api` (este) e `siscav-web` (frontend).

Este repositório (`siscav-api`) contém toda a lógica do lado do servidor e é composto por duas aplicações Python principais:

1.  **API Central (`apps/api`):** Um serviço backend robusto construído com **FastAPI**. Ele serve como o "cérebro" do sistema, utilizando um banco de dados **PostgreSQL** para:
    * Autenticar administradores.
    * Validar placas de veículos recebidas contra uma "whitelist".
    * Registrar cada tentativa de acesso (com foto).
    * Enviar comandos de acionamento para o portão.
2.  **Script IoT (`apps/iot-device`):** Um script Python projetado para ser executado no dispositivo de borda (ex: Raspberry Pi). Este script utiliza a biblioteca **`easyocr`** para realizar o Reconhecimento Automático de Placas de Veículos (ALPR). Após capturar e processar a imagem de um veículo, ele envia os dados via `POST HTTPS` seguro para a API Central e aguarda uma resposta (`Autorizado`/`Negado`) para acionar o relé físico via `GPIO`.

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
- ✅ Testes unitários com Pytest (4 testes)
- ✅ Documentação completa do CI/CD
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
│   ├── workflows/
│   │   └── ci.yml              # Pipeline de CI/CD
│   ├── CI_LOCAL_GUIDE.md       # Guia para testar CI localmente
│   ├── GUIA_COMANDOS.md        # Comandos úteis e referências rápidas
│   ├── PULL_REQUEST_TEMPLATE.md # Template para Pull Requests
│   └── README_CI.md            # Documentação completa do CI/CD
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
│   │       ├── alembic/            # Migrações de banco de dados
│   │       └── main.py         # Ponto de entrada da aplicação FastAPI
│   └── iot-device/         # Script Python ALPR (easyocr) - em desenvolvimento
├── docs/                   # Documentação do projeto
│   ├── Arquitetura - Critérios de Aceite e Devops.md
│   ├── Arquitetura e Backlog do projeto.md
│   └── Especificação de Projeto.md
├── tests/                  # Testes unitários
│   ├── __init__.py
│   └── test_main.py        # Testes da API principal
├── .gitignore
├── pyproject.toml          # Dependências e configuração do projeto
├── ruff.toml               # Configuração do linter Ruff
└── README.md
```

## Guia de Instalação (Getting Started)

> **Nota:** Os arquivos de configuração Docker estão sendo desenvolvidos. Por enquanto, você pode executar a aplicação localmente com Python.

### Pré-requisitos

* Python 3.10+
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
pip install -e ".[dev]"
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

## Guia de Instalação com Docker (Em Desenvolvimento)

> **⚠️ Aviso:** Os arquivos Docker ainda não foram criados. Esta seção documenta como será a configuração futura.

Este guia detalha como configurar e executar o ambiente de desenvolvimento local usando Docker.

### Pré-requisitos

* Docker
* Docker Compose

### 1. Clonar o Repositório

```bash
git clone https://github.com/JFMGDB/siscav-api.git
cd siscav-api
```

### 2. Configuração do Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto. Você pode copiar o arquivo `.env.example` (quando criado):

```bash
cp .env.example .env
```

Edite o arquivo `.env` com as credenciais do seu banco de dados e as chaves de segurança da aplicação:

```ini
# Configuração do PostgreSQL
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha_segura
POSTGRES_DB=siscav_db
POSTGRES_HOST=db # Nome do serviço no docker-compose.yml

# URL de Conexão do SQLAlchemy (deve corresponder às credenciais acima)
DATABASE_URL=postgresql+psycopg2://seu_usuario:sua_senha_segura@db/siscav_db

# Configuração do JWT
SECRET_KEY=sua_chave_secreta_muito_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Executar a Aplicação (Desenvolvimento)

Use o Docker Compose para construir as imagens e iniciar os contêineres da API e do banco de dados:

```bash
docker-compose up -d --build
```

A API estará acessível em http://localhost:8000.

### 4. Executar as Migrações (Alembic)

Após iniciar os contêineres, aplique as migrações do banco de dados para criar as tabelas (User, AuthorizedPlate, AccessLog):

```bash
docker-compose exec api alembic upgrade head
```

Para criar novas migrações após alterar os `models.py`:

```bash
docker-compose exec api alembic revision --autogenerate -m "Descrição da sua migração"
```

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

## Integração Contínua (CI) ✅

Este projeto utiliza **GitHub Actions** para integração contínua. O pipeline está configurado e funcional!

**Workflow:** `.github/workflows/ci.yml`

O pipeline é acionado automaticamente em **Pull Requests para a branch `develop`** e executa:

1. ✅ **Linting com Ruff** - Verifica qualidade e estilo do código
2. ✅ **Verificação de Formatação** - Garante código bem formatado  
3. ✅ **Testes Unitários com Pytest** - Executa todos os testes
4. 📊 **Relatório de Cobertura** - Gera relatório de cobertura (opcional)

### ⚠️ Bloqueio de Merge

O pipeline **bloqueia automaticamente** a mesclagem se:
- ❌ Houver erros de linting
- ❌ O código não estiver formatado corretamente
- ❌ Qualquer teste unitário falhar

### Testar Localmente

Antes de abrir um Pull Request, execute:

```bash
# Instalar dependências de dev
pip install -e ".[dev]"

# Simular o pipeline CI completo
ruff check . && ruff format --check . && pytest -v
```

📚 **Documentação detalhada:**
- **CI/CD Completo:** `.github/README_CI.md`
- **Guia Local:** `.github/CI_LOCAL_GUIDE.md`
- **Comandos Rápidos:** `.github/GUIA_COMANDOS.md`

## Documentação da API (Swagger)

Com a aplicação em execução, a documentação automática e interativa da API (Swagger UI) está disponível em:

* **Swagger UI:** http://localhost:8000/docs
* **ReDoc:** http://localhost:8000/redoc

## Roadmap

### Fase 1: Setup e Infraestrutura ✅
- [x] Estrutura básica do projeto
- [x] Configuração FastAPI
- [x] Definição de dependências (pyproject.toml)
- [ ] Dockerfile e docker-compose.yml
- [ ] Arquivo .env.example

### Fase 2: Banco de Dados e Autenticação 🔄
- [ ] Configuração PostgreSQL
- [ ] Modelos SQLAlchemy (User, AuthorizedPlate, AccessLog)
- [ ] Configuração Alembic para migrações
- [ ] Sistema de autenticação JWT
- [ ] Endpoints de login/logout
- [ ] Middleware de autenticação

### Fase 3: CRUD e API Principal 📋
- [ ] Endpoints CRUD para placas autorizadas
- [ ] Endpoint de registro de acesso (IoT)
- [ ] Endpoint de visualização de logs
- [ ] Endpoint de controle remoto do portão
- [ ] Rate limiting no login
- [ ] Validações com Pydantic

### Fase 4: Dispositivo IoT 🤖
- [ ] Script de captura de imagem
- [ ] Integração com EasyOCR (ALPR)
- [ ] Comunicação HTTPS com API
- [ ] Controle de GPIO para relé
- [ ] Tratamento de erros e retry logic

### Fase 5: Testes e CI/CD 🧪
- [x] Testes unitários (pytest)
- [x] GitHub Actions (CI/CD)
- [x] Linting automatizado (ruff)
- [x] Estrutura de testes básica
- [ ] Testes de integração
- [ ] Coverage reports avançados

### Fase 6: Documentação e Deploy 📚
- [ ] Documentação completa da API
- [ ] Guia de deploy em produção
- [ ] Configuração de HTTPS
- [ ] Monitoramento e logs

## Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue primeiro para discutir as mudanças que você gostaria de fazer.

### Workflow de Contribuição

1. **Fork** o repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Teste localmente** antes de commitar:
   ```bash
   ruff check . && ruff format --check . && pytest -v
   ```
4. **Commit** suas mudanças (`git commit -m 'feat: Adiciona MinhaFeature'`)
5. **Push** para a branch (`git push origin feature/MinhaFeature`)
6. Abra um **Pull Request** para a branch `develop`
7. Aguarde o **CI passar** ✅ e a **aprovação** do code review

📝 Use o template de PR automaticamente fornecido pelo GitHub.

## Documentação do Projeto

Este repositório contém documentação técnica detalhada na pasta `docs/`:

- **Arquitetura e Critérios de Aceite**: Critérios de aceitação para todas as tarefas (FND-01 a FND-08)
- **Arquitetura e Backlog**: Detalhamento da arquitetura e backlog do projeto
- **Especificação de Projeto**: Requisitos funcionais e não funcionais completos

📚 Consulte estes documentos para entender melhor o projeto e seus requisitos.

## Licença

Este projeto está em desenvolvimento acadêmico na UNICAP.

## Contato

- **Repositório:** https://github.com/JFMGDB/siscav-api
- **Frontend:** https://github.com/JFMGDB/siscav-web (em desenvolvimento)