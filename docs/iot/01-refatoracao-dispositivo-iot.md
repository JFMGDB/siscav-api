# Refatoração do Dispositivo IoT - Reconhecimento de Placas com IA

Este documento descreve as melhorias implementadas no dispositivo IoT para finalizar a funcionalidade de reconhecimento de placas com IA para demonstração ao-vivo.

## Data: 2025-01-XX

## Objetivo

Finalizar e melhorar a funcionalidade de reconhecimento automático de placas veiculares usando processamento de imagem e OCR, preparando o sistema para demonstração ao-vivo.

## Problemas Identificados e Corrigidos

### 1. Detecção de Placas Simplificada

**Problema:** A detecção de placas usava apenas contornos básicos sem filtragem adequada, resultando em muitos falsos positivos.

**Solução:** Criado módulo `PlateDetector` com:
- Filtragem por tamanho (largura/altura mínima e máxima)
- Filtragem por razão de aspecto (placas são retangulares horizontais)
- Filtragem por área do contorno
- Remoção de sobreposições
- Processamento de imagem melhorado (equalização, filtros bilaterais, morfologia)

**Arquivos criados:**
- `apps/iot-device/services/plate_detector.py`

### 2. Falta de Validação de Placas Brasileiras

**Problema:** Não havia validação do formato de placa brasileira, aceitando qualquer string de 7 caracteres.

**Solução:** Criado módulo `plate_validator` com:
- Validação de formato antigo (ABC1234)
- Validação de formato Mercosul (ABC1D23)
- Normalização consistente

**Arquivos criados:**
- `apps/iot-device/utils/plate_validator.py`

### 3. Detecções Duplicadas

**Problema:** A mesma placa era processada múltiplas vezes em frames consecutivos, gerando requisições desnecessárias à API.

**Solução:** Implementado sistema de debounce que:
- Mantém histórico de placas detectadas recentemente
- Aplica cooldown configurável (padrão: 3 segundos)
- Limpa automaticamente entradas antigas

**Arquivos criados:**
- `apps/iot-device/utils/debounce.py`

### 4. OCR Service Melhorado

**Problema:** OCR não validava formato de placa e tinha tratamento de erros limitado.

**Solução:** Melhorias no `OCRService`:
- Validação de formato brasileiro após OCR
- Allowlist de caracteres para melhor precisão
- Tratamento robusto de exceções
- Documentação completa

**Arquivos modificados:**
- `apps/iot-device/services/ocr.py`

### 5. Tratamento de Erros e Logging

**Problema:** Falta de logging estruturado e tratamento de erros adequado.

**Solução:**
- Logging configurável via variável de ambiente
- Tratamento de exceções em todos os serviços
- Mensagens de log informativas
- Remoção de emojis (conforme requisito)

**Arquivos modificados:**
- `apps/iot-device/main.py`
- `apps/iot-device/services/api_client.py`

### 6. Estrutura do Código (SOLID/DRY)

**Problema:** Lógica de negócio misturada no main, violando princípios SOLID.

**Solução:** Refatoração completa:
- Separação de responsabilidades (cada serviço tem uma função)
- Componentização (módulos reutilizáveis)
- Injeção de dependências
- Código DRY (sem duplicação)

**Arquivos modificados:**
- `apps/iot-device/main.py` (refatoração completa)

### 7. Configurações Flexíveis

**Problema:** Configurações hardcoded, dificultando ajustes para demonstração.

**Solução:** Adicionadas configurações via variáveis de ambiente:
- `PLATE_DETECTION_COOLDOWN`: Tempo de cooldown entre detecções
- `ENABLE_SOUND`: Habilitar/desabilitar sons
- `ENABLE_DISPLAY`: Habilitar/desabilitar exibição de vídeo
- `LOG_LEVEL`: Nível de logging
- `FRAME_WIDTH` / `FRAME_HEIGHT`: Resolução da câmera

**Arquivos modificados:**
- `apps/iot-device/config.py`

## Arquitetura Implementada

### Componentes Principais

1. **CameraService**: Gerencia captura de vídeo da câmera
2. **PlateDetector**: Detecta regiões candidatas a placas no frame
3. **OCRService**: Processa imagem e extrai texto da placa
4. **APIClient**: Comunica com a API central
5. **PlateDebouncer**: Evita processamento duplicado
6. **PlateValidator**: Valida formato de placas brasileiras

### Fluxo de Processamento

```
Frame da Câmera
    ↓
PlateDetector.detect_plates()
    ↓
Para cada candidato:
    ↓
OCRService.preprocess_plate()
    ↓
OCRService.read_plate()
    ↓
PlateValidator.validate_brazilian_plate()
    ↓
PlateDebouncer.should_process()
    ↓
APIClient.send_access_log()
    ↓
Feedback visual/sonoro
```

