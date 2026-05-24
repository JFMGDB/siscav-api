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

## Opção 2: PostgreSQL em Docker (sem docker-compose neste repo)

Não há `docker-compose.yml` versionado aqui. Para subir só o Postgres localmente:

```bash
docker run --name siscav-postgres \
  -e POSTGRES_USER=siscav_user \
  -e POSTGRES_PASSWORD=siscav_password \
  -e POSTGRES_DB=siscav_db \
  -p 5432:5432 \
  -d postgres:15
```

Configure `DATABASE_URL` ou `POSTGRES_*` conforme [`installation.md`](installation.md), depois na raiz do repositório: `alembic upgrade head` e inicie o Uvicorn como na Opção 1.

---

## Comandos Úteis

### Parar o Servidor
- **Local:** Pressione `Ctrl+C` no terminal
- **Container Postgres:** `docker stop siscav-postgres` (se usou o exemplo acima)

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

## Opção 3: Script PowerShell (Windows)

Na **raiz do repositório**:

```powershell
.\scripts\start_server.ps1
```

O script define `PYTHONPATH` na raiz do repo, tenta ativar `venv\` e executa `uvicorn apps.api.src.main:app`.

---

## Troubleshooting

### Erro: "Could not import module 'main'"
**Causa:** O uvicorn não encontra o módulo porque está sendo executado no diretório errado ou o PYTHONPATH não está configurado.

**Soluções:**

1. **Usar o script PowerShell (mais fácil):**
   ```powershell
   .\scripts\start_server.ps1
   ```

2. **Configurar PYTHONPATH manualmente:**
   ```powershell
   $env:PYTHONPATH = $PWD
   uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Ou navegar para o diretório correto:**
   ```powershell
   cd apps/api/src
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

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
   - Coleção Postman em `docs/SISCAV_API.postman_collection.json` (e ambiente em `docs/SISCAV_API.postman_environment.json`)
   - Ou acesse a documentação interativa: http://localhost:8000/docs

2. **Criar um usuário:**
   - Use um script Python ou crie manualmente no banco de dados
   - Veja exemplos nos testes em `tests/`

3. **Executar testes:**
   ```bash
   pytest tests/ -v
   ```

