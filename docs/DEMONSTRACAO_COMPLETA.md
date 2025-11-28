# Guia Completo de Demonstração - Sistema SISCAV

## Visão Geral

Este documento consolida todas as informações necessárias para realizar uma demonstração ao-vivo bem-sucedida do sistema de reconhecimento automático de placas veiculares.

## Arquitetura do Sistema

O sistema SISCAV é composto por três componentes principais:

1. **Dispositivo IoT** (`apps/iot-device/`): 
   - Captura imagens da câmera
   - Detecta placas usando processamento de imagem (OpenCV)
   - Extrai texto usando OCR (EasyOCR)
   - Envia dados para a API central

2. **API Backend** (`apps/api/src/`):
   - Recebe logs de acesso dos dispositivos IoT
   - Valida placas contra whitelist
   - Armazena imagens e registros
   - Retorna status de autorização

3. **Banco de Dados PostgreSQL**:
   - Armazena whitelist de placas autorizadas
   - Registra todos os logs de acesso
   - Gerencia usuários e autenticação

## Fluxo de Funcionamento

```
[Câmera] → [Detecção de Placa] → [OCR] → [API] → [Validação Whitelist] → [Resposta]
                                                      ↓
                                              [Banco de Dados]
```

### Passo a Passo Detalhado

1. **Captura**: Câmera captura frame de vídeo
2. **Detecção**: Algoritmo detecta região candidata a placa
3. **OCR**: EasyOCR extrai texto da placa
4. **Validação Local**: Valida formato brasileiro (ABC1234 ou ABC1D23)
5. **Envio**: Envia placa + imagem para API via POST
6. **Validação API**: API normaliza placa e verifica whitelist
7. **Resposta**: API retorna status (Authorized/Denied)
8. **Feedback**: Sistema exibe resultado e toca som (se habilitado)

## Pré-requisitos para Demonstração

### Hardware

- **Computador com câmera integrada (laptop)**: A demonstração utilizará a câmera do próprio laptop
- Conexão de rede para comunicação com API
- Python 3.10, 3.11 ou 3.12 instalado

**Nota Importante**: A câmera utilizada será a câmera integrada do laptop onde a demonstração será realizada. Certifique-se de que:
- A câmera está funcionando
- As permissões de acesso à câmera estão habilitadas (Windows pode solicitar permissão)
- Não há outros aplicativos usando a câmera simultaneamente

### Software

#### Dispositivo IoT

- Python 3.10-3.12 (evitar 3.13+)
- Dependências: numpy, opencv-python, easyocr, requests

#### API Backend

- Python 3.10+
- PostgreSQL (local ou Supabase)
- Dependências: fastapi, sqlalchemy, pydantic, etc.

### Configuração Inicial

1. **API Backend deve estar rodando**:
   ```bash
   cd apps/api/src
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Banco de dados configurado**:
   - Migrações aplicadas
   - Whitelist com placas de teste cadastradas

3. **Dispositivo IoT configurado**:
   - Dependências instaladas
   - Câmera testada e funcionando
   - Variáveis de ambiente configuradas

## Guia Rápido de Execução

### 1. Preparar API Backend

```bash
# Terminal 1: Iniciar API
cd apps/api/src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verificar se está funcionando:
```bash
curl http://localhost:8000/api/v1/health
# Resposta esperada: {"status": "ok"}
```

### 2. Cadastrar Placas de Teste na Whitelist

```bash
# Criar usuário e obter token (se necessário)
# Depois cadastrar placas:
curl -X POST http://localhost:8000/api/v1/whitelist/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plate": "ABC1234", "description": "Veículo de teste"}'
```

### 3. Executar Dispositivo IoT

```bash
# Terminal 2: Executar dispositivo IoT
cd apps/iot-device

# Configurar variáveis (PowerShell)
$env:API_BASE_URL="http://localhost:8000/api/v1"
$env:CAMERA_ID=0
$env:ENABLE_DISPLAY="true"
$env:ENABLE_SOUND="true"
$env:LOG_LEVEL="INFO"

# Executar
python main.py
```

### 4. Demonstração

1. Posicionar placa na frente da câmera
2. Sistema detecta automaticamente
3. Janela mostra detecção em tempo real
4. Logs mostram processo completo
5. Som indica autorização/negação

## Configurações Recomendadas para Demonstração

