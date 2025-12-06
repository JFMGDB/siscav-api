# Instalação do Python 3.12 - Guia Rápido

## Por que Python 3.12?

Python 3.14 é muito recente e muitas bibliotecas científicas (como scikit-image, usado pelo EasyOCR) ainda não têm wheels pré-compilados. Python 3.12 tem suporte completo de todas as dependências necessárias.

## Instalação Rápida

### Método 1: Script Automático (Recomendado)

```powershell
cd apps/iot-device
.\scripts\setup_python312.ps1
```

O script irá:
1. Verificar se Python 3.12 está instalado
2. Oferecer instalação via winget (se disponível)
3. Criar ambiente virtual com Python 3.12
4. Instalar todas as dependências
5. Verificar instalação

### Método 2: Instalação Manual

#### Passo 1: Baixar Python 3.12

1. Acesse: https://www.python.org/downloads/release/python-3120/
2. Baixe "Windows installer (64-bit)"
3. Execute o instalador

#### Passo 2: Durante a Instalação

- **IMPORTANTE:** Marque a opção "Add Python to PATH"
- Clique em "Install Now"

#### Passo 3: Verificar Instalação

Abra um novo PowerShell e execute:

```powershell
py -3.12 --version
```

Deve mostrar: `Python 3.12.0`

#### Passo 4: Configurar Ambiente

```powershell
cd apps/iot-device

# Criar ambiente virtual
py -3.12 -m venv venv

# Ativar ambiente
venv\Scripts\Activate.ps1

# Instalar dependências
python -m pip install --upgrade pip
python -m pip install numpy opencv-python requests easyocr

# Verificar
python -c "import numpy, cv2, easyocr, requests; print('OK!')"
```

### Método 3: Usar Winget

```powershell
winget install Python.Python.3.12
```

Depois execute o script `setup_python312.ps1` ou siga o Método 2, Passo 4.

## Verificação

Após instalação, verifique:

```powershell
# Verificar Python
python --version
# Deve mostrar: Python 3.12.x

# Verificar dependências
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import easyocr; print('EasyOCR: OK')"
python -c "import requests; print('Requests: OK')"
```

## Problemas Comuns

### "py -3.12 não encontrado"

- Certifique-se de que Python 3.12 está instalado
- Verifique se "Add Python to PATH" foi marcado durante instalação
- Reinicie o terminal após instalação

### "Execution Policy" no PowerShell

Se encontrar erro de política de execução:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Ambiente Virtual Não Ativa

Execute manualmente:

```powershell
.\venv\Scripts\Activate.ps1
```

## Próximos Passos

Após instalação bem-sucedida:

1. Configure variáveis de ambiente (veja `docs/GUIA_DEMONSTRACAO_E_AVALIACAO.md`)
2. Execute o sistema: `python main.py`
3. Consulte o guia de demonstração para mais detalhes













