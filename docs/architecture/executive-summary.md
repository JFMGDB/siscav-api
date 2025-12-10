# Resumo Executivo - Arquitetura SISCAV-API

## Visão Geral

O Sistema de Controle de Acesso Veicular (SISCAV) é uma solução completa que integra IoT, Inteligência Artificial e automação para controle de acesso veicular. Este documento apresenta um resumo executivo das decisões arquiteturais principais do backend.

## Arquitetura de Alto Nível

O sistema segue uma arquitetura de três camadas:

1. **Camada de Borda (IoT)**: Dispositivos com câmera e processamento local de reconhecimento de placas
2. **Camada de Servidor (Backend)**: API FastAPI centralizada com padrão MVC
3. **Camada de Cliente (Frontend)**: Painel de administração web (repositório separado)

## Padrão Arquitetural: MVC com Service Layer

### Estrutura de Camadas

```
┌─────────────────────────────────┐
│   Endpoints (Views)             │  ← Roteamento HTTP
│   - Validação de entrada/saída  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Controllers (Service Layer)   │  ← Lógica de Negócio
│   - Validações                  │
│   - Orquestração                │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Repositories (Data Access)    │  ← Acesso a Dados
│   - Queries SQLAlchemy          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Models (SQLAlchemy)           │  ← Estrutura do BD
└─────────────────────────────────┘
```

## Princípios Aplicados

### SOLID

- **Single Responsibility**: Cada camada tem uma única responsabilidade bem definida
- **Open/Closed**: Extensível sem modificar código existente
- **Liskov Substitution**: Repositories podem ser substituídos por mocks em testes
- **Interface Segregation**: Cada repository expõe apenas métodos necessários
- **Dependency Inversion**: Dependências de abstrações, não implementações

### DRY (Don't Repeat Yourself)

- Validações centralizadas em controllers
- Lógica de negócio reutilizável
- Utilitários compartilhados
- Eliminação de duplicação de código

### MVC (Model-View-Controller)

- **Models**: SQLAlchemy ORM (estrutura do banco de dados)
- **Views**: Endpoints FastAPI (roteamento HTTP)
- **Controllers**: Service Layer (lógica de negócio)

## Componentes Principais

### Repositories (Data Access Layer)

Responsabilidade: Apenas operações de banco de dados.

- `UserRepository`: Operações de banco para usuários
- `AuthorizedPlateRepository`: Operações de banco para placas autorizadas
- `AccessLogRepository`: Operações de banco para logs de acesso

### Controllers (Service Layer)

Responsabilidade: Lógica de negócio e orquestração.

- `AuthController`: Autenticação, validação de credenciais, tokens JWT
- `PlateController`: Validação de placas, normalização, CRUD de whitelist
- `AccessLogController`: Validação de arquivos, processamento de imagens, verificação de autorização
- `GateController`: Controle de portão (preparado para integração IoT)

### Endpoints (Views)

Responsabilidade: Roteamento HTTP e validação de entrada/saída.

- `auth.py`: Autenticação e login
- `whitelist.py`: CRUD de placas autorizadas
- `access_logs.py`: Registro e consulta de logs de acesso
- `gate_control.py`: Controle remoto do portão
- `devices.py`: Gerenciamento de dispositivos IoT
- `health.py`: Health check da API

## Tecnologias e Ferramentas

### Backend

- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLAlchemy
- **Validação**: Pydantic
- **Banco de Dados**: PostgreSQL (produção) / SQLite (desenvolvimento)
- **Autenticação**: JWT (python-jose)
- **Hashing**: Argon2 (passlib)
- **Migrações**: Alembic
- **Rate Limiting**: slowapi

### DevOps

- **CI/CD**: GitHub Actions
- **Linting**: Ruff
- **Testes**: Pytest
- **Containerização**: Docker, Docker Compose

## Estrutura de Diretórios

