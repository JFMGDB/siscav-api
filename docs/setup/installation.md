# Guia de Instalação - SISCAV API

## Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Escopo e Objetivos](#escopo-e-objetivos)
3. [Arquitetura e Tecnologias](#arquitetura-e-tecnologias)
4. [Pré-requisitos](#pré-requisitos)
5. [Instalação da API Central](#instalação-da-api-central)
6. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
7. [Integração com cliente de borda (ALPR/IoT)](#integração-com-cliente-de-borda-alpriot)
8. [Executando o Sistema](#executando-o-sistema)
9. [Verificação e Testes](#verificação-e-testes)
10. [Troubleshooting](#troubleshooting)

---

## Visão Geral do Projeto

O **SISCAV (Sistema de Controle de Acesso Veicular)** é uma solução completa de controle de acesso automatizado que combina **IoT (Internet of Things)** e **IA (Inteligência Artificial)** para reconhecimento automático de placas veiculares.

### Fluxo de Funcionamento

1. **Captura de Imagem**: Um dispositivo IoT com câmera captura a imagem do veículo em um ponto de acesso
2. **Reconhecimento de Placa**: O sistema utiliza visão computacional (OpenCV) e OCR (EasyOCR) para detectar e extrair o texto da placa
3. **Validação Central**: Os dados são enviados ao servidor central via API REST
4. **Verificação de Autorização**: O servidor valida a placa contra uma lista de placas autorizadas (whitelist)
5. **Controle de Acesso**: Se autorizada, a decisão fica registrada; o acionamento físico do portão pode ser feito via **`GATE_ACTUATOR_URL`** (HTTP no servidor) ou por outro sistema na borda — não há firmware obrigatório neste repositório

---

## Escopo e Objetivos

### Objetivos Principais

- **Automação Completa**: Eliminar necessidade de intervenção humana no controle de acesso
- **Reconhecimento Preciso**: Utilizar IA para reconhecimento automático de placas brasileiras (formato antigo ABC1234 e Mercosul ABC1D23)
- **Rastreabilidade**: Registrar todas as tentativas de acesso com imagens e timestamps
- **Segurança**: Implementar autenticação robusta e controle de acesso baseado em roles
- **Escalabilidade**: Arquitetura preparada para múltiplos pontos de acesso simultâneos

### Funcionalidades Implementadas

- Sistema de autenticação JWT com refresh tokens
- CRUD completo de placas autorizadas (whitelist)
- Registro de logs de acesso com imagens
- Sistema de filtros e paginação para consulta de logs
- Endpoint público para recebimento de dados do dispositivo IoT
- Controle remoto de portão (acionamento via API)
- Rate limiting para prevenção de ataques de força bruta
- Validação e normalização automática de placas brasileiras

---

## Arquitetura e Tecnologias

### Stack Tecnológica

#### Backend (API Central) — versões pinadas em `pyproject.toml`
- **Framework**: FastAPI 0.135.x
- **Linguagem**: Python compatível com o projeto; **CI** usa Python **3.13** (`.github/workflows/ci.yml`); `ruff.toml` usa `target-version = "py313"`.
- **ORM**: SQLAlchemy 2.0.x
- **Migrações**: Alembic (`alembic.ini` na raiz; revisões em `apps/api/src/alembic/versions/`)
- **Validação**: Pydantic 2.x
- **Autenticação**: JWT (`python-jose`), refresh tokens
- **Hashing**: Argon2 (`passlib`)
- **Rate Limiting**: slowapi
- **Banco de Dados**: PostgreSQL (Supabase ou local) ou SQLite em desenvolvimento

#### Cliente de borda (ALPR / IoT)

**Não faz parte deste repositório.** Um dispositivo ou serviço externo pode capturar a placa (OpenCV, EasyOCR, etc.) e enviar **`POST /api/v1/access_logs/`** (multipart). Veja [`docs/api/README.md`](../api/README.md).

### Padrões Arquiteturais

O projeto segue rigorosamente os princípios **SOLID** e **DRY**, utilizando o padrão **MVC (Model-View-Controller)** com uma camada adicional de Service Layer:

```
┌─────────────────────────────────┐
│   Endpoints (Views)              │  ← Roteamento HTTP, validação I/O
├─────────────────────────────────┤
│   Controllers (Service Layer)   │  ← Lógica de negócio, orquestração
├─────────────────────────────────┤
│   Repositories (Data Access)    │  ← Operações de banco de dados
├─────────────────────────────────┤
│   Models (SQLAlchemy ORM)       │  ← Estrutura e mapeamento de dados
└─────────────────────────────────┘
```

#### Princípios SOLID Aplicados

1. **Single Responsibility**: Cada camada possui responsabilidade única e bem definida
2. **Open/Closed**: Extensível sem modificar código existente
3. **Liskov Substitution**: Repositories podem ser substituídos por mocks em testes
4. **Interface Segregation**: Interfaces específicas e focadas
5. **Dependency Inversion**: Dependências injetadas via FastAPI Depends

#### Princípio DRY Aplicado

- Validações centralizadas em utilitários (`utils/plate.py`)
- Lógica de negócio reutilizável em controllers
- Funções compartilhadas em módulos `core/`

### Estrutura do Banco de Dados

O sistema utiliza três tabelas principais:

1. **users**: Usuários do sistema
   - Campos: id (UUID), email, hashed_password, **is_admin** (boolean), created_at, updated_at

2. **authorized_plates**: Lista de placas autorizadas
   - Campos: id (UUID), plate, normalized_plate, description, created_at, updated_at

3. **access_logs**: Registro de todas as tentativas de acesso
   - Campos: id (UUID), timestamp, plate_string_detected, status (ENUM), image_storage_key, authorized_plate_id (FK)

---

## Pré-requisitos

### Para a API Central

- **Python**: 3.11+ recomendado; alinhe com CI (3.13) quando possível
- **pip**: Versão atualizada
- **PostgreSQL**: 12+ (ou acesso a Supabase), ou SQLite para desenvolvimento rápido
- **Git**: Para clonar o repositório

### Para um cliente ALPR / IoT (fora deste repo)

Depende do seu projeto de borda (Python, embarcado, etc.). O contrato com **esta** API está em [`docs/api/README.md`](../api/README.md).

### Opcional

- **Docker**: Para executar PostgreSQL localmente
- **Postman/Insomnia**: Para testar endpoints da API
- **VS Code**: Editor recomendado com extensões Python

---

## Instalação da API Central

### 1. Clonar o Repositório

```bash
git clone https://github.com/JFMGDB/siscav-api.git
cd siscav-api
```

### 2. Criar Ambiente Virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Nota**: Se você tiver múltiplas versões do Python instaladas, use `python3.12` ou `py -3.12` no Windows.

### 3. Instalar Dependências

**Para desenvolvimento (recomendado):**
```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

**Para produção:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Diferença entre os arquivos:**
- `requirements.txt`: Dependências de execução da API com versões fixas (`==`) para instalações reproduzíveis
- `requirements-dev.txt`: Inclui `requirements.txt` + ferramentas de desenvolvimento (pytest, pytest-cov, ruff, httpx), também pinadas

O pipeline de CI (`.github/workflows/ci.yml`) usa **Python 3.13** e `pip install -r requirements-dev.txt` antes de `ruff` e `pytest`.

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto baseado nos exemplos fornecidos:

**Opção A: Usando Supabase (Recomendado para produção)**

Copie `env.supabase.example` para `.env.supabase` e configure:

```bash
cp env.supabase.example .env.supabase
```

Edite `.env.supabase` com suas credenciais do Supabase:

```env
DATABASE_URL=postgresql+psycopg2://postgres:[SUA_SENHA]@db.[ID_PROJETO].supabase.co:5432/postgres?sslmode=require

SECRET_KEY=sua_chave_secreta_aleatoria_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
```

**Importante**: 
- Substitua `[SUA_SENHA]` pela senha do seu banco Supabase
- Substitua `[ID_PROJETO]` pelo ID do seu projeto Supabase
- Se a senha contiver caracteres especiais, faça URL-encode (ex: `?` → `%3F`)
- Gere uma `SECRET_KEY` forte (pode usar: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

**Opção B: PostgreSQL Local (Docker)**

Copie `env.local.example` para `.env.local`:

```bash
cp env.local.example .env.local
```

Edite `.env.local`:

```env
POSTGRES_USER=siscav_user
POSTGRES_PASSWORD=siscav_password
POSTGRES_DB=siscav_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

SECRET_KEY=sua_chave_secreta_aleatoria_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
```

**Opção C: SQLite (Desenvolvimento rápido)**

Defina `DATABASE_URL` apontando para SQLite (ex.: `sqlite:///./siscav_dev.db`). Você pode usar `.env.local` ou exportar a variável; sem `DATABASE_URL`, a aplicação pode usar o fallback configurado em código.

Na **primeira execução**, o schema **não** é criado ao importar a API. Com o repositório como diretório atual (onde está `alembic.ini`), execute:

```powershell
$env:PYTHONPATH = $PWD   # se necessário
alembic upgrade head
```

Depois inicie o servidor normalmente.

### 5. Carregar Variáveis de Ambiente

**Windows (PowerShell):**
```powershell
# Para Supabase
Get-Content .env.supabase | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}

# Para PostgreSQL local
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
```

**Linux/Mac:**
```bash
# Para Supabase
export $(cat .env.supabase | grep -v '^#' | xargs)

# Para PostgreSQL local
export $(cat .env.local | grep -v '^#' | xargs)
```

**Alternativa (usando python-dotenv):**

Se preferir, instale `python-dotenv` e crie um arquivo `.env` na raiz:

```bash
pip install python-dotenv
```

Crie `.env` com o conteúdo de `.env.supabase` ou `.env.local`.

---

## Configuração do Banco de Dados

### Opção A: Supabase (Recomendado)

#### 1. Criar Projeto no Supabase

1. Acesse [https://supabase.com](https://supabase.com)
2. Crie uma conta ou faça login
3. Crie um novo projeto
4. Anote o ID do projeto e a senha do banco de dados

#### 2. Executar Scripts SQL

No Supabase Studio, acesse o **SQL Editor** e execute os scripts na ordem:

1. **Habilitar Extensões** (`db/sql/supabase/01_enable_extensions.sql`):
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

2. **Criar Tipos ENUM** (`db/sql/supabase/02_types.sql`):
```sql
CREATE TYPE access_status AS ENUM ('Authorized', 'Denied');
```

3. **Criar Tabelas** (`db/sql/supabase/03_tables.sql`):
```sql
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS authorized_plates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plate TEXT NOT NULL,
  normalized_plate TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "timestamp" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  plate_string_detected TEXT NOT NULL,
  status access_status NOT NULL,
  image_storage_key TEXT NOT NULL,
  authorized_plate_id UUID REFERENCES authorized_plates(id) ON DELETE SET NULL
);
```

4. **Criar Índices** (`db/sql/supabase/04_indexes.sql`):
```sql
-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_access_logs_status ON access_logs(status);
CREATE INDEX IF NOT EXISTS idx_access_logs_plate ON access_logs(plate_string_detected);
CREATE INDEX IF NOT EXISTS idx_authorized_plates_normalized ON authorized_plates(normalized_plate);

-- Índices com pg_trgm para busca fuzzy (opcional)
CREATE INDEX IF NOT EXISTS idx_access_logs_plate_trgm ON access_logs USING gin(plate_string_detected gin_trgm_ops);
```

#### 3. Sincronizar Alembic

Após criar as tabelas manualmente, sincronize o Alembic sem executar migrações:

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL='postgresql+psycopg2://postgres:[SENHA]@db.[ID].supabase.co:5432/postgres?sslmode=require'
alembic stamp head
```

**Linux/Mac:**
```bash
export DATABASE_URL='postgresql+psycopg2://postgres:[SENHA]@db.[ID].supabase.co:5432/postgres?sslmode=require'
alembic stamp head
```

**Nota**: Substitua `[SENHA]` e `[ID]` pelos valores reais do seu projeto Supabase.

### Opção B: PostgreSQL Local (Docker)

#### 1. Executar PostgreSQL via Docker

```bash
docker run --name siscav-postgres \
  -e POSTGRES_USER=siscav_user \
  -e POSTGRES_PASSWORD=siscav_password \
  -e POSTGRES_DB=siscav_db \
  -p 5432:5432 \
  -d postgres:15
```

#### 2. Executar Migrações com Alembic

```bash
# Garantir que as variáveis de ambiente estão configuradas
alembic upgrade head
```

### Opção C: SQLite (Desenvolvimento)

1. Configure `DATABASE_URL=sqlite:///./siscav_dev.db` (ou outro caminho de arquivo SQLite).
2. Na raiz do repositório, com `PYTHONPATH` apontando para o projeto se necessário, execute **`alembic upgrade head`** para criar/atualizar as tabelas via migrações.
3. Inicie a API. O arquivo `.db` aparece quando o SQLite ou o Alembic abrem essa URL pela primeira vez — não há mais criação implícita de tabelas no `session.py`.

### Criar Usuário Administrador

Após configurar o banco de dados, crie um usuário administrador. Você pode usar o script de seed:

```bash
# From repo root with PYTHONPATH=. set
python scripts/seed_demo.py
```

See `scripts/seed_demo.py` for default credentials — **do not use in production**.

Ou criar manualmente via Python:

```python
from apps.api.src.api.v1.db.session import SessionLocal
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.core.security import get_password_hash

db = SessionLocal()
try:
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("senha123"),
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    print(f"Usuário criado: {admin.email}")
finally:
    db.close()
```

---

## Integração com cliente de borda (ALPR/IoT)

Este repositório **não inclui** um cliente ALPR embarcado. Qualquer cliente (outro repositório, firmware, gateway) deve:

1. Obter a string da placa (OCR, LPR comercial, leitura manual em testes, etc.).
2. Enviar **`POST /api/v1/access_logs/`** com `multipart/form-data`: campo **`plate`** e arquivo **`file`** (imagem).
3. Se o servidor tiver **`DEVICE_INGEST_KEY`** definido (fora de ambiente de desenvolvimento), enviar o header **`X-Device-Key`** com o mesmo valor.

Detalhes e links: **[`docs/api/README.md`](../api/README.md)**.

Para testar sem cliente físico, use Swagger em `/docs` ou a coleção Postman em `docs/`.

---

## Executando o Sistema

### 1. Iniciar a API Central

Na **raiz do repositório**, com venv ativado e dependências instaladas:

**Desenvolvimento (reload):**
```bash
export PYTHONPATH=.   # PowerShell: $env:PYTHONPATH = (Get-Location).Path
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000
```

**Alternativa:** entrar em `apps/api/src` e rodar `uvicorn main:app --reload --host 0.0.0.0 --port 8000`.

**Windows (PowerShell), a partir da raiz:**
```powershell
.\scripts\start_server.ps1
```

**Produção (exemplo):**
```bash
uvicorn apps.api.src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

Guia rápido adicional: **[`init-server-guide.md`](init-server-guide.md)**.

### 2. Cliente de borda

Implementação **fora** deste repositório; ver seção [Integração com cliente de borda](#integração-com-cliente-de-borda-alpriot) acima.

### 3. Verificar funcionamento

1. **Health Check da API:**
```bash
curl http://localhost:8000/api/v1/health
```

2. **Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=senha123"
```

3. **Criar Placa Autorizada:**
```bash
curl -X POST "http://localhost:8000/api/v1/whitelist" \
  -H "Authorization: Bearer [SEU_TOKEN]" \
  -H "Content-Type: application/json" \
  -d '{"plate": "ABC1234", "description": "Veículo autorizado"}'
```

---

## Verificação e Testes

### Executar Testes Unitários

```bash
# Na raiz do projeto, com venv ativado
pytest

# Com verbose e cobertura (fonte: pacote `apps`)
pytest -v --cov=apps --cov-report=term-missing

# Executar testes específicos
pytest tests/test_main.py
```

### Verificar Linting

```bash
# Verificar problemas
ruff check .

# Corrigir automaticamente
ruff check --fix .

# Formatar código
ruff format .
```

### Testar Endpoints Manualmente

Use a documentação interativa do Swagger em http://localhost:8000/docs para testar os endpoints diretamente no navegador.

---

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão com Banco de Dados

**Sintoma**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Soluções**:
- Verifique se o PostgreSQL está rodando (se local)
- Verifique se as credenciais no `.env` estão corretas
- Verifique se a URL do Supabase está correta (incluindo `sslmode=require`)
- Teste a conexão manualmente: `psql -h [HOST] -U [USER] -d [DB]`

#### 2. Erro de Importação de Módulos

**Sintoma**: `ModuleNotFoundError: No module named 'apps'`

**Soluções**:
- Defina `PYTHONPATH` para a **raiz** do repositório ao usar `uvicorn apps.api.src.main:app`
- Ou execute a partir de `apps/api/src` com `uvicorn main:app`
- Use `.\scripts\start_server.ps1` no Windows a partir da raiz
- Verifique se o ambiente virtual está ativado e rode `pip install -r requirements-dev.txt`

#### 3. Token JWT Inválido

**Sintoma**: `Could not validate credentials`

**Soluções**:
- Verifique se o token não expirou (padrão: 15 minutos)
- Use o refresh token para obter novo access token
- Verifique se `SECRET_KEY` está configurada corretamente
- Certifique-se de incluir `Bearer ` antes do token no header

#### 4. Rate Limit Exceeded

**Sintoma**: `Rate limit exceeded: 5/minute`

**Soluções**:
- Aguarde 1 minuto antes de tentar novamente
- O rate limiting está configurado para 5 tentativas por minuto no endpoint de login
- Em produção, ajuste os limites em `apps/api/src/api/v1/core/limiter.py`

### Logs e Debugging

**API Central:**
- Logs são exibidos no console onde o uvicorn está rodando
- Para mais detalhes, ajuste o nível de log no código

**Cliente de borda (fora deste repo):** depuração fica a cargo do seu aplicativo ou firmware.

---

## Decisões Arquiteturais

### Por que FastAPI?

- **Performance**: Suporte nativo a async/await, crucial para múltiplas requisições simultâneas de dispositivos IoT
- **Documentação Automática**: Geração nativa de OpenAPI/Swagger
- **Validação Robusta**: Integração forte com Pydantic para validação de dados
- **Type Hints**: Suporte completo a type hints do Python, melhorando manutenibilidade

### Por que MVC com Service Layer?

- **Separação de Responsabilidades**: Cada camada tem responsabilidade única e bem definida
- **Testabilidade**: Cada camada pode ser testada isoladamente
- **Manutenibilidade**: Mudanças localizadas e seguras
- **Escalabilidade**: Preparado para crescimento e adição de novas funcionalidades

### Por que Repository Pattern?

- **Abstração**: Isola detalhes de implementação do banco de dados
- **Flexibilidade**: Facilita mudanças de SGBD ou estratégias de persistência
- **Testabilidade**: Permite mocks em testes unitários
- **Centralização**: Queries complexas centralizadas e otimizáveis

### Por que JWT?

- **Stateless**: Não requer armazenamento de sessão no servidor
- **Escalabilidade**: Permite múltiplas instâncias da API sem compartilhamento de estado
- **Segurança**: Tokens assinados e validados a cada requisição
- **Padrão da Indústria**: Amplamente adotado e bem documentado

### Por que PostgreSQL?

- **Robustez**: Banco de dados relacional maduro e confiável
- **Recursos Avançados**: Suporte a tipos customizados (ENUM), índices GIN (pg_trgm)
- **Escalabilidade**: Preparado para grandes volumes de dados
- **Supabase**: Integração fácil com Supabase para deploy rápido

---

## Próximos Passos

Após a instalação bem-sucedida:

1. **Configurar Usuários**: Crie usuários administradores via script de seed ou manualmente
2. **Adicionar Placas**: Adicione placas autorizadas via API ou interface web
3. **Integrar cliente de borda**: implemente ou recupere um cliente que chame `POST /api/v1/access_logs/` (ver `docs/api/README.md`)
4. **Monitorar Logs**: Acompanhe os logs de acesso através da API ou interface web
5. **Personalizar**: Ajuste configurações de segurança, rate limiting e expiração de tokens conforme necessário

---

## Referências

- **Documentação geral**: `docs/README.md`
- **Documentação da API (técnica)**: `docs/api/technical-documentation.md`
- **Modelo de dados**: `docs/database/data-model.md`
- **Integração frontend**: `docs/api/frontend-integration.md`
- **Contrato de ingestão / borda**: `docs/api/README.md`
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Supabase**: https://supabase.com/docs

---

## Suporte

Para problemas ou dúvidas:
1. Consulte a documentação em `docs/`
2. Verifique os logs do sistema
3. Execute os testes para verificar integridade
4. Consulte o código-fonte para entender implementações específicas