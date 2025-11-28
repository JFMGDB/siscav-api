# Estado Atual do Projeto e Decisões Técnicas

## Data: 2025-01-XX

## Resumo Executivo

O sistema SISCAV (Sistema de Controle de Acesso Veicular) está funcional e pronto para demonstração ao-vivo. O sistema integra dispositivos IoT com uma API central para reconhecimento automático de placas veiculares e controle de acesso.

## Estado Atual do Sistema

### Componentes Implementados

#### 1. Dispositivo IoT (`apps/iot-device/`)

**Status**: ✅ Funcional e testado

**Funcionalidades Implementadas**:
- Captura de imagens via câmera (OpenCV)
- Detecção de placas usando processamento de imagem
- Reconhecimento de texto usando EasyOCR
- Validação de formato brasileiro (antigo e Mercosul)
- Sistema de debounce para evitar detecções duplicadas
- Comunicação com API via HTTP
- Feedback visual e sonoro

**Arquitetura**:
- **CameraService**: Responsável apenas pela captura de frames
- **PlateDetector**: Detecta regiões candidatas a placas usando OpenCV
- **OCRService**: Extrai texto usando EasyOCR com pré-processamento
- **APIClient**: Gerencia comunicação HTTP com a API
- **PlateDebouncer**: Evita processamento duplicado da mesma placa

**Tecnologias**:
- Python 3.10-3.12
- OpenCV 4.8+ (processamento de imagem)
- EasyOCR 1.7+ (OCR baseado em Deep Learning)
- NumPy 1.24+ (processamento numérico)
- Requests (comunicação HTTP)

#### 2. API Backend (`apps/api/src/`)

**Status**: ✅ Funcional e testado

**Funcionalidades Implementadas**:
- Autenticação JWT para administradores
- CRUD completo de whitelist de placas
- Recebimento e processamento de logs de acesso
- Validação de placas contra whitelist
- Armazenamento de imagens
- Endpoints de consulta de logs
- Controle remoto do portão (estrutura pronta)

**Arquitetura**:
- **FastAPI**: Framework web assíncrono
- **SQLAlchemy**: ORM para acesso ao banco
- **Pydantic**: Validação de dados
- **Alembic**: Migrações de banco de dados
- **PostgreSQL**: Banco de dados relacional

**Endpoints Principais**:
- `POST /api/v1/access_logs/`: Recebe logs dos dispositivos IoT
- `GET /api/v1/access_logs/`: Lista logs de acesso
- `GET /api/v1/whitelist/`: Lista placas autorizadas
- `POST /api/v1/whitelist/`: Adiciona placa à whitelist
- `POST /api/v1/gate_control/trigger`: Aciona portão remotamente

#### 3. Banco de Dados

**Status**: ✅ Schema implementado e migrações prontas

**Tabelas**:
- `users`: Usuários administradores
- `authorized_plates`: Whitelist de placas autorizadas
- `access_logs`: Registros de todas as tentativas de acesso

**Características**:
- Suporte a PostgreSQL (local ou Supabase)
- Fallback para SQLite em desenvolvimento
- Migrações automáticas via Alembic

## Decisões Técnicas e Justificativas

### 1. Escolha do EasyOCR para OCR

**Decisão**: Utilizar EasyOCR em vez de Tesseract ou OpenALPR

**Justificativa**:
- **Precisão Superior**: Baseado em Deep Learning (CNN/RNN), oferece precisão significativamente maior que Tesseract em condições reais
- **Facilidade de Instalação**: Instalação simples via `pip install easyocr`, sem necessidade de compilação
- **Robustez**: Funciona bem em condições variadas de iluminação e ângulos
- **Manutenibilidade**: Biblioteca bem mantida e documentada, facilitando suporte futuro

**Alternativas Consideradas**:
- **Tesseract**: Precisão baixa em imagens do mundo real, requer pipeline complexo de pré-processamento
- **OpenALPR**: Alta precisão, mas instalação complexa (requer compilação de dependências C++)

### 2. Arquitetura de Detecção de Placas

**Decisão**: Implementar detecção baseada em processamento de imagem clássico (OpenCV) em vez de modelos de Deep Learning

**Justificativa**:
- **Performance**: Processamento mais rápido, adequado para execução em tempo real
- **Recursos**: Não requer GPU, funciona em hardware mais simples
- **Controle**: Permite ajuste fino de parâmetros para diferentes condições
- **Simplicidade**: Implementação mais simples e manutenível

**Processo de Detecção**:
1. Conversão para escala de cinza
2. Equalização de histograma
3. Filtro bilateral para redução de ruído
4. Detecção de bordas (Canny)
5. Operações morfológicas
6. Análise de contornos
7. Filtragem por tamanho, razão de aspecto e área

### 3. Sistema de Debounce

**Decisão**: Implementar sistema de debounce para evitar processamento duplicado

**Justificativa**:
- **Eficiência**: Evita requisições desnecessárias à API
- **Precisão**: Reduz falsos positivos de detecções repetidas
- **Performance**: Melhora latência geral do sistema

**Implementação**:
- Cooldown configurável (padrão: 3 segundos)
- Histórico de placas detectadas recentemente
- Limpeza automática de entradas antigas

