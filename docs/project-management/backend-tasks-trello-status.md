# Status das Tarefas do Projeto SISCAV

**Data de Análise:** 06 de dezembro de 2025  
**Repositório:** siscav-api

---

## 📋 Resumo Executivo

Este documento mapeia o status de implementação dos requisitos funcionais (RF) e não funcionais (RNF) do Sistema de Controle de Acesso de Veículos (SISCAV), baseado na análise do codebase atual.

### Status Geral
- ✅ **Concluídas:** 8 tarefas principais
- 🚧 **Em Andamento:** 3 tarefas
- ⏳ **Pendentes:** 5 tarefas principais
- 🔒 **Bloqueadas/Aguardando:** 2 tarefas

---

## ✅ TAREFAS CONCLUÍDAS

### Backend - API Central

#### ✅ RF-007: Autenticação de Administrador
- **Status:** ✅ Concluído
- **Evidências:**
  - Endpoint `/api/v1/login/access-token` implementado (`apps/api/src/api/v1/endpoints/auth.py`)
  - Sistema JWT com tokens de acesso
  - Rate limiting (5 tentativas/minuto) para prevenir força bruta
  - Modelo `User` com hashing seguro de senhas (passlib)
  - CRUD de usuários implementado (`crud_user.py`)
  - Testes unitários: `test_auth_whitelist.py`
- **Arquivos:**
  - `apps/api/src/api/v1/endpoints/auth.py`
  - `apps/api/src/api/v1/models/user.py`
  - `apps/api/src/api/v1/crud/crud_user.py`
  - `apps/api/src/api/v1/core/security.py`

#### ✅ RF-008: Gerenciamento da Lista de Acesso (CRUD)
- **Status:** ✅ Concluído
- **Evidências:**
  - Endpoints CRUD completos para whitelist (`/api/v1/whitelist/`)
    - GET `/` - Listar placas (com paginação)
    - POST `/` - Criar nova placa
    - GET `/{id}` - Obter placa por ID
    - PUT `/{id}` - Atualizar placa
    - DELETE `/{id}` - Remover placa
  - Normalização automática de placas (suporta formatos antigo e Mercosul)
  - Modelo `AuthorizedPlate` com campos `plate`, `normalized_plate`, `description`
  - Proteção com autenticação JWT em todos os endpoints
  - Testes unitários completos: `test_auth_whitelist.py`
- **Arquivos:**
  - `apps/api/src/api/v1/endpoints/whitelist.py`
  - `apps/api/src/api/v1/models/authorized_plate.py`
  - `apps/api/src/api/v1/crud/crud_authorized_plate.py`

#### ✅ RF-004: Verificação na Lista de Acesso
- **Status:** ✅ Concluído
- **Evidências:**
  - Lógica de verificação implementada no endpoint de access logs
  - Normalização de placas para comparação (ignora maiúsculas/minúsculas, hífens, espaços)
  - Busca por `normalized_plate` na whitelist
  - Retorno de status `Authorized` ou `Denied`
- **Arquivos:**
  - `apps/api/src/api/v1/endpoints/access_logs.py` (linhas 84-92)
  - `apps/api/src/api/v1/utils/plate.py` (normalização)

#### ✅ RF-006: Registro de Eventos (Log)
- **Status:** ✅ Concluído
- **Evidências:**
  - Endpoint `POST /api/v1/access_logs/` para registro de tentativas de acesso
  - Armazenamento de:
    - Placa detectada (`plate_string_detected`)
    - Status (`Authorized`/`Denied`)
    - Imagem capturada (salva em `uploads/`)
    - Timestamp automático
    - Referência à placa autorizada (se aplicável)
  - Modelo `AccessLog` com ENUM `AccessStatus`
  - Validação de arquivos (tipo MIME, tamanho máximo 10MB)
  - Testes unitários: `test_access_logs.py`
- **Arquivos:**
  - `apps/api/src/api/v1/endpoints/access_logs.py`
  - `apps/api/src/api/v1/models/access_log.py`
  - `apps/api/src/api/v1/crud/crud_access_log.py`

