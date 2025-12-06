# Script de Instalação de Dependências - Dispositivo IoT SISCAV
# Resolve problemas de instalação no Windows, especialmente com Python 3.14

param(
    [string]$PythonVersion = "",
    [switch]$ForceWheel = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instalação de Dependências - SISCAV IoT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar versão do Python
Write-Host "Verificando versão do Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Versão encontrada: $pythonVersion" -ForegroundColor Green

# Extrair número da versão
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $majorVersion = [int]$matches[1]
    $minorVersion = [int]$matches[2]
    
    if ($majorVersion -eq 3 -and $minorVersion -ge 13) {
        Write-Host ""
        Write-Host "AVISO: Python 3.$minorVersion detectado!" -ForegroundColor Red
        Write-Host "Python 3.13+ pode causar problemas de compilação." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Opções:" -ForegroundColor Yellow
        Write-Host "1. Usar Python 3.12 (recomendado)" -ForegroundColor White
        Write-Host "2. Tentar instalar com wheels pré-compilados (pode falhar)" -ForegroundColor White
        Write-Host ""
        
        if (-not $ForceWheel) {
            $choice = Read-Host "Escolha uma opção (1 ou 2)"
            
            if ($choice -eq "1") {
                Write-Host ""
                Write-Host "Para usar Python 3.12:" -ForegroundColor Cyan
                Write-Host "1. Baixe Python 3.12 de: https://www.python.org/downloads/" -ForegroundColor White
                Write-Host "2. Execute: py -3.12 -m venv venv" -ForegroundColor White
                Write-Host "3. Execute: venv\Scripts\activate" -ForegroundColor White
                Write-Host "4. Execute este script novamente" -ForegroundColor White
                Write-Host ""
                exit 1
            }
        }
    }
}

# Atualizar pip
Write-Host ""
Write-Host "Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao atualizar pip!" -ForegroundColor Red
    exit 1
}

# Instalar NumPy com estratégia específica
Write-Host ""
Write-Host "Instalando NumPy..." -ForegroundColor Yellow

if ($ForceWheel -or $minorVersion -ge 13) {
    Write-Host "Tentando instalar NumPy usando wheel pré-compilado..." -ForegroundColor Yellow
    python -m pip install --only-binary :all: numpy
} else {
    Write-Host "Instalando NumPy (versão compatível)..." -ForegroundColor Yellow
    python -m pip install "numpy>=1.24.0,<2.0.0"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Falha ao instalar NumPy!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Soluções:" -ForegroundColor Yellow
    Write-Host "1. Use Python 3.12: py -3.12 -m venv venv" -ForegroundColor White
    Write-Host "2. Instale Visual Studio Build Tools (se precisar compilar)" -ForegroundColor White
    Write-Host "3. Use Conda: conda install numpy" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Verificar instalação do NumPy
Write-Host ""
Write-Host "Verificando instalação do NumPy..." -ForegroundColor Yellow
python -c "import numpy; print(f'NumPy {numpy.__version__} instalado com sucesso!')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao verificar NumPy!" -ForegroundColor Red
    exit 1
}

# Instalar OpenCV
Write-Host ""
Write-Host "Instalando OpenCV..." -ForegroundColor Yellow
python -m pip install "opencv-python>=4.8.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar OpenCV!" -ForegroundColor Red
    exit 1
}

# Instalar Requests
Write-Host ""
Write-Host "Instalando Requests..." -ForegroundColor Yellow
python -m pip install "requests>=2.31.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar Requests!" -ForegroundColor Red
    exit 1
}

# Instalar EasyOCR
Write-Host ""
Write-Host "Instalando EasyOCR (pode demorar alguns minutos)..." -ForegroundColor Yellow
python -m pip install "easyocr>=1.7.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar EasyOCR!" -ForegroundColor Red
    exit 1
}

# Verificação final
Write-Host ""
Write-Host "Verificando todas as dependências..." -ForegroundColor Yellow
Write-Host ""

$allOk = $true

try {
    python -c "import numpy; print('✓ NumPy:', numpy.__version__)" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host "✓ NumPy: OK" -ForegroundColor Green } else { $allOk = $false; Write-Host "✗ NumPy: FALHOU" -ForegroundColor Red }
} catch {
    $allOk = $false
    Write-Host "✗ NumPy: FALHOU" -ForegroundColor Red
}

try {
    python -c "import cv2; print('✓ OpenCV:', cv2.__version__)" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host "✓ OpenCV: OK" -ForegroundColor Green } else { $allOk = $false; Write-Host "✗ OpenCV: FALHOU" -ForegroundColor Red }
} catch {
    $allOk = $false
    Write-Host "✗ OpenCV: FALHOU" -ForegroundColor Red
}

try {
    python -c "import easyocr; print('✓ EasyOCR: OK')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host "✓ EasyOCR: OK" -ForegroundColor Green } else { $allOk = $false; Write-Host "✗ EasyOCR: FALHOU" -ForegroundColor Red }
} catch {
    $allOk = $false
    Write-Host "✗ EasyOCR: FALHOU" -ForegroundColor Red
}

try {
    python -c "import requests; print('✓ Requests:', requests.__version__)" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host "✓ Requests: OK" -ForegroundColor Green } else { $allOk = $false; Write-Host "✗ Requests: FALHOU" -ForegroundColor Red }
} catch {
    $allOk = $false
    Write-Host "✗ Requests: FALHOU" -ForegroundColor Red
}

Write-Host ""

if ($allOk) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Instalação concluída com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Cyan
    Write-Host "1. Configure as variáveis de ambiente" -ForegroundColor White
    Write-Host "2. Execute: python main.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Algumas dependências falharam!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Consulte docs/TROUBLESHOOTING_INSTALACAO.md para ajuda." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}