### 4. Normalização de Placas

**Decisão**: Normalizar placas removendo caracteres especiais antes da comparação

**Justificativa**:
- **Robustez**: Aceita placas em diferentes formatos (com/sem hífen, espaços)
- **Consistência**: Garante comparação correta mesmo com variações de OCR
- **Flexibilidade**: Suporta formatos antigo (ABC1234) e Mercosul (ABC1D23)

**Implementação**:
- Função `normalize_plate()` remove caracteres não alfanuméricos
- Conversão para maiúsculas
- Validação de formato brasileiro

### 5. Arquitetura de Componentização

**Decisão**: Separar responsabilidades em serviços independentes

**Justificativa**:
- **SOLID**: Segue princípio de Responsabilidade Única
- **Testabilidade**: Facilita testes unitários
- **Manutenibilidade**: Código mais fácil de entender e modificar
- **Extensibilidade**: Permite substituir componentes sem afetar outros

**Componentes**:
- `CameraService`: Apenas captura de frames
- `PlateDetector`: Apenas detecção de placas
- `OCRService`: Apenas reconhecimento de texto
- `APIClient`: Apenas comunicação HTTP
- `PlateDebouncer`: Apenas controle de debounce

### 6. Armazenamento de Imagens

**Decisão**: Armazenar imagens em sistema de arquivos local (não em banco de dados)

**Justificativa**:
- **Performance**: Evita sobrecarga no banco de dados
- **Simplicidade**: Implementação mais simples
- **Escalabilidade**: Facilita migração futura para storage distribuído (S3, etc.)

**Implementação**:
- Diretório configurável via `UPLOAD_DIR`
- Nomes de arquivo únicos (UUID)
- Validação de tipo e tamanho de arquivo

## Fluxo de Dados

### Fluxo Completo de Detecção

```
1. Câmera captura frame
   ↓
2. PlateDetector detecta região candidata
   ↓
3. OCRService extrai texto da região
   ↓
4. Validação de formato brasileiro
   ↓
5. Verificação de debounce
   ↓
6. APIClient envia para API (placa + imagem)
   ↓
7. API normaliza placa
   ↓
8. API verifica whitelist
   ↓
9. API armazena log e imagem
   ↓
10. API retorna status (Authorized/Denied)
   ↓
11. Dispositivo IoT exibe resultado e toca som
```

## Métricas e Performance

### Métricas Esperadas

- **Precisão de Detecção**: > 90% em condições ideais
- **Precisão de OCR**: > 95% em condições diurnas
- **Latência Total**: < 5 segundos (captura → resposta API)
- **Taxa de Processamento**: 10-30 FPS (dependendo do hardware)

### Fatores que Afetam Performance

- **Hardware**: CPU, GPU (se habilitada), RAM
- **Resolução**: Resoluções maiores = processamento mais lento
- **Iluminação**: Condições ideais melhoram precisão
- **Rede**: Latência de comunicação com API

## Preparação para Demonstração

### Checklist de Verificação

1. ✅ API backend rodando e acessível
2. ✅ Banco de dados configurado
3. ✅ Whitelist com placas de teste
4. ✅ Dispositivo IoT com dependências instaladas
5. ✅ Câmera testada e funcionando
6. ✅ Script de verificação criado
7. ✅ Documentação completa disponível

### Scripts de Apoio

- `verify_demo_setup.py`: Verifica pré-requisitos antes da demonstração
- `collect_metrics.py`: Coleta e analisa métricas dos logs

## Próximos Passos (Futuro)

### Melhorias Planejadas

1. **Modelo de Deep Learning para Detecção**:
   - Substituir detecção clássica por modelo treinado
   - Melhorar precisão em condições adversas

2. **Operação Offline**:
   - Cache local da whitelist no dispositivo
   - Sincronização periódica com servidor

3. **Múltiplos Dispositivos**:
   - Gerenciamento centralizado de dispositivos
   - Monitoramento de status

4. **Dashboard Web**:
   - Interface administrativa completa
   - Visualização de logs e estatísticas

5. **Acionamento Físico do Portão**:
   - Integração com módulo relé
   - Comunicação bidirecional com dispositivos IoT

## Documentação Criada

### Documentos Principais

1. **DEMONSTRACAO_COMPLETA.md**: Guia completo de demonstração
2. **GUIA_RAPIDO_DEMONSTRACAO.md**: Guia rápido para execução
3. **ESTADO_ATUAL_E_DECISOES.md**: Este documento

### Documentos de Apoio

- `docs/operacao/01-guia-demonstracao.md`: Guia detalhado de demonstração
- `docs/iot/01-refatoracao-dispositivo-iot.md`: Documentação técnica do IoT
- `docs/api/01-documentacao-tecnica.md`: Documentação técnica da API

## Conclusão

O sistema SISCAV está funcional e pronto para demonstração. Todas as funcionalidades principais foram implementadas seguindo princípios SOLID e DRY, com código bem documentado e modular. O sistema pode ser demonstrado ao-vivo com confiança, mostrando o reconhecimento automático de placas e a integração completa entre dispositivo IoT e API central.

