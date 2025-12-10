# Guia de Instalação - SISCAV API

## Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Escopo e Objetivos](#escopo-e-objetivos)
3. [Arquitetura e Tecnologias](#arquitetura-e-tecnologias)
4. [Pré-requisitos](#pré-requisitos)
5. [Instalação da API Central](#instalação-da-api-central)
6. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
7. [Instalação do Dispositivo IoT](#instalação-do-dispositivo-iot)
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
5. **Controle de Acesso**: Se autorizada, o servidor aciona o portão através de um módulo relé conectado ao dispositivo IoT

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

#### Backend (API Central)
- **Framework**: FastAPI 0.104+
- **Linguagem**: Python 3.12
- **ORM**: SQLAlchemy 2.0+
- **Migrações**: Alembic
- **Validação**: Pydantic 2.0+
- **Autenticação**: JWT (python-jose)
- **Hashing**: Argon2 (passlib)
- **Rate Limiting**: slowapi
- **Banco de Dados**: PostgreSQL (Supabase ou local)

#### Dispositivo IoT
- **Linguagem**: Python 3.10, 3.11 ou 3.12
- **Visão Computacional**: OpenCV 4.8+
- **OCR**: EasyOCR 1.7+ (Deep Learning)
- **Processamento**: NumPy 1.24+
- **Comunicação**: HTTP/REST (requests)
- **Hardware**: Câmera USB, Módulo Relé (Arduino)

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

1. **users**: Usuários administradores do sistema
   - Campos: id (UUID), email, hashed_password, created_at, updated_at

2. **authorized_plates**: Lista de placas autorizadas
   - Campos: id (UUID), plate, normalized_plate, description, created_at, updated_at

3. **access_logs**: Registro de todas as tentativas de acesso
   - Campos: id (UUID), timestamp, plate_string_detected, status (ENUM), image_storage_key, authorized_plate_id (FK)

---

## Pré-requisitos

### Para a API Central

- **Python**: 3.12 (recomendado) ou 3.11
- **pip**: Versão atualizada
- **PostgreSQL**: 12+ (ou acesso a Supabase)
- **Git**: Para clonar o repositório

### Para o Dispositivo IoT

- **Python**: 3.10, 3.11 ou 3.12 (evitar 3.13+)
- **pip**: Versão atualizada
- **Câmera USB**: Para captura de imagens (opcional para testes)
- **Arduino com Módulo Relé**: Para controle do portão (opcional)

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
- `requirements.txt`: Dependências mínimas para executar a API
- `requirements-dev.txt`: Inclui `requirements.txt` + ferramentas de desenvolvimento (pytest, ruff, httpx, pyright)

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

Não é necessário criar arquivo `.env`. O sistema usará SQLite automaticamente como fallback se nenhuma configuração de PostgreSQL estiver disponível.

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

Não é necessária configuração adicional. O sistema criará automaticamente o arquivo `siscav_dev.db` na raiz do projeto na primeira execução.

### Criar Usuário Administrador

Após configurar o banco de dados, crie um usuário administrador. Você pode usar o script de seed:

```bash
python app/seed_demo.py
```

Ou criar manualmente via Python:

```python
from app.api.v1.db.session import SessionLocal
from app.api.v1.models.user import User
from app.api.v1.core.security import get_password_hash

db = SessionLocal()
try:
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("senha123")
    )
    db.add(admin)
    db.commit()
    print(f"Usuário criado: {admin.email}")
finally:
    db.close()
```

---

## Instalação do Dispositivo IoT

O dispositivo IoT está localizado em `app/iot-device/` e é responsável por:
- Capturar imagens da câmera
- Detectar placas usando visão computacional
- Extrair texto das placas usando OCR
- Enviar dados para a API central
- Controlar módulo relé para acionar portão

### 1. Navegar para o Diretório

```bash
cd app/iot-device
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

**Importante**: Use Python 3.10, 3.11 ou 3.12. Python 3.13+ pode ter problemas com wheels pré-compilados.

### 3. Instalar Dependências

**Windows (PowerShell) - Método Automático (Recomendado):**

```powershell
.\scripts\install_dependencies.ps1
```

O script detecta problemas automaticamente e oferece soluções.

**Windows (PowerShell) - Método Manual:**

```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Instalar NumPy (forçar wheel pré-compilado)
pip install --only-binary :all: numpy

# Instalar outras dependências
pip install opencv-python requests pyserial

# Instalar EasyOCR
pip install easyocr

# Verificar instalação
python -c "import numpy, cv2, easyocr, requests; print('Instalação OK!')"
```

**Se encontrar erro de compilação do NumPy:**
```powershell
.\scripts\fix_numpy_install.ps1
```

**Linux/Mac:**

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
python -c "import numpy, cv2, easyocr, requests; print('Instalação OK!')"
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` em `app/iot-device/` ou configure variáveis de ambiente:

```env
# URL da API Central
API_BASE_URL=http://localhost:8000
ACCESS_LOGS_ENDPOINT=http://localhost:8000/api/v1/access_logs

# Configurações da Câmera
CAMERA_INDEX=0
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720

# Configurações de Detecção
PLATE_DETECTION_COOLDOWN=5
DEMO_MODE=False
DEMO_WHITELIST=ABC1234,XYZ5678

# Configurações do Arduino (opcional)
ARDUINO_ENABLED=False
ARDUINO_PORT=COM3
ARDUINO_BAUD_RATE=9600

# Logging
LOG_LEVEL=INFO
ENABLE_DISPLAY=True
ENABLE_SOUND=False
```

**Nota**: Ajuste `API_BASE_URL` e `ACCESS_LOGS_ENDPOINT` para apontar para sua API central.

---

## Executando o Sistema

### 1. Iniciar a API Central

**Desenvolvimento (com reload automático):**
```bash
# Na raiz do projeto, com venv ativado
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Produção:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

### 2. Iniciar o Dispositivo IoT

**Modo Normal:**
```bash
# Em app/iot-device/, com venv ativado
python main.py
```

**Modo Demo (sem câmera):**
```bash
python run_demo.py
```

O dispositivo IoT irá:
1. Inicializar a câmera
2. Capturar frames continuamente
3. Detectar placas em cada frame
4. Extrair texto usando OCR
5. Enviar dados para a API central
6. Exibir resultados na tela (se `ENABLE_DISPLAY=True`)

### 3. Verificar Funcionamento

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

# Com verbose e cobertura
pytest -v --cov=app --cov-report=term-missing

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

**Sintoma**: `ModuleNotFoundError: No module named 'app'`

**Soluções**:
- Certifique-se de estar na raiz do projeto ao executar comandos
- Verifique se o ambiente virtual está ativado
- Reinstale as dependências: `pip install -r requirements-dev.txt`

#### 3. Erro de Compilação do NumPy (Dispositivo IoT)

**Sintoma**: `error: Microsoft Visual C++ 14.0 or greater is required`

**Soluções**:
- Use o script automático: `.\scripts\fix_numpy_install.ps1`
- Ou instale wheel pré-compilado: `pip install --only-binary :all: numpy`
- Considere usar Python 3.12 que tem melhor suporte a wheels

#### 4. Câmera Não Detectada (Dispositivo IoT)

**Sintoma**: `cv2.error: OpenCV(4.x) ... Can't initialize camera`

**Soluções**:
- Verifique se a câmera está conectada
- Teste com `CAMERA_INDEX=0, 1, 2...` no arquivo de configuração
- No Linux, verifique permissões: `sudo usermod -a -G video $USER`
- Use modo demo para testes sem câmera: `python run_demo.py`

#### 5. Token JWT Inválido

**Sintoma**: `Could not validate credentials`

**Soluções**:
- Verifique se o token não expirou (padrão: 15 minutos)
- Use o refresh token para obter novo access token
- Verifique se `SECRET_KEY` está configurada corretamente
- Certifique-se de incluir `Bearer ` antes do token no header

#### 6. Rate Limit Exceeded

**Sintoma**: `Rate limit exceeded: 5/minute`

**Soluções**:
- Aguarde 1 minuto antes de tentar novamente
- O rate limiting está configurado para 5 tentativas por minuto no endpoint de login
- Em produção, ajuste os limites em `app/api/v1/core/rate_limit.py`

### Logs e Debugging

**API Central:**
- Logs são exibidos no console onde o uvicorn está rodando
- Para mais detalhes, ajuste o nível de log no código

**Dispositivo IoT:**
- Logs são exibidos no console
- Configure `LOG_LEVEL=DEBUG` no arquivo de configuração para mais detalhes
- Logs incluem informações sobre detecção de placas, OCR e comunicação com API

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

### Por que EasyOCR?

- **Precisão**: Baseado em Deep Learning (CNN + RNN), superior a OCR tradicional
- **Multilíngue**: Suporta português e outros idiomas
- **Fácil Integração**: API simples e bem documentada
- **Open Source**: Sem custos de licenciamento

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
3. **Configurar Dispositivo IoT**: Ajuste configurações de câmera e Arduino conforme seu hardware
4. **Monitorar Logs**: Acompanhe os logs de acesso através da API ou interface web
5. **Personalizar**: Ajuste configurações de segurança, rate limiting e expiração de tokens conforme necessário

---

## Referências

- **Documentação da API**: `app/docs/`
- **Documentação Técnica**: `app/docs/technical-documentation.md`
- **Arquitetura**: `app/docs/architecture.md`
- **Endpoints**: `app/docs/endpoints.md`
- **Dispositivo IoT**: `app/iot-device/docs/`
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **Supabase**: https://supabase.com/docs

---

## Suporte

Para problemas ou dúvidas:
1. Consulte a documentação em `app/docs/`
2. Verifique os logs do sistema
3. Execute os testes para verificar integridade
4. Consulte o código-fonte para entender implementações específicas