### Variáveis de Ambiente (Dispositivo IoT)

```bash
# API
API_BASE_URL=http://localhost:8000/api/v1

# Câmera (câmera do laptop)
CAMERA_ID=0                    # ID da câmera do laptop (geralmente 0)
FRAME_WIDTH=1280
FRAME_HEIGHT=720

# OCR
GPU_ENABLED=false  # true se tiver GPU NVIDIA

# Detecção
PLATE_DETECTION_COOLDOWN=3.0  # Segundos entre detecções

# Aplicação
MAX_RUNTIME_SECONDS=0  # 0 = ilimitado
ENABLE_SOUND=true
ENABLE_DISPLAY=true
LOG_LEVEL=INFO
```

## Visualizando o Conteúdo Extraído da Placa

### Durante a Demonstração (Tempo Real)

O sistema exibe o conteúdo extraído da placa de três formas:

1. **Interface Visual (Janela de Vídeo)**:
   - Quando `ENABLE_DISPLAY=true`, uma janela mostra o vídeo em tempo real
   - A placa detectada é destacada com um retângulo colorido
   - O texto extraído aparece acima da placa: `PLACA: ABC1234`
   - O status de autorização aparece logo abaixo: `STATUS: Authorized/Denied`
   - Cores: Verde para autorizado, Vermelho para negado

2. **Logs no Console**:
   - O sistema imprime logs detalhados no formato:
   ```
   ============================================================
   EXTRACAO DE PLACA CONCLUIDA
     Conteudo extraido: ABC1234
     Tipo de placa: branca
     Tipo de veiculo: carro
     Coordenadas: x=100, y=200, w=150, h=50
   ============================================================
   RESULTADO DA VALIDACAO
     Placa extraida: ABC1234
     Status: Authorized
   ============================================================
   ```

3. **API Backend (Histórico)**:
   - Todos os logs são armazenados no banco de dados
   - O conteúdo extraído está disponível via API

### Consultar Logs via API

#### Listar Todos os Logs

```bash
# Obter token de autenticação primeiro
TOKEN=$(curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=senha" | jq -r '.access_token')

# Listar últimos 10 logs
curl -X GET "http://localhost:8000/api/v1/access_logs/?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### Filtrar por Placa

```bash
# Buscar logs de uma placa específica
curl -X GET "http://localhost:8000/api/v1/access_logs/?plate=ABC1234" \
  -H "Authorization: Bearer $TOKEN"
```

#### Filtrar por Status

```bash
# Apenas autorizados
curl -X GET "http://localhost:8000/api/v1/access_logs/?status=Authorized" \
  -H "Authorization: Bearer $TOKEN"

# Apenas negados
curl -X GET "http://localhost:8000/api/v1/access_logs/?status=Denied" \
  -H "Authorization: Bearer $TOKEN"
```

#### Resposta da API

A resposta inclui o conteúdo extraído da placa:

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T10:30:00Z",
    "plate_string_detected": "ABC1234",
    "status": "Authorized",
    "image_storage_key": "/uploads/abc123.jpg",
    "authorized_plate_id": "660e8400-e29b-41d4-a716-446655440000"
  }
]
```

**Campo Importante**: `plate_string_detected` contém o texto exato extraído pelo OCR.

### Visualizar Imagem da Placa

```bash
# Obter imagem de um log específico
curl -X GET "http://localhost:8000/api/v1/access_logs/images/{image_filename}" \
  -H "Authorization: Bearer $TOKEN" \
  --output plate_image.jpg
```

## Métricas e Análise

### O que Observar Durante a Demonstração

1. **Precisão de Detecção**: Quantas placas são detectadas corretamente
2. **Precisão de OCR**: Quantos caracteres são reconhecidos corretamente
   - **Verificar o campo `plate_string_detected` nos logs da API**
   - Comparar com a placa real para avaliar precisão
3. **Latência**: Tempo entre captura e resposta da API
4. **Taxa de Sucesso**: Porcentagem de requisições bem-sucedidas
5. **Conteúdo Extraído**: Verificar se o texto extraído corresponde à placa real

### Coletar Métricas

```bash
# Executar e salvar logs
python main.py > logs/demo_$(date +%Y%m%d_%H%M%S).log 2>&1

# Analisar métricas
python scripts/collect_metrics.py logs/demo_*.log

# Extrair apenas as placas detectadas dos logs
grep "Conteudo extraido:" logs/demo_*.log
```

