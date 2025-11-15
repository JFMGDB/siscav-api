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
- 

### Changed
- 

### Fixed
- 

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
- Documentação: README atualizado com instruções explícitas de uso do Docker para alternar entre `.env.local` (com `--profile local` para subir o `db`) e `.env.supabase` (somente `api`).
- Documentação: README atualizado com seção de Alembic e estrutura do diretório `alembic/` (arquivo `alembic.ini` na raiz).
- Alembic: `env.py` configurado com `compare_type=True` e `compare_server_default=True` para autogenerate mais preciso.
- Modelos: colunas `id` e FKs alteradas para `UUID(as_uuid=True)` (PostgreSQL) com tipagem `uuid.UUID` e `default=uuid.uuid4` no ORM.
- Migração inicial: IDs e FK ajustados para `postgresql.UUID(as_uuid=True)` com `server_default=gen_random_uuid()`; mantido ENUM `access_status` para `access_logs.status`.

### Notes (Notas)
- Critérios de aceitação do FND-03 atendidos: estrutura orientada a domínio criada e app inicia sem erros.
- Alembic e migração inicial (FND-05) foram implementados.
 - FND-08: Pipeline de CI básico configurado para PRs em `develop` e pushes em `main`/`develop`.

---


