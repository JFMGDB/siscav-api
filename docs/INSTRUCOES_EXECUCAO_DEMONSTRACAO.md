# Instruções para Execução da Demonstração

## Status Atual

### ✅ API Backend
- **Status**: RODANDO
- **URL**: http://localhost:8000
- **Health Check**: ✅ Funcionando
- **Comando para iniciar** (se necessário):
  ```powershell
  cd C:\src\personal\siscav-api\apps\api\src
  $env:PYTHONPATH="C:\src\personal\siscav-api"
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```

### ⚠️ Dispositivo IoT
- **Status**: PRONTO, mas EasyOCR não instalado
- **Câmera**: ✅ Funcionando (ID 0 - laptop)
- **OpenCV**: ✅ Instalado
- **NumPy**: ✅ Instalado
- **EasyOCR**: ❌ Não instalado (problemas com Python 3.14)

## Problema Identificado

O EasyOCR não pode ser instalado no Python 3.14 devido a problemas de compilação de dependências (scikit-image). 

## Soluções

### Opção 1: Usar Python 3.12 (Recomendado)

1. Instalar Python 3.12
2. Criar novo ambiente virtual:
   ```powershell
   cd apps/iot-device
   py -3.12 -m venv venv312
   .\venv312\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Executar com Python 3.12

### Opção 2: Executar Demonstração Parcial (Sem OCR)

O sistema pode funcionar parcialmente sem EasyOCR:
- ✅ Captura de imagens
- ✅ Detecção de regiões de placas
- ❌ OCR (reconhecimento de texto) não funcionará

Para testar a detecção visual:
```powershell
cd C:\src\personal\siscav-api\apps\iot-device
.\venv\Scripts\Activate.ps1
$env:API_BASE_URL="http://localhost:8000/api/v1"
$env:CAMERA_ID=0
python run.py
```

### Opção 3: Instalar EasyOCR via Conda (Alternativa)

Se tiver Conda instalado:
```powershell
conda create -n siscav python=3.12
conda activate siscav
pip install easyocr
```

## Execução Atual

### Passo 1: Verificar API

```powershell
curl http://localhost:8000/api/v1/health
# Deve retornar: {"status":"ok"}
```

### Passo 2: Executar Dispositivo IoT (com run.py)

```powershell
cd C:\src\personal\siscav-api\apps\iot-device
.\venv\Scripts\Activate.ps1
$env:API_BASE_URL="http://localhost:8000/api/v1"
$env:CAMERA_ID=0
$env:ENABLE_DISPLAY="true"
$env:ENABLE_SOUND="true"
python run.py
```

**Nota**: O script `run.py` foi criado para resolver o problema de imports (iot-device vs iot_device).

## O que Funcionará

- ✅ Captura de vídeo da câmera do laptop
- ✅ Detecção visual de regiões candidatas a placas
- ✅ Exibição em tempo real com retângulos
- ⚠️ OCR não funcionará sem EasyOCR instalado

## Próximos Passos Recomendados

1. **Para demonstração completa**: Usar Python 3.12 e instalar EasyOCR
2. **Para demonstração parcial**: Executar com `run.py` para mostrar detecção visual
3. **Para produção**: Considerar usar Python 3.10, 3.11 ou 3.12 (não 3.14)

## Arquivos Criados

- `apps/iot-device/run.py`: Script wrapper para executar o dispositivo IoT corretamente

