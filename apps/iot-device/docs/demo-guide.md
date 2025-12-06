# Guia de Demonstração e Avaliação de Desempenho - SISCAV

Este guia fornece instruções detalhadas para realizar demonstrações do sistema de reconhecimento de placas e avaliar o desempenho do modelo.

## Índice

1. [Quick Start](#quick-start)
2. [Pré-requisitos](#pré-requisitos)
3. [Preparação do Ambiente](#preparação-do-ambiente)
4. [Configuração do Sistema](#configuração-do-sistema)
5. [Execução da Demonstração](#execução-da-demonstração)
6. [Avaliação de Desempenho](#avaliação-de-desempenho)
7. [Coleta de Métricas](#coleta-de-métricas)
8. [Análise de Resultados](#análise-de-resultados)
9. [Troubleshooting](#troubleshooting)
10. [Checklist de Demonstração](#checklist-de-demonstração)

---

## Quick Start

### Execução Rápida (5 minutos)

#### Windows (PowerShell)

```powershell
# 1. Verificar Python (deve ser 3.10, 3.11 ou 3.12)
python --version

# 2. Navegar para o diretório
cd apps/iot-device

# 3. Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate

# 4. Atualizar pip e instalar dependências
python -m pip install --upgrade pip
pip install --only-binary :all: numpy
pip install opencv-python requests easyocr

# 5. Configurar variáveis (opcional)
$env:API_BASE_URL="http://localhost:8000/api/v1"
$env:CAMERA_ID=0

# 6. Executar
python main.py
```

#### Linux/Mac

```bash
# 1. Instalar dependências
cd apps/iot-device
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Configurar variáveis (opcional)
export API_BASE_URL="http://localhost:8000/api/v1"
export CAMERA_ID=0

# 3. Executar
python main.py
```

### Análise Rápida de Métricas

#### Windows (PowerShell)

```powershell
# Criar diretório de logs se não existir
New-Item -ItemType Directory -Force -Path logs

# Executar sistema e salvar logs
python main.py *> logs/demo.log

# Analisar métricas
python scripts/collect_metrics.py logs/demo.log
```

#### Linux/Mac

```bash
# Executar sistema e salvar logs
python main.py > logs/demo.log 2>&1

# Analisar métricas
python scripts/collect_metrics.py logs/demo.log
```

---

## Pré-requisitos

### Hardware

- **Computador/Placa de Desenvolvimento:**
  - CPU: Mínimo 2 cores, recomendado 4+ cores
  - RAM: Mínimo 4GB, recomendado 8GB+
  - GPU: Opcional, mas acelera significativamente o OCR (NVIDIA com CUDA)
  - Armazenamento: 5GB livres para dependências

- **Câmera:**
  - Webcam USB ou câmera IP
  - Resolução mínima: 640x480
  - Resolução recomendada: 1280x720 ou superior
  - Taxa de quadros: 30 FPS ou superior

- **Conectividade:**
  - Conexão de rede para comunicação com API
  - Latência baixa (< 100ms) para melhor experiência

### Software

- **Sistema Operacional:**
  - Windows 10/11, Linux (Ubuntu 20.04+), ou macOS
  - **Python 3.10, 3.11 ou 3.12** (evitar 3.13 e 3.14 por compatibilidade)

- **Dependências Python:**
  - NumPy >= 1.24.0, < 2.0.0
  - OpenCV >= 4.8.0
  - EasyOCR >= 1.7.0
  - Requests >= 2.31.0

**Nota Importante:** Python 3.13 e 3.14 podem causar problemas de compilação no Windows devido à falta de wheels pré-compilados. Use Python 3.12 ou anterior. Se encontrar problemas de instalação, consulte `docs/TROUBLESHOOTING_INSTALACAO.md`.

- **API Backend:**
  - API SISCAV rodando e acessível
  - Banco de dados configurado
  - Whitelist de placas cadastrada

---

## Preparação do Ambiente

### 1. Instalação das Dependências

#### Windows (PowerShell)

```powershell
# Navegar para o diretório do dispositivo IoT
cd apps/iot-device

# Verificar versão do Python (deve ser 3.10-3.12)
python --version

# Se for Python 3.13 ou 3.14, usar Python 3.12:
# py -3.12 -m venv venv

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Atualizar pip
python -m pip install --upgrade pip

# Instalar NumPy primeiro (forçar wheel pré-compilado)
pip install --only-binary :all: numpy

# Instalar outras dependências
pip install opencv-python requests

# Instalar EasyOCR (pode demorar alguns minutos na primeira vez)
pip install easyocr
```

**Se encontrar erro de compilação do NumPy, consulte:** `docs/TROUBLESHOOTING_INSTALACAO.md`

#### Linux/Mac

```bash
# Navegar para o diretório do dispositivo IoT
cd apps/iot-device

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Verificação da Câmera

```bash
# Testar acesso à câmera
python -c "import cv2; cap = cv2.VideoCapture(0); print('Câmera OK' if cap.isOpened() else 'Câmera não encontrada'); cap.release()"
```

**Nota:** Se tiver múltiplas câmeras, identifique o ID correto (geralmente 0, 1, 2...).

### 3. Verificação da API

```bash
# Testar conectividade com a API
curl http://localhost:8000/api/v1/health

# Resposta esperada: {"status": "ok"}
```

### 4. Preparação da Whitelist

Certifique-se de que há placas cadastradas na whitelist para teste:

```bash
# Via API (requer autenticação)
curl -X POST http://localhost:8000/api/v1/whitelist/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plate": "ABC1234", "description": "Veículo de teste"}'
```

---

## Configuração do Sistema

### Variáveis de Ambiente

Crie um arquivo `.env` no diretório `apps/iot-device/` ou configure as variáveis de ambiente:

```bash
# API Configuration
export API_BASE_URL="http://localhost:8000/api/v1"

# Camera Configuration
export CAMERA_ID=0                    # ID da câmera (0, 1, 2...)
export FRAME_WIDTH=1280              # Largura do frame (640, 1280, 1920)
export FRAME_HEIGHT=720              # Altura do frame (480, 720, 1080)

# OCR Configuration
export GPU_ENABLED=false              # true se tiver GPU NVIDIA com CUDA

# Plate Detection Configuration
export PLATE_DETECTION_COOLDOWN=3.0  # Segundos entre detecções da mesma placa

# Application Logic
export MAX_RUNTIME_SECONDS=300        # Tempo máximo de execução (0 = ilimitado)
export ENABLE_SOUND=true              # Habilitar sons de notificação
export ENABLE_DISPLAY=true            # Habilitar exibição de vídeo

# Logging
export LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
```

### Configurações Recomendadas por Cenário

#### Demonstração ao Vivo (Apresentação)

```bash
export FRAME_WIDTH=1280
export FRAME_HEIGHT=720
export ENABLE_SOUND=true
export ENABLE_DISPLAY=true
export LOG_LEVEL=INFO
export PLATE_DETECTION_COOLDOWN=3.0
```

#### Teste de Performance (Sem Display)

```bash
export FRAME_WIDTH=1920
export FRAME_HEIGHT=1080
export ENABLE_SOUND=false
export ENABLE_DISPLAY=false
export LOG_LEVEL=DEBUG
export PLATE_DETECTION_COOLDOWN=1.0
```

#### Desenvolvimento/Debug

```bash
export FRAME_WIDTH=640
export FRAME_HEIGHT=480
export ENABLE_SOUND=false
export ENABLE_DISPLAY=true
export LOG_LEVEL=DEBUG
export PLATE_DETECTION_COOLDOWN=2.0
```

---

## Execução da Demonstração

### Execução Básica

```bash
cd apps/iot-device
python main.py
```

### Execução com Configuração Customizada

```bash
# Linux/Mac
export API_BASE_URL="http://localhost:8000/api/v1"
export CAMERA_ID=0
export LOG_LEVEL=INFO
python main.py

# Windows (PowerShell)
$env:API_BASE_URL="http://localhost:8000/api/v1"
$env:CAMERA_ID=0
$env:LOG_LEVEL="INFO"
python main.py
```

### Controles Durante a Execução

- **ESC**: Encerrar aplicação
- **Ctrl+C**: Interrupção segura
- **Janela de vídeo**: Mostra detecções em tempo real

### Saída Esperada

```
2025-01-XX 10:00:00 - __main__ - INFO - Iniciando dispositivo IoT SISCAV
2025-01-XX 10:00:01 - __main__ - INFO - Serviços inicializados com sucesso
2025-01-XX 10:00:05 - __main__ - INFO - Placa detectada: ABC1234 (tipo: branca, veiculo: carro)
2025-01-XX 10:00:05 - api_client - INFO - Enviando placa ABC1234 para API
2025-01-XX 10:00:06 - api_client - INFO - Resposta da API: Authorized
2025-01-XX 10:00:06 - __main__ - INFO - Resposta da API: Authorized
```

---

## Avaliação de Desempenho

### Métricas Principais

#### 1. Precisão de Detecção

**Definição:** Porcentagem de placas corretamente detectadas em relação ao total de placas presentes.

**Cálculo:**
```
Precisão = (Placas Detectadas Corretamente / Total de Placas Presentes) × 100
```

**Como Medir:**
- Prepare um conjunto de teste com placas conhecidas
- Execute o sistema por um período determinado
- Compare detecções com ground truth
- Calcule a porcentagem de acertos

#### 2. Precisão de OCR

**Definição:** Porcentagem de caracteres corretamente reconhecidos.

**Cálculo:**
```
Precisão OCR = (Caracteres Corretos / Total de Caracteres) × 100
```

**Como Medir:**
- Para cada placa detectada, compare o texto OCR com a placa real
- Conte caracteres corretos vs. incorretos
- Calcule a média

#### 3. Taxa de Falsos Positivos

**Definição:** Porcentagem de detecções que não são placas reais.

**Cálculo:**
```
Taxa FP = (Falsos Positivos / Total de Detecções) × 100
```

#### 4. Taxa de Falsos Negativos

**Definição:** Porcentagem de placas reais que não foram detectadas.

**Cálculo:**
```
Taxa FN = (Placas Não Detectadas / Total de Placas Reais) × 100
```

#### 5. Latência de Processamento

**Definição:** Tempo entre captura do frame e resposta da API.

**Componentes:**
- Tempo de detecção
- Tempo de OCR
- Tempo de comunicação com API

**Como Medir:**
- Adicione timestamps nos logs
- Calcule diferenças entre eventos
- Analise distribuição de latências

#### 6. Taxa de Processamento (FPS)

**Definição:** Frames processados por segundo.

**Cálculo:**
```
FPS = Total de Frames Processados / Tempo Total
```

#### 7. Taxa de Sucesso da API

**Definição:** Porcentagem de requisições bem-sucedidas à API.

**Cálculo:**
```
Taxa Sucesso = (Requisições Bem-sucedidas / Total de Requisições) × 100
```

---

## Coleta de Métricas

### Script de Coleta Automática

Um script Python está disponível em `apps/iot-device/scripts/collect_metrics.py` para coletar métricas automaticamente:

**Uso básico:**
```bash
python scripts/collect_metrics.py logs/siscav.log
```

**Salvar relatório:**
```bash
python scripts/collect_metrics.py logs/siscav.log -o relatorio.txt
```

**Saída em JSON:**
```bash
python scripts/collect_metrics.py logs/siscav.log --json
```

**Métricas coletadas:**
- Total de detecções
- Taxa de sucesso de OCR
- Taxa de sucesso da API
- Taxa de autorização
- Placas únicas detectadas
- Detecções por minuto
- Erros encontrados

Ver `apps/iot-device/scripts/README.md` para mais detalhes.

### Coleta Manual

#### 1. Preparar Conjunto de Teste

- Prepare 10-20 placas conhecidas (físicas ou imagens)
- Documente a placa real de cada uma
- Anote condições de teste (iluminação, ângulo, distância)

#### 2. Executar Testes

```bash
# Redirecionar logs para arquivo
python main.py > logs/demo_$(date +%Y%m%d_%H%M%S).log 2>&1
```

#### 3. Anotar Resultados

Crie uma planilha ou arquivo CSV:

```csv
Placa Real,Placa Detectada,OCR Correto,Status API,Tempo Detecção,Observações
ABC1234,ABC1234,Sim,Authorized,0.5s,Iluminação boa
XYZ5678,XYZ5678,Sim,Denied,0.6s,Ângulo 30 graus
...
```

### Coleta via API

Consulte os logs de acesso na API:

```bash
# Listar logs de acesso
curl -X GET "http://localhost:8000/api/v1/access_logs/?limit=100" \
  -H "Authorization: Bearer <token>"
```

---

## Análise de Resultados

### Relatório de Desempenho

Crie um template de relatório:

```markdown
# Relatório de Desempenho - SISCAV

## Data: [DATA]
## Ambiente: [DESCRIÇÃO]
## Duração do Teste: [TEMPO]

## Métricas Gerais

- Total de Detecções: [N]
- Precisão de Detecção: [X]%
- Precisão de OCR: [Y]%
- Taxa de Falsos Positivos: [Z]%
- Taxa de Falsos Negativos: [W]%
- Latência Média: [T]ms
- FPS Médio: [F]
- Taxa de Sucesso da API: [S]%

## Análise por Condições

### Iluminação
- Boa: Precisão [X]%
- Média: Precisão [Y]%
- Ruim: Precisão [Z]%

### Ângulo da Placa
- Frontal (0-15°): Precisão [X]%
- Inclinado (15-45°): Precisão [Y]%
- Muito Inclinado (>45°): Precisão [Z]%

### Distância
- Próxima (< 2m): Precisão [X]%
- Média (2-5m): Precisão [Y]%
- Distante (> 5m): Precisão [Z]%

## Problemas Identificados

1. [PROBLEMA 1]
2. [PROBLEMA 2]

## Recomendações

1. [RECOMENDAÇÃO 1]
2. [RECOMENDAÇÃO 2]
```

### Análise Estatística

Use Python para análise estatística:

```python
# scripts/analyze_metrics.py
import pandas as pd
import numpy as np

# Carregar dados
df = pd.read_csv("results/test_results.csv")

# Calcular métricas
precision = df["OCR Correto"].sum() / len(df) * 100
avg_latency = df["Tempo Detecção"].mean()

print(f"Precisão OCR: {precision:.2f}%")
print(f"Latência Média: {avg_latency:.2f}s")
```

---

## Troubleshooting

### Problemas Comuns e Soluções

#### 1. Câmera Não Detectada

**Sintoma:** Erro "Failed to read from camera"

**Soluções:**
- Verificar se a câmera está conectada
- Tentar diferentes IDs (0, 1, 2...)
- Verificar permissões de acesso à câmera
- Reiniciar o sistema

#### 2. OCR Lento

**Sintoma:** Processamento muito lento, baixo FPS

**Soluções:**
- Habilitar GPU se disponível: `export GPU_ENABLED=true`
- Reduzir resolução: `export FRAME_WIDTH=640`
- Desabilitar display: `export ENABLE_DISPLAY=false`
- Verificar carga do sistema

#### 3. Muitos Falsos Positivos

**Sintoma:** Detecta objetos que não são placas

**Soluções:**
- Ajustar parâmetros do `PlateDetector`:
  - Aumentar `min_width` e `min_height`
  - Ajustar `min_aspect_ratio` e `max_aspect_ratio`
- Melhorar iluminação
- Ajustar posição da câmera

#### 4. OCR Incorreto

**Sintoma:** Placas detectadas mas texto errado

**Soluções:**
- Melhorar iluminação
- Reduzir distância da placa
- Ajustar ângulo da câmera
- Verificar qualidade da câmera
- Considerar pré-processamento adicional

#### 5. Falhas de Comunicação com API

**Sintoma:** Erros "Error sending data to API"

**Soluções:**
- Verificar se a API está rodando
- Verificar conectividade de rede
- Verificar URL da API: `export API_BASE_URL="http://correct-url"`
- Verificar timeout: aumentar se necessário
- Verificar logs da API

#### 6. Display Não Aparece

**Sintoma:** Nenhuma janela de vídeo

**Soluções:**
- Verificar: `export ENABLE_DISPLAY=true`
- Verificar se há display disponível (SSH sem X11)
- Verificar permissões de GUI
- Tentar em modo headless se não houver display

### Logs de Debug

Para diagnóstico detalhado:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

Isso mostrará informações detalhadas sobre:
- Candidatos detectados
- Processamento de OCR
- Comunicação com API
- Tempos de processamento

---

## Checklist de Demonstração

### Antes da Demonstração

- [ ] Ambiente Python configurado e dependências instaladas
- [ ] Câmera testada e funcionando
- [ ] API backend rodando e acessível
- [ ] Whitelist configurada com placas de teste
- [ ] Variáveis de ambiente configuradas
- [ ] Teste rápido executado com sucesso
- [ ] Iluminação adequada no ambiente
- [ ] Câmera posicionada corretamente
- [ ] Placas de teste preparadas
- [ ] Scripts de coleta de métricas prontos (se aplicável)

### Durante a Demonstração

- [ ] Sistema iniciado corretamente
- [ ] Janela de vídeo visível (se habilitada)
- [ ] Logs sendo gerados
- [ ] Primeira detecção bem-sucedida
- [ ] Feedback sonoro funcionando (se habilitado)
- [ ] Comunicação com API funcionando
- [ ] Anotações de resultados (se necessário)

### Após a Demonstração

- [ ] Logs salvos para análise
- [ ] Métricas calculadas
- [ ] Relatório gerado
- [ ] Problemas documentados
- [ ] Melhorias identificadas
- [ ] Feedback coletado

---

## Exemplo de Sessão de Teste

### Cenário: Teste de Precisão

1. **Preparação:**
   ```bash
   export LOG_LEVEL=INFO
   export ENABLE_DISPLAY=true
   export ENABLE_SOUND=false
   python main.py > logs/test_precision_$(date +%Y%m%d_%H%M%S).log 2>&1
   ```

2. **Execução:**
   - Apresentar 10 placas conhecidas uma por uma
   - Anotar cada detecção
   - Aguardar 3 segundos entre placas (cooldown)

3. **Análise:**
   ```bash
   # Contar detecções nos logs
   grep "Placa detectada:" logs/test_precision_*.log | wc -l
   
   # Verificar precisão
   python scripts/analyze_metrics.py
   ```

### Cenário: Teste de Performance

1. **Preparação:**
   ```bash
   export ENABLE_DISPLAY=false
   export LOG_LEVEL=DEBUG
   export MAX_RUNTIME_SECONDS=60
   python main.py > logs/test_performance.log 2>&1
   ```

2. **Métricas a Coletar:**
   - FPS médio
   - Latência de detecção
   - Latência de OCR
   - Latência total (até resposta da API)
   - Uso de CPU/GPU
   - Uso de memória

---

## Referências

- Documentação técnica: `docs/IOT_DEVICE_REFACTORING.md`
- Resumo executivo: `docs/IOT_DEVICE_SUMMARY.md`
- Troubleshooting de instalação: `docs/TROUBLESHOOTING_INSTALACAO.md`
- Scripts auxiliares: `apps/iot-device/scripts/README.md`
- Código-fonte: `apps/iot-device/`

## Apêndices

### A. Exemplo de Relatório Gerado

```
============================================================
RELATÓRIO DE DESEMPENHO - SISCAV IoT DEVICE
============================================================

MÉTRICAS GERAIS
------------------------------------------------------------
Total de Detecções: 25
Placas Únicas: 8
OCR Bem-sucedido: 23
OCR Falhou: 2
Taxa de Sucesso OCR: 92.00%

COMUNICAÇÃO COM API
------------------------------------------------------------
Requisições Bem-sucedidas: 23
Requisições Falhadas: 0
Timeouts: 0
Taxa de Sucesso API: 100.00%

AUTORIZAÇÕES
------------------------------------------------------------
Autorizadas: 15
Negadas: 8
Taxa de Autorização: 65.22%

SESSÃO
------------------------------------------------------------
Duração: 120.50 segundos
Detecções por Minuto: 12.45

PLACAS DETECTADAS
------------------------------------------------------------
  ABC1234: 5 vez(es)
  XYZ5678: 3 vez(es)
  ...
============================================================
```

### B. Template de Planilha de Teste

Crie uma planilha CSV com as seguintes colunas:

| Placa Real | Placa Detectada | OCR Correto | Status API | Tempo Detecção | Iluminação | Ângulo | Distância | Observações |
|------------|-----------------|-------------|-----------|----------------|------------|--------|-----------|-------------|
| ABC1234     | ABC1234         | Sim         | Authorized| 0.5s           | Boa        | 0°     | 2m        | -           |
| XYZ5678     | XYZ5678         | Sim         | Denied    | 0.6s           | Média      | 30°    | 3m        | -           |

### C. Comandos Úteis

```bash
# Executar com logs detalhados
LOG_LEVEL=DEBUG python main.py

# Executar sem display (headless)
ENABLE_DISPLAY=false python main.py

# Executar com cooldown reduzido para testes
PLATE_DETECTION_COOLDOWN=1.0 python main.py

# Executar por tempo limitado
MAX_RUNTIME_SECONDS=60 python main.py
```

---

## Suporte

Para problemas ou dúvidas:
1. Consultar logs com `LOG_LEVEL=DEBUG`
2. Verificar documentação técnica
3. Revisar seção de Troubleshooting
4. Consultar equipe de desenvolvimento

