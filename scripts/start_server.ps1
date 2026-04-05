# Script para iniciar o servidor SISCAV API
# Uso (na raiz do repositório): .\scripts\start_server.ps1

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "=== Iniciando Servidor SISCAV API ===" -ForegroundColor Cyan

# Raiz do repositório no PYTHONPATH (imports apps.api.src...)
$env:PYTHONPATH = $RepoRoot
Write-Host "PYTHONPATH configurado: $env:PYTHONPATH" -ForegroundColor Gray

# Verificar se o ambiente virtual existe
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "`nAtivando ambiente virtual..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "AVISO: Ambiente virtual não encontrado!" -ForegroundColor Yellow
    Write-Host "Certifique-se de que o venv está criado e ativado." -ForegroundColor Yellow
}

# Verificar se o uvicorn está instalado
Write-Host "`nVerificando dependências..." -ForegroundColor Yellow
try {
    python -c "import uvicorn; print('uvicorn OK')" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: uvicorn não está instalado!" -ForegroundColor Red
        Write-Host "Execute: pip install -r requirements-dev.txt" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERRO: Não foi possível verificar uvicorn!" -ForegroundColor Red
    exit 1
}

# Iniciar o servidor
Write-Host "`nIniciando servidor..." -ForegroundColor Green
Write-Host "Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentação: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPressione Ctrl+C para parar o servidor`n" -ForegroundColor Yellow

# Executar uvicorn com o caminho completo do módulo
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000


