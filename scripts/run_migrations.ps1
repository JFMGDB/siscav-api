# Script to run Alembic migrations against Supabase
# Usage (from repo root): .\scripts\run_migrations.ps1

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "=== Running Alembic Migrations ===" -ForegroundColor Cyan

# Repo root on PYTHONPATH (imports apps.api.src...)
$env:PYTHONPATH = $RepoRoot
Write-Host "PYTHONPATH configured: $env:PYTHONPATH" -ForegroundColor Gray

# Load environment variables from .env.supabase
if (Test-Path ".env.supabase") {
    Write-Host "Loading environment variables from .env.supabase..." -ForegroundColor Yellow
    Get-Content .env.supabase | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value, 'Process')
            Write-Host "  Loaded: $key" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "WARNING: .env.supabase file not found!" -ForegroundColor Red
    Write-Host "Make sure the file exists and is configured correctly." -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Verify connection
Write-Host "`nVerifying database connection..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, '.'); from apps.api.src.api.v1.core.config import get_settings; url = get_settings().database_url; print('DATABASE_URL:', url[:60] + '...' if len(url) > 60 else url)"

# Check current migration state
Write-Host "`nChecking current migration state..." -ForegroundColor Yellow
alembic current

# Run migrations
Write-Host "`nRunning migrations..." -ForegroundColor Yellow
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Migrations completed successfully! ===" -ForegroundColor Green
    Write-Host "`nVerifying final state..." -ForegroundColor Yellow
    alembic current
} else {
    Write-Host "`n=== ERROR running migrations ===" -ForegroundColor Red
    Write-Host "Check your Supabase connection and try again." -ForegroundColor Yellow
    exit 1
}
