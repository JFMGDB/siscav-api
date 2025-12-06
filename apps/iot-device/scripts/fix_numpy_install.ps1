# Script para Corrigir Instalação do NumPy no Python 3.14
# Resolve o erro: "fatal error C1083: Não é possível abrir arquivo incluir: 'stdalign.h'"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Correção de Instalação do NumPy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar versão do Python
$pythonVersion = python --version 2>&1
Write-Host "Versão do Python: $pythonVersion" -ForegroundColor Yellow

if ($pythonVersion -match "Python 3\.(1[3-9]|[2-9]\d)") {
    Write-Host ""
    Write-Host "PROBLEMA DETECTADO: Python 3.13+ não tem wheels pré-compilados do NumPy" -ForegroundColor Red
    Write-Host ""
    Write-Host "Soluções disponíveis:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPÇÃO 1: Usar Python 3.12 (RECOMENDADO)" -ForegroundColor Green
    Write-Host "  py -3.12 -m venv venv" -ForegroundColor White
    Write-Host "  venv\Scripts\activate" -ForegroundColor White
    Write-Host "  python -m pip install --upgrade pip" -ForegroundColor White
    Write-Host "  python -m pip install numpy opencv-python requests easyocr" -ForegroundColor White
    Write-Host ""
    Write-Host "OPÇÃO 2: Tentar instalar wheel pré-compilado (pode não funcionar)" -ForegroundColor Yellow
    Write-Host "  python -m pip install --upgrade pip" -ForegroundColor White
    Write-Host "  python -m pip install --only-binary :all: numpy" -ForegroundColor White
    Write-Host ""
    Write-Host "OPÇÃO 3: Usar Conda (gerencia melhor dependências binárias)" -ForegroundColor Yellow
    Write-Host "  conda create -n siscav python=3.12 -y" -ForegroundColor White
    Write-Host "  conda activate siscav" -ForegroundColor White
    Write-Host "  conda install numpy opencv requests -y" -ForegroundColor White
    Write-Host "  pip install easyocr" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Qual opção deseja tentar? (1, 2 ou 3)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "Verificando se Python 3.12 está disponível..." -ForegroundColor Yellow
            $py312 = py -3.12 --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Python 3.12 encontrado: $py312" -ForegroundColor Green
                Write-Host ""
                Write-Host "Criando ambiente virtual com Python 3.12..." -ForegroundColor Yellow
                py -3.12 -m venv venv
                Write-Host ""
                Write-Host "Para ativar o ambiente:" -ForegroundColor Cyan
                Write-Host "  venv\Scripts\activate" -ForegroundColor White
                Write-Host ""
                Write-Host "Depois execute o script de instalação novamente." -ForegroundColor Yellow
            } else {
                Write-Host "Python 3.12 não encontrado!" -ForegroundColor Red
                Write-Host "Baixe e instale Python 3.12 de: https://www.python.org/downloads/" -ForegroundColor Yellow
            }
        }
        "2" {
            Write-Host ""
            Write-Host "Tentando instalar NumPy com wheel pré-compilado..." -ForegroundColor Yellow
            python -m pip install --upgrade pip
            python -m pip install --only-binary :all: numpy
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "NumPy instalado com sucesso!" -ForegroundColor Green
                Write-Host "Continue com: pip install opencv-python requests easyocr" -ForegroundColor Yellow
            } else {
                Write-Host "Falha ao instalar NumPy!" -ForegroundColor Red
                Write-Host "Recomendamos usar Python 3.12 (Opção 1)" -ForegroundColor Yellow
            }
        }
        "3" {
            Write-Host ""
            Write-Host "Verificando se Conda está instalado..." -ForegroundColor Yellow
            $conda = conda --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Conda encontrado: $conda" -ForegroundColor Green
                Write-Host ""
                Write-Host "Execute os seguintes comandos:" -ForegroundColor Cyan
                Write-Host "  conda create -n siscav python=3.12 -y" -ForegroundColor White
                Write-Host "  conda activate siscav" -ForegroundColor White
                Write-Host "  conda install numpy opencv requests -y" -ForegroundColor White
                Write-Host "  pip install easyocr" -ForegroundColor White
            } else {
                Write-Host "Conda não encontrado!" -ForegroundColor Red
                Write-Host "Baixe Miniconda de: https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Yellow
            }
        }
        default {
            Write-Host "Opção inválida!" -ForegroundColor Red
        }
    }
} else {
    Write-Host ""
    Write-Host "Python compatível detectado. Tentando instalar NumPy..." -ForegroundColor Green
    Write-Host ""
    
    python -m pip install --upgrade pip
    python -m pip install "numpy>=1.24.0,<2.0.0"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "NumPy instalado com sucesso!" -ForegroundColor Green
        Write-Host "Continue com: pip install opencv-python requests easyocr" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "Erro ao instalar NumPy. Tente:" -ForegroundColor Red
        Write-Host "  python -m pip install --only-binary :all: numpy" -ForegroundColor Yellow
    }
}

Write-Host ""













