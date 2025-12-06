# Development

Esta seção contém documentação para desenvolvedores, incluindo padrões de código, convenções e guias de desenvolvimento.

## Documentos Disponíveis

### [Padrões de Código e Arquitetura](./coding-standards.md)
Documentação completa sobre:
- Padrão MVC implementado
- Princípios SOLID e DRY
- Estrutura de camadas (Repositories, Controllers, Endpoints)
- Convenções de nomenclatura
- Guia de migração do código antigo

## Princípios de Desenvolvimento

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

## Estrutura de Camadas

```
Endpoints (Views)
    ↓
Controllers (Service Layer)
    ↓
Repositories (Data Access)
    ↓
Models (SQLAlchemy)
```

## Convenções

### Nomenclatura

- **Endpoints**: `snake_case` (ex: `auth.py`, `access_logs.py`)
- **Controllers**: `PascalCase` com sufixo `Controller` (ex: `AuthController`)
- **Repositories**: `PascalCase` com sufixo `Repository` (ex: `UserRepository`)
- **Models**: `PascalCase` (ex: `User`, `AuthorizedPlate`)

### Organização de Arquivos

- Cada domínio tem sua própria pasta em `api/v1/`
- Controllers ficam em `controllers/`
- Repositories ficam em `repositories/`
- Endpoints ficam em `endpoints/`

## Testes

Execute os testes com:

```bash
pytest
pytest -v --cov=apps --cov-report=term-missing
```

## Referências

- [Documentação da API](../api/README.md)
- [Documentação de Arquitetura](../architecture/README.md)
- [Documentação do Banco de Dados](../database/README.md)