#### ✅ RF-009: Visualização de Logs de Acesso (Backend)
- **Status:** ✅ Concluído (Backend)
- **Evidências:**
  - Endpoint `GET /api/v1/access_logs/` com filtros:
    - Paginação (`skip`, `limit`)
    - Filtro por placa (busca parcial)
    - Filtro por status (`Authorized`/`Denied`)
    - Filtro por intervalo de datas (`start_date`, `end_date`)
  - Endpoint `GET /api/v1/access_logs/images/{filename}` para servir imagens
  - Proteção com autenticação JWT
- **Arquivos:**
  - `apps/api/src/api/v1/endpoints/access_logs.py` (linhas 175-220)

#### ✅ RF-010: Acionamento Manual Remoto (Backend)
- **Status:** ✅ Parcialmente Concluído (Backend implementado, integração IoT pendente)
- **Evidências:**
  - Endpoint `POST /api/v1/gate/trigger` implementado
  - Proteção com autenticação JWT
  - TODO: Comunicação com dispositivo IoT para acionar relé físico
- **Arquivos:**
  - `apps/api/src/api/v1/endpoints/gate_control.py`

### Dispositivo IoT

#### ✅ RF-001: Captura de Imagem
- **Status:** ✅ Concluído
- **Evidências:**
  - Serviço `CameraService` implementado
  - Suporte a câmeras USB e Pi Camera
  - Captura de frames contínuos
  - Tratamento de erros e fallback
- **Arquivos:**
  - `apps/iot-device/services/camera.py`
  - `apps/iot-device/main.py` (linhas 254-258)

#### ✅ RF-002: Detecção e Localização da Placa
- **Status:** ✅ Concluído
- **Evidências:**
  - Serviço `PlateDetector` implementado com OpenCV
  - Algoritmos de detecção de bordas (Canny)
  - Operações morfológicas para isolamento de placas
  - Análise de contornos para localização retangular
  - Suporte a placas de carros e motos
  - Evidências visuais: `docs/assets/evidencia-deteccao-placas-e-delimitacao-das-bordas.png`
- **Arquivos:**
  - `apps/iot-device/services/plate_detector.py`
  - `apps/iot-device/main.py` (linhas 264-271)

#### ✅ RF-003: Extração de Caracteres (OCR)
- **Status:** ✅ Concluído
- **Evidências:**
  - Serviço `OCRService` implementado com EasyOCR
  - Pré-processamento de imagens (escala de cinza, threshold, redimensionamento)
  - Suporte a placas antigas (ABC1234) e Mercosul (ABC1D23)
  - Validação de formato de placas brasileiras
  - Evidências de resultados: `docs/assets/evidencias-resultados-ocr.png`
- **Arquivos:**
  - `apps/iot-device/services/ocr.py`
  - `apps/iot-device/utils/plate_validator.py`
  - `apps/iot-device/main.py` (linhas 172-194)

### Infraestrutura e DevOps

#### ✅ RNF-008: Código Modular e Documentado
- **Status:** ✅ Concluído
- **Evidências:**
  - Estrutura modular bem organizada (separação de responsabilidades)
  - Documentação técnica completa em `docs/`
  - Docstrings em todos os endpoints
  - README detalhado com guias de instalação
  - Documentação de arquitetura e backlog
- **Arquivos:**
  - `README.md`
  - `docs/architecture/`
  - `docs/requirements/`
  - `docs/iot/`

#### ✅ CI/CD Pipeline
- **Status:** ✅ Concluído
- **Evidências:**
  - GitHub Actions configurado (`.github/workflows/ci.yml`)
  - Linting automatizado com Ruff
  - Testes automatizados com Pytest
  - Suporte a Python 3.13
- **Arquivos:**
  - `.github/workflows/ci.yml`

