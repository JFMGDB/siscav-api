# Guia Rápido de Demonstração - SISCAV

Este guia fornece os passos mínimos necessários para executar uma demonstração ao-vivo do sistema de reconhecimento de placas.

## Pré-requisitos Rápidos

- Python 3.10, 3.11 ou 3.12
- **Câmera do laptop** (será utilizada a câmera integrada do notebook)
- API backend rodando

## Passos Rápidos (5 minutos)

### 1. Verificar Setup

```bash
cd apps/iot-device
python scripts/verify_demo_setup.py
```

### 2. Iniciar API (Terminal 1)

```bash
cd apps/api/src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Executar Dispositivo IoT (Terminal 2)

**Importante**: A câmera utilizada será a do próprio laptop (câmera integrada).

**Windows (PowerShell):**
```powershell
cd apps/iot-device
$env:API_BASE_URL="http://localhost:8000/api/v1"
$env:CAMERA_ID=0  # Câmera do laptop (padrão)
python main.py
```

**Linux/Mac:**
```bash
cd apps/iot-device
export API_BASE_URL="http://localhost:8000/api/v1"
export CAMERA_ID=0  # Câmera do laptop (padrão)
python main.py
```

**Nota sobre Permissões (Windows)**:
- Na primeira execução, o Windows pode solicitar permissão para acessar a câmera
- Clique em "Permitir" quando solicitado
- Se a câmera não abrir, verifique as configurações de privacidade do Windows

### 4. Demonstração

1. Posicionar placa na frente da câmera
2. Sistema detecta automaticamente
3. Verificar logs e janela de vídeo

## Comandos Úteis

### Verificar API
```bash
curl http://localhost:8000/api/v1/health
```

### Cadastrar Placa na Whitelist
```bash
curl -X POST http://localhost:8000/api/v1/whitelist/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plate": "ABC1234", "description": "Teste"}'
```

### Ver Logs de Acesso (Conteúdo Extraído)

```bash
# Listar últimos 10 logs com conteúdo extraído
curl http://localhost:8000/api/v1/access_logs/?limit=10 \
  -H "Authorization: Bearer <token>"

# Filtrar por placa específica
curl "http://localhost:8000/api/v1/access_logs/?plate=ABC1234" \
  -H "Authorization: Bearer <token>"
```

**Importante**: O campo `plate_string_detected` na resposta contém o texto exato extraído pelo OCR.

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Câmera não detectada | Verificar permissões do Windows para câmera. Tentar `CAMERA_ID=0` (padrão do laptop) |
| Permissão negada | Windows > Configurações > Privacidade > Câmera > Permitir acesso |
| API não responde | Verificar se API está rodando na porta 8000 |
| OCR lento | Reduzir resolução: `FRAME_WIDTH=640 FRAME_HEIGHT=480` |
| Muitos erros | Verificar logs com `LOG_LEVEL=DEBUG` |

## Documentação Completa

Para mais detalhes, consulte:
- `docs/DEMONSTRACAO_COMPLETA.md` - Guia completo
- `docs/operacao/01-guia-demonstracao.md` - Guia detalhado
- `docs/operacao/03-troubleshooting-instalacao.md` - Troubleshooting

