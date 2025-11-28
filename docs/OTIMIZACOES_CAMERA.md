# Otimizações de Performance da Câmera

## Problema Identificado

A câmera estava lenta e travando durante a demonstração.

## Otimizações Implementadas

### 1. Redução de Resolução

**Antes:**
- Resolução: 640x480 pixels

**Depois:**
- Resolução: 320x240 pixels (redução de 75% na área de processamento)

**Impacto:** Reduz significativamente o processamento necessário por frame.

### 2. Limitação de FPS

**Nova Configuração:**
- `FPS_LIMIT = 10` (configurável via variável de ambiente)

**Implementação:**
- Controle manual de FPS no `CameraService`
- Descartar frames antigos do buffer
- Intervalo mínimo entre frames

**Impacto:** Reduz a carga de processamento e evita travamentos.

### 3. Otimização do Buffer da Câmera

**Mudança:**
- `CAP_PROP_BUFFERSIZE = 1` (buffer mínimo)

**Impacto:** Reduz latência e evita processamento de frames desatualizados.

### 4. Processamento Seletivo de Frames

**Implementação:**
- Processar apenas 1 a cada 3 frames (`frame_skip = 2`)
- Detecção de placas apenas em frames selecionados
- Exibição sempre ativa para feedback visual

**Impacto:** Reduz carga de CPU mantendo feedback visual fluido.

### 5. Aumento do Cooldown de Detecção

**Antes:**
- `PLATE_DETECTION_COOLDOWN = 3.0` segundos

**Depois:**
- `PLATE_DETECTION_COOLDOWN = 5.0` segundos

**Impacto:** Reduz processamento de OCR e chamadas à API.

## Configurações Ajustáveis

Todas as otimizações podem ser ajustadas via variáveis de ambiente:

```powershell
# Resolução (padrão: 320x240)
$env:FRAME_WIDTH="320"
$env:FRAME_HEIGHT="240"

# FPS máximo (padrão: 10)
$env:FPS_LIMIT="10"

# Cooldown entre detecções (padrão: 5.0 segundos)
$env:PLATE_DETECTION_COOLDOWN="5.0"
```

## Resultados Esperados

- ✅ Câmera mais fluida e responsiva
- ✅ Menos travamentos
- ✅ Menor uso de CPU
- ✅ Melhor experiência durante demonstração
- ⚠️ Detecção ligeiramente menos frequente (compensado pelo cooldown)

## Trade-offs

**Vantagens:**
- Performance muito melhor
- Menos travamentos
- Menor uso de recursos

**Desvantagens:**
- Resolução menor (ainda suficiente para detecção de placas)
- Detecção um pouco menos frequente (aceitável para demonstração)

## Próximos Passos (Opcional)

Se ainda houver problemas de performance:

1. Reduzir ainda mais a resolução: `FRAME_WIDTH=160 FRAME_HEIGHT=120`
2. Aumentar frame skip: modificar `frame_skip = 3` ou `4`
3. Reduzir FPS: `FPS_LIMIT=5`
4. Desabilitar display temporariamente: `ENABLE_DISPLAY=false`

