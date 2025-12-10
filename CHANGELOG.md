# Changelog

Todas as alterações notáveis neste repositório serão documentadas aqui.

Este arquivo segue o formato inspirado no Keep a Changelog e SemVer quando aplicável.

Padrão de seções para cada versão (use apenas as necessárias):
- Added (Adicionado): novos recursos
- Changed (Alterado): mudanças em funcionalidades existentes
- Fixed (Corrigido): correções de bugs
- Deprecated (Depreciado): APIs/designs que serão removidos futuramente
- Removed (Removido): itens removidos nesta versão
- Security (Segurança): notas de segurança

Datas e horas no formato ISO (YYYY-MM-DD HH:MM).

## [Unreleased]
### Added
- **DeviceController**: Criado controller para gerenciamento de dispositivos IoT seguindo o padrão MVC estabelecido
- **Schemas para Dispositivos**: Criados schemas Pydantic em `schemas/device.py` para padronização de dados de dispositivos:
  - `BluetoothDevice`: Representa um dispositivo Bluetooth detectado
  - `ConnectionRequest`: Request para conectar a um dispositivo
  - `ConnectionResponse`: Resposta da tentativa de conexão
  - `ConnectionStatus`: Status da conexão Bluetooth
  - `DisconnectResponse`: Resposta da desconexão de dispositivo
- **Dependency Injection para DeviceController**: Adicionada função `get_device_controller()` em `deps.py` para injeção de dependência do `DeviceController`
- **Dependency Injection para Controllers**: Implementado sistema de dependency injection para todos os controllers, eliminando redundância na criação de instâncias nos endpoints. Funções de dependência criadas em `deps.py`:
  - `get_plate_controller()`: Injeta `PlateController` com sessão de banco de dados
  - `get_access_log_controller()`: Injeta `AccessLogController` com sessão de banco de dados
  - `get_auth_controller()`: Injeta `AuthController` com sessão de banco de dados
  - `get_gate_controller()`: Injeta `GateController` (sem dependência de banco)
  - `get_device_controller()`: Injeta `DeviceController` (sem dependência de banco)
- **Logging Estruturado**: Adicionado logging adequado em todos os controllers para rastreamento de operações importantes:
  - `PlateController`: Logs de criação, atualização e validação de placas
  - `AccessLogController`: Logs de processamento de logs de acesso e salvamento de imagens
  - `AuthController`: Logs de tentativas de autenticação (sucesso e falha)
- **Validação de Parâmetros de Query**: Adicionada validação de parâmetros de query nos endpoints usando `Query` do FastAPI com validações de range (`ge`, `le`) para `skip` e `limit`, garantindo valores válidos.

### Fixed
- **Inconsistência Arquitetural em devices.py**: Refatorado endpoint `devices.py` para seguir o padrão MVC estabelecido:
  - Schemas movidos de `endpoints/devices.py` para `schemas/device.py` (separação de responsabilidades)
  - Criado `DeviceController` para centralizar lógica de negócio
  - Endpoints agora usam dependency injection via `Depends(get_device_controller)`
  - Adicionada autenticação obrigatória em todos os endpoints de dispositivos
  - Adicionada docstring no módulo e melhorada documentação dos endpoints
  - Adicionadas tags consistentes no router (`tags=["devices"]`)
- **Tags Duplicadas em gate_control.py**: Removida tag duplicada do router, mantendo apenas a tag definida em `api.py`
- **Linhas em Branco Desnecessárias**: Removidas linhas em branco desnecessárias no final de `core/limiter.py`
- **Documentação de Módulos**: Adicionada docstring no módulo `endpoints/health.py` para manter consistência com outros endpoints
- **Segurança - Path Traversal**: Melhorada validação de path traversal no método `get_image_path` do `AccessLogController`:
  - Adicionada sanitização do nome do arquivo usando `Path().name` para remover componentes de diretório
  - Validação adicional para prevenir nomes de arquivo vazios ou com ".." e "."
  - Mantida validação de path relativo para garantir que o arquivo está dentro do diretório permitido