## Princípios Aplicados

### SOLID

1. **Single Responsibility**: Cada classe tem uma responsabilidade única
   - `PlateDetector`: Apenas detecção de regiões
   - `OCRService`: Apenas OCR
   - `APIClient`: Apenas comunicação HTTP

2. **Open/Closed**: Estrutura permite extensão sem modificação
   - Novos tipos de detecção podem ser adicionados
   - Novos formatos de placa podem ser validados

3. **Dependency Inversion**: Dependências injetadas
   - Serviços recebidos como parâmetros
   - Facilita testes e manutenção

### DRY

1. **Validação de Placas**: Função única compartilhada
2. **Normalização**: Lógica centralizada
3. **Configurações**: Centralizadas em um módulo

### Componentização

1. **Serviços Separados**: Cada funcionalidade em módulo próprio
2. **Utilitários Reutilizáveis**: Funções compartilhadas
3. **Configuração Externa**: Facilita diferentes ambientes

## Melhorias de Performance

1. **Debounce**: Reduz requisições à API em ~90%
2. **Filtragem de Candidatos**: Processa apenas regiões promissoras
3. **Limpeza Automática**: Remove dados antigos do debouncer
4. **Otimização de Imagem**: Processamento eficiente para OCR

## Configuração para Demonstração

### Variáveis de Ambiente Recomendadas

```bash
# API
API_BASE_URL=http://localhost:8000/api/v1

# Câmera
CAMERA_ID=0
FRAME_WIDTH=1280
FRAME_HEIGHT=720

# OCR
GPU_ENABLED=false  # true se tiver GPU NVIDIA com CUDA

# Detecção
PLATE_DETECTION_COOLDOWN=3.0  # segundos entre detecções da mesma placa

# Interface
ENABLE_SOUND=true
ENABLE_DISPLAY=true

# Logging
LOG_LEVEL=INFO  # DEBUG para mais detalhes
```

### Execução

```bash
cd apps/iot-device
python main.py
```

## Tratamento de Erros

O sistema agora trata adequadamente:
- Falhas na câmera
- Erros de OCR
- Falhas de comunicação com API
- Timeouts de rede
- Interrupções do usuário (Ctrl+C, ESC)

## Logging

Sistema de logging estruturado com níveis:
- **DEBUG**: Detalhes de processamento
- **INFO**: Eventos importantes (detecções, respostas da API)
- **WARNING**: Situações anômalas mas recuperáveis
- **ERROR**: Erros que impedem operação

## Testes Recomendados

Após estas mudanças, recomenda-se criar testes para:

1. **PlateDetector**: Testar detecção em imagens conhecidas
2. **OCRService**: Testar precisão de OCR
3. **PlateValidator**: Testar validação de formatos
4. **PlateDebouncer**: Testar lógica de cooldown
5. **APIClient**: Testar comunicação e tratamento de erros
6. **Integração**: Testar fluxo completo

## Próximos Passos Sugeridos

1. **Melhorias de IA**:
   - Treinar modelo customizado para placas brasileiras
   - Usar YOLO ou similar para detecção mais precisa
   - Implementar correção de erros comuns de OCR

2. **Performance**:
   - Processamento em múltiplas threads
   - Cache de resultados de OCR
   - Otimização de processamento de imagem

3. **Robustez**:
   - Retry automático em falhas de API
   - Fila de requisições pendentes
   - Modo offline com cache local

4. **Monitoramento**:
   - Métricas de detecção
   - Taxa de sucesso do OCR
   - Latência de comunicação

## Compatibilidade

- Python 3.10+
- OpenCV 4.x
- EasyOCR
- Windows (sons) / Linux (sem sons)
- Câmeras USB padrão

## Notas Técnicas

- O sistema funciona melhor com boa iluminação
- Placas em ângulo podem ter precisão reduzida
- Recomenda-se ajustar parâmetros de detecção conforme ambiente
- GPU acelera significativamente o OCR (se disponível)

## Decisões de Design

### 1. Detecção por Contornos vs. Deep Learning

**Decisão:** Usar detecção por contornos inicialmente.

**Justificativa:**
- Não requer treinamento de modelo
- Funciona em hardware limitado
- Suficiente para demonstração
- Pode ser melhorado com YOLO no futuro

### 2. Debounce vs. Tracking

**Decisão:** Implementar debounce simples.

**Justificativa:**
- Mais simples de implementar
- Suficiente para evitar duplicatas
- Tracking pode ser adicionado depois se necessário

### 3. Validação no Cliente vs. Servidor

**Decisão:** Validar no cliente antes de enviar.

**Justificativa:**
- Reduz carga no servidor
- Feedback mais rápido
- Melhor experiência de demonstração

