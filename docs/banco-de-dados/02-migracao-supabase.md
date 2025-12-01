# Migração manual para o Supabase (sem Docker)

Este guia documenta como criar o schema inicial e índices no Supabase quando a execução via Docker/alembic não é viável (ex.: DNS do container). Também inclui os scripts SQL versionados nesta codebase.

## Conteúdo
- Extensões necessárias (pgcrypto, pg_trgm)
- Tipo ENUM `access_status`
- Tabelas: `users`, `authorized_plates`, `access_logs`
- Índices recomendados (inclui opcionais para busca)

Os arquivos SQL estão em `db/sql/supabase/`:
- `01_enable_extensions.sql`
- `02_types.sql`
- `03_tables.sql`
- `04_indexes.sql`

## Passo a passo (Supabase Studio)
1. Abra o Supabase Studio → SQL Editor.
2. Execute os arquivos SQL na ordem:
   - `01_enable_extensions.sql`
   - `02_types.sql`
   - `03_tables.sql`
   - `04_indexes.sql`
3. Valide se as tabelas aparecem em `public`:
   - `users`, `authorized_plates`, `access_logs`
   - Tipo `access_status` criado

## Alternativa: psql local (host) com SSL
Se desejar aplicar por CLI:

```bash
psql "postgres://<user>:<senha_urlencodada>@<host>:5432/postgres?sslmode=require" \
  -f db/sql/supabase/01_enable_extensions.sql \
  -f db/sql/supabase/02_types.sql \
  -f db/sql/supabase/03_tables.sql \
  -f db/sql/supabase/04_indexes.sql
```

Observação: senhas com caracteres especiais (ex.: `?`) devem ser URL-encodadas (`?` → `%3F`).

## Integração com Alembic
Se a criação foi manual, marque a migração como aplicada para sincronizar o estado local do Alembic:

```powershell
$env:DATABASE_URL = 'postgresql+psycopg2://<user>:<senha_enc>@<host>:5432/postgres?sslmode=require'
alembic stamp head
```

Assim, futuras migrações poderão ser geradas e aplicadas normalmente.

## DDL de referência
Os scripts refletem o modelo do documento de dados e a configuração atual do projeto:
- PKs em UUID com `DEFAULT gen_random_uuid()`
- `TIMESTAMPTZ` com `DEFAULT NOW()`
- ENUM `access_status` com valores `'Authorized' | 'Denied'`
- `authorized_plate_id` em `access_logs` com `ON DELETE SET NULL`

## Índices opcionais para busca
Para aceleração de busca por trechos em `plate_string_detected`, usamos `pg_trgm` com GIN (já incluso no `04_indexes.sql`).

## Troubleshooting
- Erro `gen_random_uuid()` → rode `CREATE EXTENSION IF NOT EXISTS pgcrypto;`
- Falhas de DNS: ajuste DNS do sistema para `1.1.1.1/8.8.8.8` durante a aplicação via CLI; em ambientes restritos, use o SQL Editor do Supabase.