#### ✅ Docker e Ambiente de Desenvolvimento
- **Status:** ✅ Concluído
- **Evidências:**
  - `docker-compose.yml` configurado
  - Suporte a ambientes local (PostgreSQL) e Supabase
  - `Dockerfile.dev` para desenvolvimento
  - Scripts SQL para migração manual no Supabase
- **Arquivos:**
  - `docker-compose.yml`
  - `Dockerfile.dev`
  - `db/sql/supabase/`

#### ✅ Banco de Dados
- **Status:** ✅ Concluído
- **Evidências:**
  - Modelos SQLAlchemy implementados (User, AuthorizedPlate, AccessLog)
  - Migrações Alembic configuradas
  - Scripts SQL para Supabase
  - Suporte a PostgreSQL com tipos UUID, ENUM, TIMESTAMPTZ
- **Arquivos:**
  - `apps/api/src/api/v1/models/`
  - `apps/api/src/alembic/versions/20251102_0001_initial_models.py`
  - `db/sql/supabase/`

---

## 🚧 TAREFAS EM ANDAMENTO

### Backend - API Central

#### 🚧 RF-010: Acionamento Manual Remoto (Integração IoT)
- **Status:** 🚧 Em Andamento
- **Progresso:** Backend implementado, falta comunicação com dispositivo IoT
- **Próximos Passos:**
  - Implementar endpoint no dispositivo IoT para receber comandos
  - Implementar comunicação WebSocket/HTTP entre API e IoT
  - Integrar acionamento do módulo relé físico
- **Arquivos:**
  - `apps/api/src/api/v1/endpoints/gate_control.py` (linha 39: TODO)

### Dispositivo IoT

#### 🚧 RF-005: Acionamento do Portão
- **Status:** 🚧 Em Andamento
- **Progresso:** Lógica de comunicação com API implementada, falta integração física
- **Evidências:**
  - Cliente API implementado (`api_client.py`)
  - Envio de logs de acesso funcionando
  - Falta: Integração com módulo relé GPIO
- **Próximos Passos:**
  - Implementar controle GPIO do Raspberry Pi
  - Integrar módulo relé de 5V
  - Testar acionamento físico do portão
- **Arquivos:**
  - `apps/iot-device/services/api_client.py`
  - `apps/iot-device/main.py`

#### 🚧 RNF-001: Latência de Processamento
- **Status:** 🚧 Em Andamento (Otimização)
- **Progresso:** Sistema funcional, mas precisa de otimização para atingir < 5 segundos
- **Próximos Passos:**
  - Medir latência atual end-to-end
  - Otimizar processamento de imagens
  - Implementar cache de whitelist local (se necessário)
  - Otimizar comunicação com API

---

## ⏳ TAREFAS PENDENTES

### Frontend - Painel de Administração

#### ⏳ RF-007: Autenticação de Administrador (Frontend)
- **Status:** ⏳ Pendente
- **Descrição:** Implementar interface de login no frontend
- **Tarefas:**
  - Criar página de login (`(public)/login/page.tsx`)
  - Implementar formulário de login com validação
  - Integrar com endpoint `/api/v1/login/access-token`
  - Armazenar JWT de forma segura (cookie httpOnly)
  - Implementar layout protegido (`(auth)/layout.tsx`)
  - Implementar botão "Sair"
- **Repositório:** siscav-web (separado)

#### ⏳ RF-008: Gerenciamento da Lista de Acesso - Frontend
- **Status:** ⏳ Pendente
- **Descrição:** Implementar interface CRUD completa no frontend
- **Tarefas:**
  - Criar página de whitelist (`(auth)/whitelist/page.tsx`)
  - Implementar tabela de dados (MUI DataGrid)
  - Modal/formulário para criar nova placa
  - Funcionalidade de edição inline ou modal
  - Diálogo de confirmação para deletar
  - Integração com endpoints da API
- **Repositório:** siscav-web (separado)

