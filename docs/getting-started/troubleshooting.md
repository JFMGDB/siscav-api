# Troubleshooting - Problemas de Instalação

Este documento aborda problemas comuns durante a instalação das dependências do dispositivo IoT.

## Erro: Compilação do NumPy Falha (Windows)

### Sintoma

```
fatal error C1083: Não é possível abrir arquivo incluir: 'stdalign.h': No such file or directory
error: metadata-generation-failed
```

**Solução Rápida:** Execute o script de correção:
```powershell
cd apps/iot-device
.\scripts\fix_numpy_install.ps1
```

### Causa

O NumPy está tentando compilar do código-fonte, mas há incompatibilidade com:
- Python 3.13 ou 3.14 (muito recentes, podem não ter wheels pré-compilados)
- Compilador C/C++ desatualizado ou mal configurado
- Falta de Visual Studio Build Tools

### Soluções

#### Solução 1: Usar Python 3.10, 3.11 ou 3.12 (Recomendado)

Python 3.13 e 3.14 são muito recentes e podem não ter suporte completo de todas as bibliotecas.

```powershell
# Verificar versão do Python
python --version

# Se for 3.13 ou 3.14, instalar Python 3.12 ou 3.11
# Download: https://www.python.org/downloads/

# Criar novo ambiente virtual com Python 3.12
py -3.12 -m venv venv
venv\Scripts\activate

# Ou usar Python 3.11
py -3.11 -m venv venv
venv\Scripts\activate
```

#### Solução 2: Instalar Wheel Pré-compilado

Forçar instalação de wheel pré-compilado em vez de compilar:

```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Instalar NumPy usando wheel pré-compilado
pip install --only-binary :all: numpy

# Ou especificar versão específica
pip install numpy==1.26.4 --only-binary :all:
```

#### Solução 3: Instalar Visual Studio Build Tools

Se precisar compilar (não recomendado):

```powershell
# Baixar e instalar Visual Studio Build Tools
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

# Instalar "Desktop development with C++" workload
# Reiniciar terminal após instalação
```

#### Solução 4: Usar Conda (Alternativa)

Conda gerencia melhor dependências binárias:

```powershell
# Instalar Miniconda: https://docs.conda.io/en/latest/miniconda.html

# Criar ambiente
conda create -n siscav python=3.12
conda activate siscav

# Instalar dependências
conda install numpy opencv requests
pip install easyocr
```

### Verificação

Após aplicar uma solução, verificar:

```powershell
python -c "import numpy; print(numpy.__version__)"
python -c "import cv2; print(cv2.__version__)"
```

---

## Erro: EasyOCR Não Instala

### Sintoma

```
ERROR: Could not find a version that satisfies the requirement easyocr
```

### Solução

```powershell
# Atualizar pip
python -m pip install --upgrade pip

# Instalar EasyOCR
pip install easyocr

# Se falhar, instalar dependências manualmente
pip install torch torchvision torchaudio
pip install opencv-python-headless
pip install easyocr
```

---

## Erro: OpenCV Não Encontrado

### Sintoma

```
ModuleNotFoundError: No module named 'cv2'
```

### Solução

```powershell
# Instalar OpenCV
pip install opencv-python

# Ou versão headless (sem GUI, para servidores)
pip install opencv-python-headless
```

---

## Erro: Permissão Negada no Windows

### Sintoma

```
PermissionError: [WinError 5] Access is denied
```

### Solução

```powershell
# Executar PowerShell como Administrador
# Ou usar --user flag
pip install --user -r requirements.txt

# Ou usar ambiente virtual
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Erro: Câmera Não Detectada

### Sintoma

```
RuntimeError: Failed to read from camera
```

### Solução

```powershell
# Verificar câmeras disponíveis
python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"

# Testar diferentes IDs
$env:CAMERA_ID=0
python main.py

# Se não funcionar, tentar ID 1, 2, etc.
$env:CAMERA_ID=1
python main.py
```

---

## Instalação Completa - Passo a Passo (Windows)

### Método 1: Usar Script de Instalação Automática (Recomendado)

```powershell
cd apps/iot-device
.\scripts\install_dependencies.ps1
```

O script detecta automaticamente problemas e oferece soluções.

### Método 2: Python 3.12 com pip (Manual)

```powershell
# 1. Verificar Python
py -3.12 --version

# 2. Criar ambiente virtual
py -3.12 -m venv venv

# 3. Ativar ambiente
venv\Scripts\activate

# 4. Atualizar pip
python -m pip install --upgrade pip

# 5. Instalar NumPy (forçar wheel)
pip install --only-binary :all: numpy

# 6. Instalar outras dependências
pip install opencv-python requests

# 7. Instalar EasyOCR
pip install easyocr

# 8. Verificar instalação
python -c "import numpy, cv2, easyocr; print('OK')"
```

### Método 2: Usando Conda

```powershell
# 1. Instalar Miniconda
# https://docs.conda.io/en/latest/miniconda.html

# 2. Criar ambiente
conda create -n siscav python=3.12 -y
conda activate siscav

# 3. Instalar dependências via conda
conda install numpy opencv requests -y

# 4. Instalar EasyOCR via pip
pip install easyocr

# 5. Verificar
python -c "import numpy, cv2, easyocr; print('OK')"
```

---

## Verificação de Instalação

Script de verificação:

```powershell
# Criar arquivo: check_installation.ps1
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import numpy
    print(f'NumPy: {numpy.__version__} - OK')
except ImportError as e:
    print(f'NumPy: FALHOU - {e}')

try:
    import cv2
    print(f'OpenCV: {cv2.__version__} - OK')
except ImportError as e:
    print(f'OpenCV: FALHOU - {e}')

try:
    import easyocr
    print('EasyOCR: OK')
except ImportError as e:
    print(f'EasyOCR: FALHOU - {e}')

try:
    import requests
    print(f'Requests: {requests.__version__} - OK')
except ImportError as e:
    print(f'Requests: FALHOU - {e}')
"
```

Executar:
```powershell
.\check_installation.ps1
```

---

## Requisitos Mínimos do Sistema

### Windows

- **Python:** 3.10, 3.11 ou 3.12 (evitar 3.13 e 3.14 por enquanto)
- **RAM:** 4GB mínimo, 8GB recomendado
- **Espaço:** 5GB livres
- **Câmera:** USB 2.0 ou superior

### Dependências Python

- NumPy >= 1.24.0
- OpenCV >= 4.8.0
- EasyOCR >= 1.7.0
- Requests >= 2.31.0

---

## Links Úteis

- Python Downloads: https://www.python.org/downloads/
- NumPy Wheels: https://pypi.org/project/numpy/#files
- Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
- Miniconda: https://docs.conda.io/en/latest/miniconda.html

---

## Suporte Adicional

Se nenhuma solução funcionar:

1. Verificar logs completos do erro
2. Verificar versão exata do Python: `python --version`
3. Verificar arquitetura: `python -c "import platform; print(platform.machine())"`
4. Coletar informações do sistema
5. Abrir issue no repositório do projeto

