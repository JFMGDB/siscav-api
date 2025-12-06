# Reorganização Arquitetural: Padrão MVC com SOLID e DRY

## Visão Geral

Este documento descreve a reorganização arquitetural do projeto SISCAV-API, implementando o padrão MVC (Model-View-Controller) com princípios SOLID e DRY, utilizando FastAPI e Python.

## Data da Reorganização

2025-01-XX (data a ser preenchida)

## Contexto e Motivação

### Problemas Identificados na Estrutura Anterior

1. **Violação do Single Responsibility Principle (SOLID)**:
   - Endpoints continham lógica de negócio misturada com roteamento HTTP.
   - Funções CRUD continham validações e transformações de dados.
   - Difícil testar lógica de negócio isoladamente.

2. **Duplicação de Código (DRY)**:
   - Validação de arquivos repetida em múltiplos lugares.
   - Lógica de normalização de placas espalhada.
   - Processamento de imagens duplicado.

3. **Acoplamento Alto**:
   - Endpoints diretamente acoplados a funções CRUD.
   - Mudanças em lógica de negócio requeriam alterações em múltiplos arquivos.

4. **Dificuldade de Manutenção**:
   - Lógica de negócio espalhada dificultava localização e modificação.
   - Testes dependiam de múltiplas camadas simultaneamente.

## Arquitetura Proposta: MVC com Service Layer

### Estrutura de Camadas

```
┌─────────────────────────────────────────┐
│         Endpoints (Views)                │
│  - Roteamento HTTP                       │
│  - Validação de entrada/saída            │
│  - Dependências FastAPI                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Controllers (Service Layer)         │
│  - Lógica de negócio                    │
│  - Validações de regras de negócio      │
│  - Orquestração entre repositories       │
│  - Transformações de dados              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Repositories (Data Access)         │
│  - Operações de banco de dados         │
│  - Queries SQLAlchemy                  │
│  - Mapeamento Model <-> DB              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Models (SQLAlchemy)             │
│  - Definição de tabelas                 │
│  - Relacionamentos                      │
└─────────────────────────────────────────┘
```

## Decisões Arquiteturais

### 1. Repositories (Camada de Acesso a Dados)

**Decisão**: Criar classes Repository com métodos estáticos para operações de banco de dados puras.

**Justificativa**:
- **Single Responsibility**: Repositories são responsáveis APENAS por acesso a dados.
- **Testabilidade**: Fácil criar mocks para testes unitários.
- **Reutilização**: Lógica de acesso a dados pode ser reutilizada por diferentes controllers.

**Estrutura**:
```python
class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Apenas operação de banco de dados."""
        return db.scalar(select(User).where(User.id == user_id))
```

**Localização**: `apps/api/src/api/v1/repositories/`

**Repositories Criados**:
- `UserRepository`: Operações de banco de dados para usuários.
- `AuthorizedPlateRepository`: Operações de banco de dados para placas autorizadas.
- `AccessLogRepository`: Operações de banco de dados para logs de acesso.

### 2. Controllers (Camada de Lógica de Negócio)

**Decisão**: Criar classes Controller que orquestram operações entre repositories e aplicam regras de negócio.

**Justificativa**:
- **Separation of Concerns**: Lógica de negócio isolada dos endpoints.
- **Reutilização**: Controllers podem ser usados por diferentes endpoints ou serviços.
- **Testabilidade**: Lógica de negócio pode ser testada independentemente do HTTP.
- **Manutenibilidade**: Mudanças em regras de negócio ficam centralizadas.

**Estrutura**:
```python
class PlateController:
    def __init__(self, db: Session):
        self.db = db
        self.plate_repository = AuthorizedPlateRepository
    
    def create(self, plate_data: AuthorizedPlateCreate) -> AuthorizedPlate:
        # 1. Validar formato (regra de negócio)
        # 2. Normalizar placa (transformação)
        # 3. Verificar duplicatas (regra de negócio)
        # 4. Criar via repository (acesso a dados)
        pass
```

**Localização**: `apps/api/src/api/v1/controllers/`

**Controllers Criados**:
- `AuthController`: Autenticação, validação de credenciais, criação de tokens JWT.
- `PlateController`: Validação de placas, normalização, verificação de duplicatas, CRUD de placas.
- `AccessLogController`: Validação de arquivos, processamento de imagens, verificação de autorização.
- `GateController`: Controle de portão (preparado para integração futura com IoT).

### 3. Endpoints (Camada de Apresentação/Views)

**Decisão**: Simplificar endpoints para serem apenas camadas de roteamento HTTP, delegando lógica para controllers.

**Justificativa**:
- **Single Responsibility**: Endpoints apenas lidam com HTTP (roteamento, validação de entrada/saída).
- **Simplicidade**: Endpoints ficam mais limpos e fáceis de entender.
- **Manutenibilidade**: Mudanças em lógica de negócio não afetam endpoints.

**Estrutura Antes**:
```python
@router.post("/")
def create_access_log(...):
    # Validação de arquivo
    # Normalização de placa
    # Verificação de whitelist
    # Salvamento de imagem
    # Criação de log
    # ... 100+ linhas de lógica
```

**Estrutura Depois**:
```python
@router.post("/")
def create_access_log(...):
    controller = AccessLogController(db)
    return controller.create_access_log(plate=plate, file=file)
```