- **Limpeza de Código**: Removidas linhas em branco desnecessárias em `access_log_controller.py`
- **Redundância na Criação de Controllers**: Eliminada criação repetida de instâncias de controllers em cada endpoint. Agora todos os endpoints usam dependency injection via `Depends()`, seguindo o padrão DRY e melhorando performance.
- **Superengenharia no GateController**: Removida dependência desnecessária de `db: Session` do `GateController`, pois este controller não realiza operações de banco de dados, apenas orquestra comunicação com dispositivos IoT. Isso simplifica o código e remove dependências não utilizadas.
- **Documentação de Repositories**: Adicionados comentários explicativos nos controllers sobre o uso de repositories como classes com métodos estáticos, melhorando a clareza do código.
- **Consistência de Endpoints**: Removida dependência não utilizada de `get_db` no endpoint `gate_control.py`, mantendo apenas as dependências necessárias.
- **Tratamento de Erros em Controllers**: Melhorado tratamento de erros em `PlateController.create()` com logging adequado e mensagens de erro mais informativas.
- **Limpeza de Arquivos em Caso de Erro**: Melhorado tratamento de erros em `AccessLogController.create_access_log()` com logging detalhado e limpeza adequada de arquivos salvos em caso de falha na criação do log.
- **Linhas em Branco Desnecessárias**: Removidas linhas em branco desnecessárias no final de `utils/plate.py`.
- **Imports Não Utilizados**: Removidos imports não utilizados:
  - `UUID` de `access_log_controller.py` (não era usado no código)
  - `Annotated` de `devices.py` (não era usado no código)
- **Linhas em Branco Desnecessárias**: Removidas linhas em branco desnecessárias no final de `core/limiter.py`.
- **Configuração de Constantes**: Movidas constantes hardcoded para configuração centralizada:
  - `MAX_FILE_SIZE` e `FILE_CHUNK_SIZE` agora são configuráveis via variáveis de ambiente (`MAX_FILE_SIZE_MB`, `FILE_CHUNK_SIZE`)
  - Melhora flexibilidade e facilita ajustes sem alterar código

### Changed
- **Refatoração Completa de devices.py para Padrão MVC**: Endpoint `devices.py` refatorado para seguir o padrão arquitetural estabelecido:
  - Lógica de negócio movida para `DeviceController`
  - Schemas movidos para `schemas/device.py` e exportados via `schemas/__init__.py`
  - Endpoints agora delegam lógica para o controller via dependency injection
  - Respostas tipadas usando schemas Pydantic (`ConnectionStatus`, `DisconnectResponse`)
  - Melhorada documentação e consistência com outros endpoints
- **Atualização de Exports**: Atualizado `controllers/__init__.py` e `schemas/__init__.py` para incluir `DeviceController` e schemas de dispositivos
- **Refatoração de Endpoints para Dependency Injection**: Todos os endpoints foram refatorados para usar dependency injection de controllers ao invés de criar instâncias manualmente:
  - `whitelist.py`: Usa `get_plate_controller()` via `Depends()`
  - `access_logs.py`: Usa `get_access_log_controller()` via `Depends()`
  - `auth.py`: Usa `get_auth_controller()` via `Depends()`
  - `gate_control.py`: Usa `get_gate_controller()` via `Depends()`
  - `devices.py`: Usa `get_device_controller()` via `Depends()`
- **Documentação de Endpoints**: Melhorada documentação dos endpoints com descrições mais claras dos parâmetros e uso de dependency injection.
- **Estrutura de `deps.py`**: Reorganizado `deps.py` com documentação completa de todas as funções de dependency injection, seguindo padrões de documentação Python.
- **Segurança e Validação de Arquivos**: Melhorado o método `validate_image_file` em `AccessLogController` para ler arquivos em chunks ao invés de carregar o arquivo inteiro na memória, prevenindo problemas de memória com arquivos grandes.
- **Tratamento de Erros em Transações**: Adicionado tratamento de rollback em todos os métodos de repositories que fazem commit (`create`, `update`, `delete`), garantindo que erros de banco de dados não deixem transações abertas.
- **Tratamento de Erros em Salvamento de Imagens**: Adicionado tratamento de exceções no método `save_image` e `create_access_log` do `AccessLogController`, incluindo limpeza de arquivos salvos em caso de erro ao criar o log.
- **Consistência de Status Codes**: Corrigido uso inconsistente de status codes HTTP:
  - `deps.py`: Alterado status code 404 para `status.HTTP_404_NOT_FOUND` para consistência.
  - `devices.py`: Alterado status code 400 para `status.HTTP_400_BAD_REQUEST` para consistência.
