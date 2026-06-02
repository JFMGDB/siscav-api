# Alternativas ao Supabase em `.env.local`

O fluxo padrão do time é **Supabase** via `env.local.example` → `.env.local` com `DATABASE_URL`.

Use **apenas uma** das opções abaixo (não misture `DATABASE_URL` com `POSTGRES_*` ao mesmo tempo).

## SQLite (dev isolado, sem rede)

```env
ENVIRONMENT=development
DATABASE_URL=sqlite:///./siscav_dev.db
SECRET_KEY=change_me_in_development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
DEVICE_INGEST_KEY=
```

Na raiz do repositório: `alembic upgrade head` antes de subir a API.

## PostgreSQL local (Docker Compose)

Defina `POSTGRES_*` e **omit** `DATABASE_URL` — a API monta a URL automaticamente:

```env
ENVIRONMENT=development
POSTGRES_USER=siscav_user
POSTGRES_PASSWORD=siscav_password
POSTGRES_DB=siscav_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=change_me_in_development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
DEVICE_INGEST_KEY=
```

## Supabase — notas

- **Session mode** (porta `5432` no pooler): recomendado para API + Alembic na mesma URL.
- **Transaction mode** (porta `6543`): ver [ADR 003](../architecture/adr/003-database-url-and-supabase-exposure.md).
- Evite `db.[ref].supabase.co` se a rede não tiver IPv6; prefira o host do pooler IPv4.

## Variáveis opcionais

Não estão no template mínimo; veja comentários históricos em commits antigos ou `apps/api/src/api/v1/core/config.py`:

| Variável | Uso |
|----------|-----|
| `GATE_ACTUATOR_URL` | URL do atuador do portão |
| `IOT_DEVICE_DEMO_API` | API demo Bluetooth |
| `VEHICLE_CLASSIFIER_BACKEND` | Classificador (`stub` padrão) |
| `UPLOAD_DIR` / `MAX_FILE_SIZE_MB` | Uploads |
