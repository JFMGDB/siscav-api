# Guia de Instalação - Dispositivo IoT SISCAV

## Requisitos

- Python 3.10, 3.11 ou 3.12 (evitar 3.13 e 3.14)
- pip atualizado
- Câmera USB (opcional para testes)

## Instalação Rápida

### Windows (PowerShell) - Método Automático (Recomendado)

```powershell
# 1. Navegar para o diretório
cd apps/iot-device

# 2. Executar script de instalação automática
.\scripts\install_dependencies.ps1
```

O script detecta problemas automaticamente e oferece soluções.

### Windows (PowerShell) - Método Manual

```powershell
# 1. Verificar versão do Python
python --version
# Deve mostrar Python 3.10.x, 3.11.x ou 3.12.x

# Se for Python 3.13 ou 3.14, use Python 3.12:
# py -3.12 -m venv venv

# 2. Navegar para o diretório
cd apps/iot-device

# 3. Criar ambiente virtual
python -m venv venv

# 4. Ativar ambiente virtual
venv\Scripts\activate

# 5. Atualizar pip
python -m pip install --upgrade pip

# 6. Instalar NumPy (forçar wheel pré-compilado)
pip install --only-binary :all: numpy

# 7. Instalar outras dependências
pip install opencv-python requests

# 8. Instalar EasyOCR
pip install easyocr

# 9. Verificar instalação
python -c "import numpy, cv2, easyocr, requests; print('Instalação OK!')"
```

**Se encontrar erro de compilação do NumPy:**
```powershell
.\scripts\fix_numpy_install.ps1
```

### Linux/Mac

```bash
# 1. Verificar versão do Python
python3 --version

# 2. Navegar para o diretório
cd apps/iot-device

# 3. Criar ambiente virtual
python3 -m venv venv

# 4. Ativar ambiente virtual
source venv/bin/activate

# 5. Atualizar pip
pip install --upgrade pip

# 6. Instalar dependências
pip install -r requirements.txt

# 7. Verificar instalação
python -c "import numpy, cv2, easyocr, requests; print('Instalação OK!')"
```

## Problemas de Instalação?

Consulte `docs/TROUBLESHOOTING_INSTALACAO.md` para soluções de problemas comuns.

## Próximos Passos

Após instalação bem-sucedida:

1. Configure as variáveis de ambiente (veja `docs/GUIA_DEMONSTRACAO_E_AVALIACAO.md`)
2. Execute o sistema: `python main.py`
3. Consulte o guia de demonstração para mais detalhes