```
apps/api/src/api/v1/
├── controllers/      # Service Layer - Lógica de negócio
├── repositories/     # Data Access Layer - Acesso a dados
├── endpoints/        # Views - Roteamento HTTP
├── models/          # SQLAlchemy Models
├── schemas/         # Pydantic Schemas
├── core/           # Configurações e segurança
├── db/             # Setup do banco de dados
└── utils/          # Utilitários compartilhados
```

## Decisões Arquiteturais Principais

### 1. Separação de Repositórios

**Decisão**: Backend e frontend em repositórios separados.

**Justificativa**:
- Tecnologias diferentes (Python vs JavaScript/TypeScript)
- Ciclos de vida independentes
- Autonomia das equipes
- Gerenciamento de dependências simplificado

### 2. Padrão MVC com Service Layer

**Decisão**: Implementar MVC com Repository Pattern e Service Layer.

**Justificativa**:
- Separação clara de responsabilidades (SOLID)
- Facilita testes unitários
- Melhora manutenibilidade
- Permite escalabilidade

### 3. FastAPI como Framework

**Decisão**: Usar FastAPI em vez de Flask ou Django.

**Justificativa**:
- Alta performance (comparable a Node.js)
- Documentação automática (OpenAPI/Swagger)
- Validação automática com Pydantic
- Type hints nativos
- Suporte assíncrono

### 4. PostgreSQL como Banco Principal

**Decisão**: PostgreSQL para produção, SQLite para desenvolvimento.

**Justificativa**:
- Robusto e confiável
- Suporte a tipos avançados (UUID, ENUM, JSON)
- Transações ACID
- Escalabilidade
- SQLite para desenvolvimento rápido

### 5. JWT para Autenticação

**Decisão**: Usar JWT (JSON Web Tokens) para autenticação stateless.

**Justificativa**:
- Stateless (não requer sessões no servidor)
- Escalável (funciona com múltiplos servidores)
- Padrão da indústria
- Seguro quando configurado corretamente

## Fluxo de Dados Típico

### Exemplo: Criar Placa Autorizada

1. **Cliente** → Envia requisição HTTP POST para `/api/v1/whitelist/`
2. **Endpoint** → Valida schema Pydantic, cria `PlateController`
3. **Controller** → Valida formato da placa, normaliza, verifica duplicatas
4. **Repository** → Executa query SQLAlchemy, persiste no banco
5. **Controller** → Retorna `AuthorizedPlate`
6. **Endpoint** → Serializa para schema Pydantic
7. **Cliente** ← Recebe resposta HTTP com placa criada

## Benefícios da Arquitetura

### Manutenibilidade

- Código organizado e fácil de navegar
- Lógica de negócio centralizada
- Mudanças isoladas em camadas específicas

### Testabilidade

- Controllers testáveis sem HTTP
- Repositories mockáveis facilmente
- Testes unitários rápidos e isolados

### Escalabilidade

- Fácil adicionar novos endpoints
- Fácil adicionar novos controllers
- Preparado para crescimento

### Consistência

- Regras de negócio aplicadas uniformemente
- Validações centralizadas
- Padrões claros para novos desenvolvedores

## Documentação Relacionada

- **Detalhes da Reorganização**: `../development/coding-standards.md`
- **Backlog e Estrutura**: `../archive/architecture-backlog.md` (arquivado - estrutura obsoleta)
- **Critérios de Aceite**: `acceptance-criteria-devops.md`
- **Especificação do Projeto**: `../requirements/project-specification.md`
- **Documentação da API**: `../api/technical-documentation.md`

## Conclusão

A arquitetura implementada segue práticas de mercado e princípios de engenharia de software, resultando em um sistema:

- **Manutenível**: Código organizado e bem documentado
- **Testável**: Camadas isoladas e facilmente testáveis
- **Escalável**: Estrutura preparada para crescimento
- **Consistente**: Padrões aplicados uniformemente
- **Profissional**: Seguindo melhores práticas da indústria

Esta arquitetura fornece uma base sólida para o desenvolvimento contínuo e manutenção do sistema SISCAV.

