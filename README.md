# siscav-api: Backend do Sistema de Controle de Acesso de Veículos

Este é o repositório backend para o "Sistema de Controle de Acesso de Veículos".

## Visão Geral

A arquitetura geral do projeto é dividida em dois repositórios distintos: `siscav-api` (este) e `siscav-web` (frontend).

Este repositório (`siscav-api`) contém toda a lógica do lado do servidor e é composto por duas aplicações Python principais:

1.  **API Central (`apps/api`):** Um serviço backend robusto construído com **FastAPI**. Ele serve como o "cérebro" do sistema, utilizando um banco de dados **PostgreSQL** para:
    * Autenticar administradores.
    * Validar placas de veículos recebidas contra uma "whitelist".
    * Registrar cada tentativa de acesso (com foto).
    * Enviar comandos de acionamento para o portão.
2.  **Script IoT (`apps/iot-device`):** Um script Python projetado para ser executado no dispositivo de borda (ex: Raspberry Pi). Este script utiliza a biblioteca **`easyocr`** para realizar o Reconhecimento Automático de Placas de Veículos (ALPR). Após capturar e processar a imagem de um veículo, ele envia os dados via `POST HTTPS` seguro para a API Central e aguarda uma resposta (`Autorizado`/`Negado`) para acionar o relé físico via `GPIO`.

## Principais Funcionalidades

* **Autenticação:** Sistema seguro de login para administradores baseado em **JWT**.
* **Gerenciamento (CRUD):** Endpoints completos para Criar, Ler, Atualizar e Deletar placas na lista de veículos autorizados (whitelist).
* **Registro de Acesso:** Endpoint para o dispositivo IoT submeter dados (placa, imagem), com cada tentativa sendo registrada de forma persistente no banco de dados.
* **Visualização de Logs:** Endpoint para o frontend buscar o histórico de logs de acesso, com suporte a filtragem por placa, intervalo de datas e status.
* **Controle Remoto:** Endpoint que permite a um administrador autenticado acionar a abertura do portão remotamente através do painel web.
* **Segurança:** Implementa limitação de taxa (rate limiting) no endpoint de login para prevenir força bruta e exige comunicação criptografada (HTTPS) do dispositivo IoT.

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
controle-acesso-veicular-api/
├── .github/
│   └── workflows/
│       └── ci.yml          # Pipeline de CI (Lint, Test)
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
│   └── iot-device/         # Script Python ALPR (easyocr)
├── .env.example            # Arquivo de exemplo para variáveis de ambiente
├── .gitignore
├── docker-compose.yml      # Orquestra a API e o DB PostgreSQL
├── pyproject.toml          # Dependências (FastAPI, SQLAlchemy, Alembic...)
└── README.md
```

## Guia de Instalação (Getting Started)

Este guia detalha como configurar e executar o ambiente de desenvolvimento local usando Docker.

### Pré-requisitos

* Docker
* Docker Compose

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/siscav-api.git
cd siscav-api
```

### 2. Configuração do Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto. Você pode copiar o arquivo `.env.example`:

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

## Testes

O pipeline de CI executa testes automatizados usando pytest. Para executá-los localmente:

```bash
docker-compose exec api pytest
```

## Integração Contínua (CI)

Este projeto utiliza GitHub Actions para integração contínua. O fluxo de trabalho, definido em `.github/workflows/ci.yml`, é acionado em cada pull request para a branch develop e executa os seguintes passos:

* **Linting:** Verifica a qualidade e o estilo do código (ex: ruff ou flake8).
* **Testes:** Executa a suíte de testes unitários com pytest.

## Documentação da API (Swagger)

Com a aplicação em execução, a documentação automática e interativa da API (Swagger UI) está disponível em:

* **Swagger UI:** http://localhost:8000/docs
* **ReDoc:** http://localhost:8000/redoc

