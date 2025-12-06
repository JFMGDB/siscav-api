# Script para Configurar Ambiente Python 3.12 - SISCAV IoT Device

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuração Python 3.12 - SISCAV IoT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python 3.12 já está instalado
Write-Host "Verificando Python 3.12..." -ForegroundColor Yellow
$py312 = py -3.12 --version 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Python 3.12 encontrado: $py312" -ForegroundColor Green
    $python312Available = $true
} else {
    Write-Host "Python 3.12 não encontrado." -ForegroundColor Red
    Write-Host ""
    Write-Host "Opções para instalar Python 3.12:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPÇÃO 1: Download Manual (Recomendado)" -ForegroundColor Green
    Write-Host "  1. Baixe Python 3.12.0 de:" -ForegroundColor White
    Write-Host "     https://www.python.org/downloads/release/python-3120/" -ForegroundColor Cyan
    Write-Host "  2. Execute o instalador" -ForegroundColor White
    Write-Host "  3. Marque 'Add Python to PATH'" -ForegroundColor White
    Write-Host "  4. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    Write-Host "OPÇÃO 2: Usar Winget (se disponível)" -ForegroundColor Yellow
    Write-Host "  winget install Python.Python.3.12" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Deseja tentar instalar via winget agora? (S/N)"
    
    if ($choice -eq "S" -or $choice -eq "s") {
        Write-Host ""
        Write-Host "Tentando instalar Python 3.12 via winget..." -ForegroundColor Yellow
        winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python 3.12 instalado com sucesso!" -ForegroundColor Green
            Write-Host "Reinicie o terminal e execute este script novamente." -ForegroundColor Yellow
            exit 0
        } else {
            Write-Host "Falha ao instalar via winget. Use a Opção 1 (Download Manual)." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "Por favor, instale Python 3.12 manualmente e execute este script novamente." -ForegroundColor Yellow
        exit 1
    }
}

# Se chegou aqui, Python 3.12 está disponível
Write-Host ""
Write-Host "Criando ambiente virtual com Python 3.12..." -ForegroundColor Yellow

# Remover ambiente virtual antigo se existir
if (Test-Path "venv") {
    Write-Host "Removendo ambiente virtual antigo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Criar novo ambiente virtual
py -3.12 -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao criar ambiente virtual!" -ForegroundColor Red
    exit 1
}

Write-Host "Ambiente virtual criado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow

# Ativar ambiente virtual
& "venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao ativar ambiente virtual!" -ForegroundColor Red
    Write-Host "Execute manualmente: venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Ambiente virtual ativado!" -ForegroundColor Green
Write-Host ""
Write-Host "Verificando versão do Python no ambiente virtual..." -ForegroundColor Yellow
python --version

Write-Host ""
Write-Host "Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""
Write-Host "Instalando dependências..." -ForegroundColor Yellow
Write-Host ""

# Instalar NumPy
Write-Host "Instalando NumPy..." -ForegroundColor Yellow
python -m pip install "numpy>=1.24.0,<2.0.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar NumPy!" -ForegroundColor Red
    exit 1
}

# Instalar OpenCV
Write-Host "Instalando OpenCV..." -ForegroundColor Yellow
python -m pip install "opencv-python>=4.8.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar OpenCV!" -ForegroundColor Red
    exit 1
}

# Instalar Requests
Write-Host "Instalando Requests..." -ForegroundColor Yellow
python -m pip install "requests>=2.31.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar Requests!" -ForegroundColor Red
    exit 1
}

# Instalar EasyOCR
Write-Host "Instalando EasyOCR (pode demorar alguns minutos)..." -ForegroundColor Yellow
python -m pip install "easyocr>=1.7.0"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar EasyOCR!" -ForegroundColor Red
    exit 1
}

# Verificação final
Write-Host ""
Write-Host "Verificando instalação..." -ForegroundColor Yellow
Write-Host ""

$allOk = $true

try {
    $numpy = python -c "import numpy; print(numpy.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) { 
        Write-Host "✓ NumPy: $numpy" -ForegroundColor Green 
    } else { 
        $allOk = $false
        Write-Host "✗ NumPy: FALHOU" -ForegroundColor Red 
    }
} catch {
    $allOk = $false
    Write-Host "✗ NumPy: FALHOU" -ForegroundColor Red
}

try {
    $cv2 = python -c "import cv2; print(cv2.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) { 
        Write-Host "✓ OpenCV: $cv2" -ForegroundColor Green 
    } else { 
        $allOk = $false
        Write-Host "✗ OpenCV: FALHOU" -ForegroundColor Red 
    }
} catch {
    $allOk = $false
    Write-Host "✗ OpenCV: FALHOU" -ForegroundColor Red
}

try {
    python -c "import easyocr" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { 
        Write-Host "✓ EasyOCR: OK" -ForegroundColor Green 
    } else { 
        $allOk = $false
        Write-Host "✗ EasyOCR: FALHOU" -ForegroundColor Red 
    }
} catch {
    $allOk = $false
    Write-Host "✗ EasyOCR: FALHOU" -ForegroundColor Red
}

try {
    python -c "import requests; print(requests.__version__)" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { 
        Write-Host "✓ Requests: OK" -ForegroundColor Green 
    } else { 
        $allOk = $false
        Write-Host "✗ Requests: FALHOU" -ForegroundColor Red 
    }
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
    Write-Host "1. O ambiente virtual está ativo" -ForegroundColor White
    Write-Host "2. Configure as variáveis de ambiente (opcional)" -ForegroundColor White
    Write-Host "3. Execute: python main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Para ativar o ambiente virtual novamente:" -ForegroundColor Yellow
    Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor White
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