- **Documentação de Métodos**: Melhorada documentação do método `create_access_log` para explicar que a placa original do OCR é preservada no log, mesmo que não esteja em formato válido.
- **Limpeza de Código**: Removidas linhas em branco desnecessárias no final dos arquivos `gate_control.py` e `plate.py`.

### Changed
- **Validação de Tamanho de Arquivo**: Método `validate_image_file` agora lê arquivos em chunks de 8KB ao invés de carregar o arquivo inteiro, melhorando o uso de memória e permitindo validação de arquivos grandes sem esgotar a memória.
- **Tratamento de Erros em Repositories**: Todos os métodos de repositories que fazem commit agora incluem blocos try/except com rollback em caso de erro, garantindo integridade transacional.

### Removed
- **Import Não Utilizado**: Removido import não utilizado de `AuthorizedPlateCreate` do `AuthorizedPlateRepository`, pois este schema não é usado diretamente no repository (apenas no controller).

### Added
- Arquitetura MVC com separação de responsabilidades (SOLID, DRY):
- Documentação arquitetural completa em `docs/arquitetura/03-padrao-mvc-reorganizacao.md`:
  - Explicação detalhada das decisões arquiteturais
  - Justificativas para cada camada (Repositories, Controllers, Endpoints)
  - Princípios SOLID e DRY aplicados
  - Guia de migração do código antigo
  - Fluxo de dados e exemplos práticos
  - `apps/api/src/api/v1/repositories/`: Camada de acesso a dados (Data Access Layer) com classes Repository para operações de banco de dados puras.
    - `UserRepository`: Operações de banco de dados para usuários.
    - `AuthorizedPlateRepository`: Operações de banco de dados para placas autorizadas.
    - `AccessLogRepository`: Operações de banco de dados para logs de acesso.
  - `apps/api/src/api/v1/controllers/`: Camada de lógica de negócio (Service Layer) com classes Controller seguindo Single Responsibility Principle.
    - `AuthController`: Lógica de negócio de autenticação (validação de credenciais, criação de tokens).
    - `PlateController`: Lógica de negócio de placas autorizadas (validação de formato, normalização, verificação de duplicatas).
    - `AccessLogController`: Lógica de negócio de logs de acesso (validação de arquivos, processamento de imagens, verificação de autorização).
    - `GateController`: Lógica de negócio de controle de portão (preparado para integração futura com IoT).

### Changed
- Reorganização arquitetural completa seguindo padrões MVC, SOLID e DRY:
  - **Repositories (Data Access Layer)**: Funções CRUD antigas (`crud/`) foram refatoradas para classes Repository com métodos estáticos, focando exclusivamente em operações de banco de dados.
  - **Controllers (Service Layer)**: Nova camada que contém toda a lógica de negócio, orquestrando operações entre repositories e aplicando regras de negócio (validações, transformações, etc.).
  - **Endpoints (Views)**: Endpoints foram simplificados para serem apenas camadas de roteamento HTTP, delegando toda a lógica de negócio para os controllers.
  - **Separação de Responsabilidades**: Cada camada tem uma responsabilidade única e bem definida:
    - Repositories: Apenas acesso a dados (SQLAlchemy queries).
    - Controllers: Lógica de negócio e orquestração.
    - Endpoints: Roteamento HTTP e validação de entrada/saída.
