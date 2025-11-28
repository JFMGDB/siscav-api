# Nota Importante: Câmera do Laptop

## Informação Principal

**A demonstração utilizará a câmera integrada do laptop onde será realizada.**

## Configuração

### ID da Câmera

A câmera do laptop geralmente é identificada como **ID 0** (padrão). O sistema está configurado para usar `CAMERA_ID=0`.

### Permissões no Windows

Na primeira execução, o Windows pode solicitar permissão para acessar a câmera:

1. **Solicitação de Permissão**: Quando o sistema tentar acessar a câmera, o Windows mostrará uma notificação
2. **Ação**: Clique em "Permitir" ou "Sim" quando solicitado
3. **Configurações Permanentes**: 
   - Windows > Configurações > Privacidade > Câmera
   - Habilitar "Permitir que aplicativos acessem sua câmera"
   - Habilitar "Permitir que aplicativos da área de trabalho acessem sua câmera"

### Verificação Rápida

Para verificar se a câmera está acessível:

```powershell
cd apps/iot-device
.\venv\Scripts\Activate.ps1
python -c "import cv2; cap = cv2.VideoCapture(0); print('Câmera OK' if cap.isOpened() else 'Câmera não encontrada'); cap.release()"
```

### Problemas Comuns

#### 1. Câmera não abre

**Causa**: Outro aplicativo está usando a câmera
**Solução**: 
- Feche aplicativos como Teams, Zoom, Skype, etc.
- Verifique se a Câmera do Windows não está aberta

#### 2. Permissão negada

**Causa**: Windows bloqueou o acesso
**Solução**:
- Configurações > Privacidade > Câmera
- Habilitar todas as opções de acesso à câmera
- Reiniciar o aplicativo

#### 3. Câmera não detectada

**Causa**: Driver ou hardware
**Solução**:
- Verificar se a câmera funciona com a aplicação Câmera do Windows
- Atualizar drivers da câmera
- Reiniciar o sistema

### Durante a Demonstração

1. **Posicionamento**: 
   - Posicione a placa na frente da câmera do laptop
   - Mantenha distância adequada (1-2 metros)
   - Garanta boa iluminação

2. **Área de Detecção**:
   - A placa deve estar visível na tela do laptop
   - Evite reflexos e sombras
   - Mantenha a placa reta (não inclinada)

3. **Feedback Visual**:
   - O sistema mostrará uma janela com o vídeo da câmera
   - Detecções aparecerão com retângulos coloridos
   - Status será exibido (Authorized/Denied)

### Configuração Recomendada

Para melhor desempenho com câmera de laptop:

```powershell
$env:CAMERA_ID=0
$env:FRAME_WIDTH=1280
$env:FRAME_HEIGHT=720
$env:ENABLE_DISPLAY="true"  # Para ver o vídeo
$env:ENABLE_SOUND="true"    # Para feedback sonoro
```

### Teste Antes da Demonstração

Execute o script de verificação:

```powershell
cd apps/iot-device
.\venv\Scripts\Activate.ps1
python scripts\verify_demo_setup.py
```

O script verificará se a câmera está acessível e funcionando.

