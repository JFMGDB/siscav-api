# Como Iniciar o Servidor SISCAV API

Guia rápido para iniciar o servidor da API localmente.

## Opção 1: Execução Local (Recomendado para Desenvolvimento)

### Passo 1: Ativar Ambiente Virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Passo 2: Instalar Dependências (se ainda não instalou)

```bash
pip install -r requirements-dev.txt
```

### Passo 3: Executar o Servidor

```bash
cd apps/api/src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Ou, a partir da raiz do projeto:**
```bash
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000
```

### Passo 4: Verificar se está rodando

Abra seu navegador e acesse:
- **API Status:** http://localhost:8000/
- **Health Check:** http://localhost:8000/api/v1/health
- **Documentação Swagger:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Opção 2: Usando Docker Compose

### Passo 1: Configurar Ambiente

Crie um arquivo `.env.local` na raiz do projeto:

```ini
POSTGRES_USER=siscav_user
POSTGRES_PASSWORD=siscav_password
POSTGRES_DB=siscav_db
SECRET_KEY=change_me_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### Passo 2: Iniciar com Docker Compose

```bash
docker compose --env-file .env.local --profile local up -d --build
```

### Passo 3: Executar Migrações

```bash
docker compose --env-file .env.local exec api alembic upgrade head
```

### Passo 4: Verificar Logs

```bash
docker compose --env-file .env.local logs -f api
```

---

## Comandos Úteis

### Parar o Servidor
- **Local:** Pressione `Ctrl+C` no terminal
- **Docker:** `docker compose --env-file .env.local down`

### Verificar se o servidor está rodando
```bash
curl http://localhost:8000/
```

Ou acesse no navegador: http://localhost:8000/

### Verificar Health Check
```bash
curl http://localhost:8000/api/v1/health
```

---

## Troubleshooting

### Erro: "ModuleNotFoundError"
**Solução:** Instale as dependências:
```bash
pip install -r requirements-dev.txt
```

### Erro: "Port 8000 already in use"
**Solução:** Use outra porta:
```bash
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8001
```

### Erro: "Could not connect to database"
**Solução:** 
- Verifique se o banco de dados está rodando (se usar Docker)
- Verifique as variáveis de ambiente no arquivo `.env`
- Para desenvolvimento local, o sistema usa SQLite automaticamente se não houver configuração de PostgreSQL

### Erro: "Permission denied" ao ativar venv (Linux/Mac)
**Solução:**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

---

## Variáveis de Ambiente (Opcional)

Para desenvolvimento local simples, você não precisa configurar variáveis de ambiente. O sistema usa valores padrão:
- Banco de dados: SQLite local (`siscav_dev.db`)
- Secret Key: `change_me_in_development`
- Porta: 8000

Para usar PostgreSQL ou outras configurações, crie um arquivo `.env` na raiz:

```ini
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/siscav_db
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=10
```

---

## Próximos Passos

Após iniciar o servidor:

1. **Testar a API:**
   - Use a coleção Postman (`SISCAV_API.postman_collection.json`)
   - Ou acesse a documentação interativa: http://localhost:8000/docs

2. **Criar um usuário:**
   - Use um script Python ou crie manualmente no banco de dados
   - Veja exemplos nos testes em `tests/`

3. **Executar testes:**
   ```bash
   pytest tests/ -v
   ```