## Troubleshooting Rápido

### Problema: Câmera não detectada

**Solução:**
- **Windows**: Verificar permissões em Configurações > Privacidade > Câmera
  - Habilitar "Permitir que aplicativos acessem sua câmera"
  - Habilitar "Permitir que aplicativos da área de trabalho acessem sua câmera"
- Verificar se nenhum outro aplicativo está usando a câmera (Teams, Zoom, etc.)
- Testar câmera com outro aplicativo (Câmera do Windows) para confirmar funcionamento
- Reiniciar o sistema se necessário
- Se houver múltiplas câmeras, testar diferentes IDs (0, 1, 2...)

### Problema: API não responde

**Solução:**
- Verificar se API está rodando: `curl http://localhost:8000/api/v1/health`
- Verificar URL configurada: `echo $API_BASE_URL`
- Verificar logs da API

### Problema: OCR lento ou impreciso

**Solução:**
- Habilitar GPU se disponível: `GPU_ENABLED=true`
- Reduzir resolução: `FRAME_WIDTH=640 FRAME_HEIGHT=480`
- Melhorar iluminação
- Ajustar posição da câmera

### Problema: Muitos falsos positivos

**Solução:**
- Ajustar parâmetros de detecção no `PlateDetector`
- Melhorar iluminação
- Ajustar posição e ângulo da câmera

## Checklist Pré-Demonstração

### Antes da Demonstração

- [ ] API backend rodando e acessível
- [ ] Banco de dados configurado e migrações aplicadas
- [ ] Whitelist com placas de teste cadastradas
- [ ] Dispositivo IoT com dependências instaladas
- [ ] Câmera testada e funcionando
- [ ] Variáveis de ambiente configuradas
- [ ] Teste rápido executado com sucesso
- [ ] Iluminação adequada no ambiente
- [ ] Placas de teste preparadas

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

## Decisões de Arquitetura

### Por que EasyOCR?

- **Precisão**: Baseado em Deep Learning, oferece alta precisão
- **Facilidade**: Instalação simples via pip
- **Robustez**: Funciona bem em condições variadas de iluminação
- **Manutenibilidade**: Código aberto e bem documentado

### Por que FastAPI?

- **Performance**: Alta performance para APIs assíncronas
- **Documentação**: Geração automática de documentação (Swagger)
- **Type Safety**: Validação automática com Pydantic
- **Modernidade**: Framework moderno e bem mantido

### Por que PostgreSQL?

- **Robustez**: SGBD relacional robusto e confiável
- **Extensibilidade**: Suporte a tipos avançados e extensões
- **Conformidade**: Conformidade estrita com padrões ACID
- **Escalabilidade**: Preparado para crescimento futuro

## Componentização e SOLID

### Princípios Aplicados

1. **Single Responsibility**: Cada serviço tem uma responsabilidade única
   - `CameraService`: Apenas captura de frames
   - `PlateDetector`: Apenas detecção de placas
   - `OCRService`: Apenas reconhecimento de texto
   - `APIClient`: Apenas comunicação com API

2. **Open/Closed**: Extensível sem modificar código existente
   - Detector de placas pode ser substituído
   - OCR pode ser trocado por outra biblioteca
   - API pode ser estendida com novos endpoints

3. **Dependency Inversion**: Dependências injetadas via construtor
   - Serviços recebem dependências como parâmetros
   - Facilita testes e manutenção

4. **DRY (Don't Repeat Yourself)**: Código reutilizável
   - Utilitários compartilhados (`plate_validator`, `normalize_plate`)
   - Configuração centralizada
   - Funções de validação reutilizadas

## Documentação Adicional

- **Guia Detalhado**: `docs/operacao/01-guia-demonstracao.md`
- **Troubleshooting**: `docs/operacao/03-troubleshooting-instalacao.md`
- **Documentação Técnica**: `docs/api/01-documentacao-tecnica.md`
- **Arquitetura IoT**: `docs/iot/01-refatoracao-dispositivo-iot.md`

## Suporte

Para problemas ou dúvidas:
1. Consultar logs com `LOG_LEVEL=DEBUG`
2. Verificar documentação técnica
3. Revisar seção de Troubleshooting
4. Consultar equipe de desenvolvimento