**Localização**: `apps/api/src/api/v1/endpoints/`

## Princípios SOLID Aplicados

### Single Responsibility Principle (SRP)

- **Repositories**: Responsáveis apenas por acesso a dados.
- **Controllers**: Responsáveis apenas por lógica de negócio.
- **Endpoints**: Responsáveis apenas por roteamento HTTP.

### Open/Closed Principle (OCP)

- Controllers podem ser estendidos sem modificar código existente.
- Novos tipos de validação podem ser adicionados sem alterar repositories.

### Liskov Substitution Principle (LSP)

- Repositories podem ser substituídos por implementações mock em testes.
- Controllers podem ser substituídos por implementações alternativas.

### Interface Segregation Principle (ISP)

- Cada repository expõe apenas os métodos necessários para seu domínio.
- Controllers expõem apenas métodos públicos necessários para endpoints.

### Dependency Inversion Principle (DIP)

- Endpoints dependem de abstrações (controllers), não de implementações concretas.
- Controllers dependem de abstrações (repositories), não de implementações concretas.

## Princípio DRY Aplicado

### Eliminação de Duplicação

**Antes**: Validação de arquivos duplicada em múltiplos lugares.
```python
# Em access_logs.py
if file.content_type not in ALLOWED_CONTENT_TYPES:
    raise HTTPException(...)

# Em outro arquivo (duplicado)
if file.content_type not in ALLOWED_CONTENT_TYPES:
    raise HTTPException(...)
```

**Depois**: Validação centralizada em `AccessLogController`.
```python
# Em AccessLogController
def validate_image_file(self, file: UploadFile) -> None:
    # Lógica única e reutilizável
    pass
```

**Benefícios**:
- Mudanças em validação requerem alteração em um único lugar.
- Consistência garantida em toda a aplicação.
- Redução de bugs por inconsistência.

## Fluxo de Dados

### Exemplo: Criar Placa Autorizada

1. **Endpoint** (`whitelist.py`):
   - Recebe requisição HTTP POST.
   - Valida schema Pydantic.
   - Cria instância de `PlateController`.
   - Chama `controller.create()`.

2. **Controller** (`plate_controller.py`):
   - Valida formato da placa (regra de negócio).
   - Normaliza placa (transformação).
   - Verifica duplicatas via `PlateRepository`.
   - Cria placa via `PlateRepository.create()`.
   - Retorna `AuthorizedPlate`.

3. **Repository** (`authorized_plate_repository.py`):
   - Executa query SQLAlchemy.
   - Persiste no banco de dados.
   - Retorna modelo SQLAlchemy.

4. **Endpoint**:
   - Serializa modelo para schema Pydantic.
   - Retorna resposta HTTP.

## Benefícios da Reorganização

### 1. Manutenibilidade
- Lógica de negócio centralizada e fácil de localizar.
- Mudanças isoladas em camadas específicas.
- Código mais limpo e organizado.

### 2. Testabilidade
- Controllers podem ser testados sem HTTP.
- Repositories podem ser mockados facilmente.
- Testes unitários mais rápidos e isolados.

### 3. Escalabilidade
- Fácil adicionar novos endpoints reutilizando controllers.
- Fácil adicionar novos controllers reutilizando repositories.
- Preparado para crescimento do projeto.

### 4. Consistência
- Regras de negócio aplicadas consistentemente.
- Validações centralizadas evitam inconsistências.
- Padrão claro para novos desenvolvedores.

## Migração de Código Antigo

### Módulos CRUD Obsoletos

Os seguintes módulos estão **depreciados** e serão removidos em versão futura:

- `apps/api/src/api/v1/crud/crud_user.py`
- `apps/api/src/api/v1/crud/crud_authorized_plate.py`
- `apps/api/src/api/v1/crud/crud_access_log.py`

### Como Migrar

**Antes**:
```python
from apps.api.src.api.v1.crud import crud_user

user = crud_user.get_by_email(db, email)
```

**Depois**:
```python
from apps.api.src.api.v1.repositories.user_repository import UserRepository

user = UserRepository.get_by_email(db, email)
```

**Para Lógica de Negócio**:
```python
from apps.api.src.api.v1.controllers.plate_controller import PlateController

controller = PlateController(db)
plate = controller.create(plate_data)
```

## Estrutura de Diretórios Final

```
apps/api/src/api/v1/
├── controllers/          # Lógica de negócio (Service Layer)
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── plate_controller.py
│   ├── access_log_controller.py
│   └── gate_controller.py
├── repositories/         # Acesso a dados (Data Access Layer)
│   ├── __init__.py
│   ├── user_repository.py
│   ├── authorized_plate_repository.py
│   └── access_log_repository.py
├── endpoints/           # Roteamento HTTP (Views)
│   ├── auth.py
│   ├── whitelist.py
│   ├── access_logs.py
│   └── gate_control.py
├── models/             # Modelos SQLAlchemy
├── schemas/            # Schemas Pydantic
├── core/               # Configurações e segurança
└── db/                 # Setup do banco de dados
```

## Referências

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [DRY Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)

## Conclusão

A reorganização arquitetural implementa padrões de mercado (MVC, Repository, Service Layer) seguindo princípios SOLID e DRY, resultando em código mais manutenível, testável e escalável. A separação clara de responsabilidades facilita o desenvolvimento futuro e a manutenção do projeto.

