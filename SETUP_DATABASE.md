# Guia de Setup do Banco de Dados - Supabase

Este guia explica como criar as tabelas e executar as migrações no Supabase.

## Opção 1: Setup Manual via Supabase Studio (Recomendado)

### Passo 1: Acessar o SQL Editor

1. Acesse o [Supabase Dashboard](https://app.supabase.com)
2. Selecione seu projeto
3. No menu lateral, clique em **SQL Editor**
4. Clique em **New Query**

### Passo 2: Executar Script Completo

1. Abra o arquivo `db/sql/supabase/00_complete_setup.sql`
2. Copie todo o conteúdo
3. Cole no SQL Editor do Supabase
4. Clique em **Run** (ou pressione Ctrl+Enter)

Este script cria:
- Extensões necessárias (pgcrypto, pg_trgm)
- Tipo ENUM `access_status`
- Tabelas: `users`, `authorized_plates`, `access_logs`
- Índices para performance

### Passo 3: Verificar Criação

Execute estas queries no SQL Editor para verificar:

```sql
-- Verificar tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'authorized_plates', 'access_logs');

-- Verificar tipo ENUM
SELECT typname FROM pg_type WHERE typname = 'access_status';

-- Verificar extensões
SELECT extname FROM pg_extension WHERE extname IN ('pgcrypto', 'pg_trgm');
```

### Passo 4: Sincronizar Alembic

Após criar as tabelas manualmente, sincronize o Alembic para que ele reconheça o estado atual:

```powershell
# Carregar variáveis de ambiente
Get-Content .env.supabase | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Configurar PYTHONPATH
$env:PYTHONPATH = $PWD

# Sincronizar Alembic (marca como se a migração já tivesse sido executada)
alembic stamp head
```

## Opção 2: Executar Migrações via Alembic

Se você tem conectividade com o Supabase, pode executar as migrações diretamente:

### Passo 1: Verificar Configuração

Certifique-se de que o arquivo `.env.supabase` está configurado corretamente:

```env
DATABASE_URL=postgresql+psycopg2://postgres:[SUA_SENHA]@db.[ID_PROJETO].supabase.co:5432/postgres?sslmode=require
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Importante**: 
- Substitua `[SUA_SENHA]` pela senha do banco de dados do Supabase
- Substitua `[ID_PROJETO]` pelo ID do seu projeto Supabase
- Se a senha contiver caracteres especiais, faça URL-encode (ex: `?` → `%3F`)

### Passo 2: Executar Script de Migração

```powershell
# Executar script PowerShell
.\run_migrations.ps1
```

Ou manualmente:

```powershell
# Carregar variáveis de ambiente
Get-Content .env.supabase | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Configurar PYTHONPATH
$env:PYTHONPATH = $PWD

# Verificar estado atual
alembic current

# Executar migrações
alembic upgrade head
```

## Opção 3: Executar Scripts Individuais

Se preferir executar os scripts em ordem separada:

### No Supabase SQL Editor, execute na ordem:

1. **01_enable_extensions.sql** - Habilita extensões
2. **02_types.sql** - Cria tipo ENUM
3. **03_tables.sql** - Cria tabelas
4. **04_indexes.sql** - Cria índices

Depois sincronize o Alembic:

```powershell
alembic stamp head
```

## Verificação Final

Após executar qualquer uma das opções acima, verifique se tudo está funcionando:

```powershell
# Testar conexão e listar tabelas
$env:PYTHONPATH = $PWD
Get-Content .env.supabase | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
.\venv\Scripts\Activate.ps1

python -c "
import sys
sys.path.insert(0, '.')
from app.api.v1.db.session import SessionLocal
from sqlalchemy import inspect

db = SessionLocal()
inspector = inspect(db.bind)
tables = inspector.get_table_names()
print('Tabelas criadas:', tables)
db.close()
"
```

## Troubleshooting

### Erro: "could not translate host name"

- Verifique se o hostname no `.env.supabase` está correto
- Verifique sua conexão com a internet
- Tente executar via Supabase Studio (Opção 1)

### Erro: "relation already exists"

- As tabelas já existem. Use `alembic stamp head` para sincronizar

### Erro: "extension already exists"

- Normal, significa que a extensão já estava instalada. Continue com os próximos passos.

### Erro: "type access_status already exists"

- O tipo ENUM já existe. Continue com a criação das tabelas.

## Próximos Passos

Após criar as tabelas:

1. **Criar usuário administrador**: Execute `python app/seed_demo.py` ou crie manualmente
2. **Testar API**: Execute `uvicorn app.main:app --reload`
3. **Verificar endpoints**: Acesse http://localhost:8000/docs