- Atualização de dependências:
  - `apps/api/src/api/v1/endpoints/auth.py`: Agora usa `AuthController` em vez de funções CRUD diretas.
  - `apps/api/src/api/v1/endpoints/whitelist.py`: Agora usa `PlateController` para toda a lógica de negócio.
  - `apps/api/src/api/v1/endpoints/access_logs.py`: Refatorado para usar `AccessLogController`, centralizando validação de arquivos e processamento de imagens.
  - `apps/api/src/api/v1/endpoints/gate_control.py`: Agora usa `GateController` para isolamento da lógica de controle de portão.
  - `apps/api/src/api/v1/deps.py`: Atualizado para usar `UserRepository` em vez de `crud_user`.
- Testes atualizados:
  - `tests/test_auth_whitelist.py`: Atualizado para usar `UserRepository` e criar usuários diretamente via modelo.
  - `tests/test_access_logs.py`: Atualizado para usar `AuthorizedPlateRepository` em vez de funções CRUD.

### Fixed
- Eliminação de duplicação de código (DRY):
  - Validação de arquivos de imagem centralizada em `AccessLogController.validate_image_file()`.
  - Lógica de salvamento de imagens centralizada em `AccessLogController.save_image()`.
  - Validação e normalização de placas centralizada em `PlateController` com reutilização de utilitários.
- Melhoria na manutenibilidade:
  - Lógica de negócio isolada em controllers, facilitando testes unitários e manutenção.
  - Separação clara entre acesso a dados e lógica de negócio, permitindo mudanças independentes.

### Deprecated
- Módulos CRUD antigos (`apps/api/src/api/v1/crud/`): 
  - `crud_user.py`, `crud_authorized_plate.py`, `crud_access_log.py` estão obsoletos.
  - Use os novos repositories em `apps/api/src/api/v1/repositories/` para acesso a dados.
  - Use os controllers em `apps/api/src/api/v1/controllers/` para lógica de negócio.
  - **Nota**: Os módulos CRUD antigos serão removidos em uma versão futura após migração completa.
  - Avisos de depreciação (`DeprecationWarning`) adicionados aos módulos CRUD antigos para alertar desenvolvedores durante a execução.

### Removed
- 

### Documentation
- README.md atualizado com seção de Arquitetura explicando o padrão MVC implementado.
- README.md atualizado na estrutura de diretórios para refletir repositories e controllers.
- Documentação técnica completa da reorganização arquitetural criada em `docs/arquitetura/03-padrao-mvc-reorganizacao.md`.
- Resumo executivo da arquitetura criado em `docs/arquitetura/00-resumo-executivo.md` com visão geral, decisões principais e benefícios.
- `docs/README.md` atualizado para incluir referência à nova documentação de arquitetura MVC e resumo executivo.
- `docs/arquitetura/README.md` atualizado com informações sobre o padrão MVC implementado e índice completo.
- `docs/arquitetura/02-arquitetura-backlog.md` atualizado com nota sobre a reorganização arquitetural.
- Arquivos `__init__.py` melhorados com documentação e exports apropriados:
  - `models/__init__.py`: Exports de todos os modelos SQLAlchemy
  - `schemas/__init__.py`: Exports de todos os schemas Pydantic
  - `endpoints/__init__.py`: Exports de todos os roteadores
  - `db/__init__.py`: Exports de configuração do banco de dados
  - `core/__init__.py`: Exports de configurações e utilitários centrais
  - `utils/__init__.py`: Exports de utilitários compartilhados
  - `api/v1/__init__.py`: Documentação do módulo principal da API v1
- `api/v1/api.py`: Documentação melhorada do agregador de roteadores.

### Fixed
- Inconsistência corrigida em `pyproject.toml`: `passlib[bcrypt]` atualizado para `passlib[argon2]` para corresponder ao `requirements.txt` e ao código implementado.
- `.gitignore` atualizado para incluir arquivos específicos do projeto:
  - Bancos de dados SQLite de desenvolvimento (`*.db`, `*.sqlite`, `siscav_dev.db`)
  - Arquivos de teste e logs (`test_output.txt`, `*.log`, `logs/`)
  - Diretório de uploads de desenvolvimento (`uploads/`)