#### ⏳ RF-009: Visualização de Logs de Acesso (Frontend)
- **Status:** ⏳ Pendente
- **Descrição:** Implementar interface de visualização de logs no frontend
- **Tarefas:**
  - Criar página de logs (`(auth)/logs/page.tsx`)
  - Implementar tabela de logs com paginação
  - Filtros: placa, status, intervalo de datas
  - Visualização de imagens capturadas
  - Integração com endpoint `GET /api/v1/access_logs/`
- **Repositório:** siscav-web (separado)

#### ⏳ RF-010: Acionamento Manual Remoto (Frontend)
- **Status:** ⏳ Pendente
- **Descrição:** Implementar botão de acionamento remoto no painel
- **Tarefas:**
  - Adicionar botão no dashboard
  - Integrar com endpoint `POST /api/v1/gate/trigger`
  - Feedback visual de sucesso/erro
- **Repositório:** siscav-web (separado)

### Requisitos Não Funcionais

#### ⏳ RNF-002: Precisão do ALPR
- **Status:** ⏳ Pendente (Testes em Produção)
- **Descrição:** Validar precisão de 95% diurno e 85% noturno
- **Tarefas:**
  - Executar testes em condições reais
  - Coletar métricas de precisão
  - Ajustar algoritmos se necessário
  - Documentar resultados

#### ⏳ RNF-003: Disponibilidade do Sistema
- **Status:** ⏳ Pendente
- **Descrição:** Implementar mecanismo de watchdog/reinicialização automática
- **Tarefas:**
  - Configurar serviço systemd no Raspberry Pi
  - Implementar watchdog para reinicialização automática
  - Configurar monitoramento de saúde da API
  - Testar recuperação de falhas

#### ⏳ RNF-004: Operação Offline (Contingência)
- **Status:** ⏳ Pendente
- **Descrição:** Implementar cache local da whitelist no dispositivo IoT
- **Tarefas:**
  - Implementar sincronização periódica da whitelist
  - Armazenar cache local (SQLite ou arquivo JSON)
  - Modificar lógica de validação para usar cache quando offline
  - Testar cenário de perda de conectividade

#### ⏳ RNF-005: Comunicação Criptografada (TLS)
- **Status:** ⏳ Pendente (Configuração de Produção)
- **Descrição:** Garantir HTTPS em produção
- **Tarefas:**
  - Configurar certificado SSL/TLS
  - Configurar reverse proxy (Nginx/Traefik)
  - Validar comunicação HTTPS do dispositivo IoT
  - Documentar configuração

#### ⏳ RNF-006: Segurança do Painel de Administração
- **Status:** ⏳ Pendente (Revisão de Segurança)
- **Descrição:** Revisar e validar proteções contra OWASP Top 10
- **Tarefas:**
  - Revisar código para SQL Injection (usar ORM protege, mas validar)
  - Implementar proteção CSRF no frontend
  - Validar sanitização de inputs
  - Revisar headers de segurança HTTP
  - Executar scan de vulnerabilidades

#### ⏳ RNF-007: Interface Intuitiva
- **Status:** ⏳ Pendente
- **Descrição:** Desenvolver UI/UX do painel de administração
- **Tarefas:**
  - Design de interface com MUI
  - Implementar responsividade
  - Testes de usabilidade
  - Documentação de uso para administradores
- **Repositório:** siscav-web (separado)

---

## 🔒 TAREFAS BLOQUEADAS/AGUARDANDO

### Hardware e Infraestrutura

#### 🔒 RF-005: Acionamento do Portão (Hardware)
- **Status:** 🔒 Bloqueado - Aguardando Hardware
- **Descrição:** Integração física com módulo relé depende de hardware
- **Bloqueio:** Cliente responsável pela montagem dos componentes de hardware (conforme especificação)
- **Próximos Passos (após hardware):**
  - Integrar código GPIO no dispositivo IoT
  - Testar acionamento do relé
  - Validar funcionamento com portão real

