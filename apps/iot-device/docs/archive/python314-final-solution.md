# Solução Final: Python 3.14 e Dependências

## Status da Instalação

### Dependências Instaladas com Sucesso

- **NumPy 2.3.5** - Instalado usando wheel pré-compilado
- **OpenCV 4.12.0** - Instalado com sucesso
- **Requests 2.32.5** - Instalado com sucesso

### Dependência com Problema

- **EasyOCR** - Não pode ser instalado no Python 3.14 porque:
  - Requer `scikit-image` como dependência
  - `scikit-image` não tem wheel pré-compilado para Python 3.14
  - Tentativa de compilação falha com erros de C++

## Soluções Disponíveis

### Opção 1: Usar Python 3.12 (RECOMENDADO)

Esta é a solução mais confiável e recomendada:

```powershell
# 1. Baixar e instalar Python 3.12
# https://www.python.org/downloads/release/python-3120/

# 2. Criar ambiente virtual com Python 3.12
py -3.12 -m venv venv
venv\Scripts\activate

# 3. Instalar todas as dependências
python -m pip install --upgrade pip
python -m pip install numpy opencv-python requests easyocr

# 4. Verificar
python -c "import numpy, cv2, easyocr, requests; print('OK!')"
```

### Opção 2: Usar EasyOCR sem scikit-image (Experimental)

Tentar instalar EasyOCR sem a dependência problemática:

```powershell
# Instalar dependências básicas do EasyOCR
python -m pip install torch torchvision Pillow

# Tentar instalar EasyOCR sem scikit-image
python -m pip install easyocr --no-deps
python -m pip install pyyaml
```

**Nota:** Isso pode não funcionar completamente, pois scikit-image pode ser necessário em runtime.

### Opção 3: Usar Conda

Conda gerencia melhor dependências binárias:

```powershell
# Instalar Miniconda: https://docs.conda.io/en/latest/miniconda.html

# Criar ambiente
conda create -n siscav python=3.12 -y
conda activate siscav

# Instalar dependências
conda install numpy opencv requests -y
pip install easyocr
```

## Recomendação Final

**Use Python 3.12** para este projeto. Python 3.14 é muito recente e muitas bibliotecas científicas ainda não têm suporte completo.

## Verificação Atual

Execute para verificar o que está instalado:

```powershell
python -c "import sys; print('Python:', sys.version)"
python -c "import numpy; print('NumPy:', numpy.__version__)" 2>$null || echo "NumPy: NÃO INSTALADO"
python -c "import cv2; print('OpenCV:', cv2.__version__)" 2>$null || echo "OpenCV: NÃO INSTALADO"
python -c "import requests; print('Requests: OK')" 2>$null || echo "Requests: NÃO INSTALADO"
python -c "import easyocr; print('EasyOCR: OK')" 2>$null || echo "EasyOCR: NÃO INSTALADO"
```

## Próximos Passos

1. Se você tem Python 3.12 instalado:
   - Use `py -3.12` para criar o ambiente virtual
   - Siga a Opção 1 acima

2. Se você não tem Python 3.12:
   - Baixe de: https://www.python.org/downloads/release/python-3120/
   - Instale (marque "Add Python to PATH")
   - Siga a Opção 1 acima

3. Alternativamente, use Conda (Opção 3) se preferir

## Documentação Relacionada

- `docs/TROUBLESHOOTING_INSTALACAO.md` - Guia completo de troubleshooting
- `apps/iot-device/INSTALACAO.md` - Guia de instalação
- `docs/SOLUCAO_ERRO_NUMPY.md` - Solução rápida para erro do NumPy

