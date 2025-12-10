# Script para executar migrações do Alembic no Supabase
# Uso: .\run_migrations.ps1

Write-Host "=== Executando Migrações do Alembic ===" -ForegroundColor Cyan

# Configurar PYTHONPATH
$env:PYTHONPATH = $PSScriptRoot

# Carregar variáveis de ambiente do .env.supabase
if (Test-Path ".env.supabase") {
    Write-Host "Carregando variáveis de ambiente de .env.supabase..." -ForegroundColor Yellow
    Get-Content .env.supabase | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value, 'Process')
            Write-Host "  Carregado: $key" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "AVISO: Arquivo .env.supabase não encontrado!" -ForegroundColor Red
    Write-Host "Certifique-se de que o arquivo existe e está configurado corretamente." -ForegroundColor Yellow
    exit 1
}

# Ativar ambiente virtual
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "`nAtivando ambiente virtual..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "ERRO: Ambiente virtual não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar conexão
Write-Host "`nVerificando conexão com o banco de dados..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, '.'); from app.api.v1.core.config import get_settings; url = get_settings().database_url; print('DATABASE_URL:', url[:60] + '...' if len(url) > 60 else url)"

# Verificar estado atual das migrações
Write-Host "`nVerificando estado atual das migrações..." -ForegroundColor Yellow
alembic current

# Executar migrações
Write-Host "`nExecutando migrações..." -ForegroundColor Yellow
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Migrações executadas com sucesso! ===" -ForegroundColor Green
    Write-Host "`nVerificando estado final..." -ForegroundColor Yellow
    alembic current
} else {
    Write-Host "`n=== ERRO ao executar migrações ===" -ForegroundColor Red
    Write-Host "Verifique a conexão com o Supabase e tente novamente." -ForegroundColor Yellow
    exit 1
}