#### 🔒 Compatibilidade com Câmera Hikvision
- **Status:** 🔒 Bloqueado - Aguardando Análise
- **Descrição:** Verificar compatibilidade da câmera Hikvision fornecida pelo cliente
- **Bloqueio:** Depende de análise técnica da câmera específica
- **Próximos Passos:**
  - Analisar especificações da câmera
  - Testar integração com OpenCV
  - Validar qualidade de imagem para ALPR

---

## 📊 Mapeamento RF/RNF vs Status

### Requisitos Funcionais (RF)

| RF | Descrição | Status | Observações |
|---|---|---|---|
| RF-001 | Captura de Imagem | ✅ Concluído | CameraService implementado |
| RF-002 | Detecção e Localização da Placa | ✅ Concluído | PlateDetector com OpenCV |
| RF-003 | Extração de Caracteres (OCR) | ✅ Concluído | EasyOCR implementado |
| RF-004 | Verificação na Lista de Acesso | ✅ Concluído | Backend completo |
| RF-005 | Acionamento do Portão | 🚧 Em Andamento | Falta integração GPIO |
| RF-006 | Registro de Eventos (Log) | ✅ Concluído | Backend completo |
| RF-007 | Autenticação de Administrador | ✅ Backend / ⏳ Frontend | Backend completo, frontend pendente |
| RF-008 | Gerenciamento da Lista (CRUD) | ✅ Backend / ⏳ Frontend | Backend completo, frontend pendente |
| RF-009 | Visualização de Logs | ✅ Backend / ⏳ Frontend | Backend completo, frontend pendente |
| RF-010 | Acionamento Manual Remoto | 🚧 Backend / ⏳ Frontend | Backend parcial, frontend pendente |

### Requisitos Não Funcionais (RNF)

| RNF | Descrição | Status | Observações |
|---|---|---|---|
| RNF-001 | Latência de Processamento (< 5s) | 🚧 Em Andamento | Otimização necessária |
| RNF-002 | Precisão do ALPR (95% diurno, 85% noturno) | ⏳ Pendente | Testes em produção necessários |
| RNF-003 | Disponibilidade (99.5%) | ⏳ Pendente | Watchdog pendente |
| RNF-004 | Operação Offline (Contingência) | ⏳ Pendente | Cache local pendente |
| RNF-005 | Comunicação Criptografada (TLS) | ⏳ Pendente | Configuração de produção |
| RNF-006 | Segurança do Painel (OWASP Top 10) | ⏳ Pendente | Revisão de segurança |
| RNF-007 | Interface Intuitiva | ⏳ Pendente | Frontend pendente |
| RNF-008 | Código Modular e Documentado | ✅ Concluído | Documentação completa |

---

## 📝 Observações Importantes

1. **Frontend Separado:** O frontend está planejado para um repositório separado (`siscav-web`), então todas as tarefas de UI estão pendentes até que esse repositório seja criado e desenvolvido.

2. **Hardware:** A integração física com o módulo relé e a câmera Hikvision depende do cliente, conforme especificado no documento de requisitos.

3. **Testes em Produção:** Alguns requisitos (RNF-002, RNF-001) precisam ser validados em ambiente real de produção.

4. **Priorização Sugerida:**
   - Finalizar integração GPIO para RF-005
   - Desenvolver frontend básico (RF-007, RF-008, RF-009)
   - Implementar watchdog (RNF-003)
   - Otimizar latência (RNF-001)

---

## 🔄 Próximas Ações Recomendadas

1. **Sprint Atual:**
   - Finalizar integração GPIO no dispositivo IoT
   - Iniciar desenvolvimento do frontend (repositório siscav-web)

2. **Sprint Seguinte:**
   - Completar painel de administração (RF-007, RF-008, RF-009)
   - Implementar watchdog e monitoramento (RNF-003)

3. **Futuro:**
   - Testes de precisão em produção (RNF-002)
   - Implementar operação offline (RNF-004)
   - Configurar TLS em produção (RNF-005)

---

**Última Atualização:** 06 de dezembro de 2025  
**Próxima Revisão:** A definir pela equipe

