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
- `tests/conftest.py`: Configuração centralizada de testes com fixtures compartilhadas (banco de dados, cliente FastAPI, limpeza automática da pasta `uploads` via fixture `cleanup_uploads`)
- Testes adicionais: `test_access_logs.py` e `test_auth_whitelist.py` para cobertura completa dos endpoints
- Testes de casos negativos: cobertura de erros de autenticação (credenciais inválidas, token ausente/inválido/malformado) e operações em recursos deletados

### Changed
- README.md: Seção de testes expandida com detalhes sobre estrutura, arquitetura e comandos de execução
- README.md: Estrutura do projeto atualizada para incluir todos os arquivos de teste (`conftest.py`, `test_access_logs.py`, `test_auth_whitelist.py`)
- Testes: Refatorados para usar fixtures compartilhadas do `conftest.py`, garantindo isolamento e consistência

### Fixed
- Lint (Ruff): Corrigidos erros PT003 (remoção de `scope='function'` implícito em fixtures pytest)
- Lint (Ruff): Corrigidos erros SIM105 (substituição de `try-except-pass` por `contextlib.suppress()`)
- Lint (Ruff): Corrigidos erros RET504 (remoção de atribuições desnecessárias antes de `return`)
- Lint (Ruff): Corrigidos erros B904 (adição de `from e` em exceções dentro de `except`)
- Lint (Ruff): Corrigidos erros PLC0415 (movimentação de imports para o topo dos arquivos)
- Lint (Ruff): Corrigidos erros ARG001 (adição de `# noqa: ARG001` para argumentos não usados necessários para dependency injection)
- Lint (Ruff): Corrigidos erros PTH103, PTH110, PTH123, PTH118 (substituição de `os` por `pathlib.Path`)
- Lint (Ruff): Corrigidos erros PLR2004 (substituição de números mágicos por constantes nomeadas)
- Lint (Ruff): Corrigidos erros T201 (remoção de `print` statements)
- Testes: Isolamento adequado entre testes usando banco de dados SQLite em memória com reset automático
- Testes: Limpeza automática de arquivos criados na pasta `uploads` durante os testes

### Deprecated
- 

### Removed
- 

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