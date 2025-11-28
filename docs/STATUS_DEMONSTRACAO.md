# Status da Demonstração - Execução

## Data: 2025-01-XX

## Status Atual

### ✅ API Backend
- **Status**: RODANDO
- **URL**: http://localhost:8000
- **Health Check**: ✅ OK (`{"status":"ok"}`)
- **Porta**: 8000

### ⚠️ Dispositivo IoT
- **Status**: PRONTO PARA EXECUÇÃO
- **Câmera**: ✅ Testada e funcionando (ID 0 - câmera do laptop)
- **OpenCV**: ✅ Instalado (4.12.0)
- **NumPy**: ✅ Instalado (2.3.5)
- **Requests**: ✅ Instalado
- **EasyOCR**: ⚠️ Não instalado (opcional para demonstração básica)

## Próximos Passos

### Para Executar a Demonstração Completa

1. **Instalar EasyOCR** (opcional, mas recomendado):
   ```powershell
   cd apps/iot-device
   .\venv\Scripts\Activate.ps1
   pip install easyocr
   ```

2. **Executar Dispositivo IoT**:
   ```powershell
   cd apps/iot-device
   .\venv\Scripts\Activate.ps1
   $env:API_BASE_URL="http://localhost:8000/api/v1"
   $env:CAMERA_ID=0
   python main.py
   ```

### Para Demonstração Básica (sem OCR)

Se o EasyOCR não estiver instalado, o sistema ainda pode:
- ✅ Capturar imagens da câmera
- ✅ Detectar regiões candidatas a placas
- ⚠️ Não realizará OCR (reconhecimento de texto)

## Comandos Úteis

### Verificar API
```powershell
curl http://localhost:8000/api/v1/health
```

### Verificar Dispositivo IoT
```powershell
cd apps/iot-device
.\venv\Scripts\Activate.ps1
python scripts\verify_demo_setup.py
```

### Parar API
```powershell
# Encontrar processo Python da API
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process
```

## Notas

- A API está rodando em background
- O dispositivo IoT está configurado e pronto
- A câmera do laptop (ID 0) está funcionando
- EasyOCR pode ser instalado durante a demonstração se necessário