### Security
- 

## [0.1.1] - 2025-11-03 20:19
### Added
- 

### Changed
- CI: Consolidado o workflow em `.github/workflows/ci.yml` (removida duplicação e unificados triggers/steps).
- README: Corrigida estrutura do projeto (removidas referências a arquivos inexistentes em `.github/` e pasta `apps/iot-device` marcada como planejada) e seção de CI alinhada ao workflow atual.
- docker-compose: adicionada dependência condicional `depends_on` com `service_healthy` para `api` → `db` no perfil local.
- env.local.example: removido `DATABASE_URL` redundante; agora a app resolve via `POSTGRES_*` por padrão.
- README: adicionada seção de troubleshooting para correção de erros de lint (`ruff check --fix`) e formatação (`ruff format`).

### Fixed
- CI: Removidas definições duplicadas no arquivo `.github/workflows/ci.yml`.
- Lint (Ruff): padronizada ordenação/agrupamento de imports (I001) e uso de imports absolutos (TID252) nos módulos da API e modelos; ajuste em `alembic/env.py` para evitar F401 mantendo import de modelos por efeito colateral.
- Lint (Ruff): executado `ruff check --select I --fix` para corrigir automaticamente a ordem dos imports nos arquivos `alembic/env.py` e na migração inicial.
- Format (Ruff): executado `ruff format .` para aplicar o padrão de formatação de código em todo o projeto.

### Deprecated
- 

### Removed
- docker-compose: entradas `dns` e `extra_hosts` não essenciais no ambiente de desenvolvimento.

### Security
- 

## [0.1.0] - 2025-11-03
### Added (Adicionado)
- Estrutura completa da API v1 (FND-03):
  - `apps/api/src/api/v1/core/config.py`: Settings centralizadas (env vars) usando Pydantic.
  - `apps/api/src/api/v1/db/base.py` e `apps/api/src/api/v1/db/session.py`: Base declarativa e Session/engine do SQLAlchemy.
  - `apps/api/src/api/v1/endpoints/health.py`: Endpoint de health com `APIRouter` (`GET /api/v1/health`).
  - `apps/api/src/api/v1/api.py`: Agregador de roteadores da versão v1.
  - `apps/api/src/api/v1/schemas/`: Schemas Pydantic iniciais (`user.py`, `authorized_plate.py`, `access_log.py`, `token.py`).
  - `apps/api/src/api/v1/models/`: Modelos SQLAlchemy iniciais (`user.py`, `authorized_plate.py`, `access_log.py`).
  - `apps/api/src/api/v1/crud/`: Skeletons de CRUD (`crud_user.py`, `crud_authorized_plate.py`, `crud_access_log.py`).
- `apps/api/src/main.py`: Inclusão do `api_router` da v1 com prefixo `/api/v1`, mantendo o endpoint raiz `/`.
- `pyrightconfig.json`: configuração para apontar o BasedPyright para o venv (`venv`) e adicionar `apps` ao sys.path do analisador.
- CI Backend (FND-08): `.github/workflows/ci.yml` com Python 3.13, cache de pip, lint/format com Ruff e testes com Pytest.
- Dependência: `email-validator` adicionada (necessária para `pydantic.EmailStr`).
- Documentação de migração manual Supabase: `docs/DB_MIGRATION_SUPABASE.md` + scripts SQL em `db/sql/supabase/` (`01_enable_extensions.sql`, `02_types.sql`, `03_tables.sql`, `04_indexes.sql`).

### Changed (Alterado)
- `core/config.py`: Montagem de `DATABASE_URL` a partir de `POSTGRES_*` quando `DATABASE_URL` não estiver definido (compatível com `.env.local` e `.env.supabase`), com fallback seguro para SQLite em dev bare.
- Documentação: README atualizado com a seção "Como o DATABASE_URL é resolvido" e docstrings no `core/config.py` detalhando as prioridades.
- Documentação: README atualizado com instruções explícitas de uso do Docker para alternar entre `.env.local` (com `--profile local` para subir o `db`) e `.env.supabase`