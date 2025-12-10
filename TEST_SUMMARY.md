# Resumo dos Testes - SISCAV API

## Cobertura de Testes

**Cobertura Total da API: 88%** (Requisito mínimo: 75% ✅)

## Comandos Úteis

### Ver resumo rápido dos testes
```bash
python -m pytest --cov=app.api.v1 --cov-report=term --tb=no -q
```

### Ver resumo detalhado com cobertura por arquivo
```bash
python -m pytest --cov=app.api.v1 --cov-report=term-missing -v
```

### Ver apenas testes que passaram
```bash
python -m pytest --cov=app.api.v1 -v --tb=no | Select-String "PASSED"
```

### Ver apenas testes que falharam
```bash
python -m pytest --cov=app.api.v1 -v --tb=short | Select-String "FAILED\|ERROR"
```

### Gerar relatório HTML de cobertura
```bash
python -m pytest --cov=app.api.v1 --cov-report=html
# Abrir: htmlcov/index.html no navegador
```

### Executar apenas testes unitários
```bash
python -m pytest tests/unit/ -v
```

### Executar apenas testes de integração
```bash
python -m pytest tests/integration/ -v
```

### Executar testes específicos
```bash
# Por arquivo
python -m pytest tests/unit/test_controllers_auth.py -v

# Por classe
python -m pytest tests/unit/test_controllers_auth.py::TestAuthController -v

# Por método
python -m pytest tests/unit/test_controllers_auth.py::TestAuthController::test_authenticate_success -v
```

## Estrutura de Testes

### Testes Unitários (`tests/unit/`)
- **Controllers**: `test_controllers_*.py`
  - AuthController
  - PlateController
  - AccessLogController
  - DeviceController
  - GateController

- **Repositories**: `test_repositories_*.py`
  - UserRepository
  - AuthorizedPlateRepository
  - AccessLogRepository

- **Core**: `test_core_*.py`
  - Config
  - Security
  - Utils

- **Utils**: `test_utils_*.py`
  - Plate utilities

### Testes de Integração (`tests/integration/`)
- **Endpoints**: `test_endpoints_*.py`
  - Auth
  - Whitelist
  - Access Logs
  - Devices
  - Gate Control

## Estatísticas Atuais

- **Total de Testes**: 162
- **Testes Passando**: 153
- **Testes Falhando**: 9
- **Erros**: 14 (principalmente testes de integração que precisam de ajustes)

## Cobertura por Módulo

### 100% de Cobertura
- Controllers: AuthController, AccessLogController, DeviceController, GateController
- Models: Todos os modelos SQLAlchemy
- Schemas: Maioria dos schemas Pydantic
- Utils: Plate utilities
- Core: Config, Utils

### Alta Cobertura (>80%)
- PlateController: 70% (alguns métodos de erro não testados)
- Repositories: 83-89%
- Endpoints: 60-89% (varia por endpoint)
- Deps: 87%

### Baixa Cobertura (<80%)
- Endpoints Auth: 62% (refresh token não totalmente testado)
- Endpoints Devices: 71% (alguns casos de erro)
- CRUD antigo: 46% (deprecated, não precisa de alta cobertura)

## Próximos Passos

1. Corrigir testes de integração que estão falhando
2. Adicionar testes para refresh token
3. Adicionar testes para casos de erro nos endpoints
4. Melhorar cobertura do PlateController (métodos de erro)

