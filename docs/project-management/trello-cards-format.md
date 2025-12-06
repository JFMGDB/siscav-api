# Cards do Trello - Formato para Cópia

## 📋 LISTA: ✅ CONCLUÍDAS

### ✅ RF-007: Autenticação de Administrador (Backend)
**Descrição:** Sistema de login seguro com JWT implementado
- ✅ Endpoint `/api/v1/login/access-token`
- ✅ Rate limiting (5/min)
- ✅ Hashing seguro de senhas
- ✅ Testes unitários
**Arquivos:** `apps/api/src/api/v1/endpoints/auth.py`

### ✅ RF-008: Gerenciamento da Lista de Acesso - CRUD (Backend)
**Descrição:** Endpoints CRUD completos para whitelist
- ✅ GET, POST, PUT, DELETE implementados
- ✅ Normalização automática de placas
- ✅ Proteção com JWT
- ✅ Testes unitários
**Arquivos:** `apps/api/src/api/v1/endpoints/whitelist.py`

### ✅ RF-004: Verificação na Lista de Acesso
**Descrição:** Lógica de validação de placas implementada
- ✅ Normalização para comparação
- ✅ Busca na whitelist
- ✅ Retorno de status Authorized/Denied
**Arquivos:** `apps/api/src/api/v1/endpoints/access_logs.py`

### ✅ RF-006: Registro de Eventos (Log)
**Descrição:** Sistema de logs de acesso completo
- ✅ Endpoint POST `/api/v1/access_logs/`
- ✅ Armazenamento de imagem, placa, status, timestamp
- ✅ Validação de arquivos
- ✅ Testes unitários
**Arquivos:** `apps/api/src/api/v1/endpoints/access_logs.py`

### ✅ RF-009: Visualização de Logs (Backend)
**Descrição:** Endpoint de consulta de logs com filtros
- ✅ GET `/api/v1/access_logs/` com paginação
- ✅ Filtros: placa, status, datas
- ✅ Endpoint para servir imagens
**Arquivos:** `apps/api/src/api/v1/endpoints/access_logs.py`

### ✅ RF-001: Captura de Imagem
**Descrição:** Serviço de captura de imagens da câmera
- ✅ CameraService implementado
- ✅ Suporte USB e Pi Camera
- ✅ Tratamento de erros
**Arquivos:** `apps/iot-device/services/camera.py`

### ✅ RF-002: Detecção e Localização da Placa
**Descrição:** Detecção de placas com OpenCV
- ✅ PlateDetector implementado
- ✅ Algoritmos de visão computacional
- ✅ Suporte carros e motos
- ✅ Evidências visuais disponíveis
**Arquivos:** `apps/iot-device/services/plate_detector.py`

### ✅ RF-003: Extração de Caracteres (OCR)
**Descrição:** OCR com EasyOCR implementado
- ✅ OCRService com EasyOCR
- ✅ Pré-processamento de imagens
- ✅ Suporte placas antigas e Mercosul
- ✅ Validação de formatos
- ✅ Evidências de resultados disponíveis
**Arquivos:** `apps/iot-device/services/ocr.py`

### ✅ RNF-008: Código Modular e Documentado
**Descrição:** Estrutura modular e documentação completa
- ✅ Separação de responsabilidades
- ✅ Documentação técnica em `docs/`
- ✅ Docstrings completas
- ✅ README detalhado
**Arquivos:** `docs/`, `README.md`

### ✅ CI/CD Pipeline
**Descrição:** Pipeline de integração contínua
- ✅ GitHub Actions configurado
- ✅ Linting com Ruff
- ✅ Testes com Pytest
**Arquivos:** `.github/workflows/ci.yml`

### ✅ Docker e Ambiente de Desenvolvimento
**Descrição:** Configuração Docker completa
- ✅ docker-compose.yml
- ✅ Suporte local e Supabase
- ✅ Scripts SQL para migração
**Arquivos:** `docker-compose.yml`, `Dockerfile.dev`

### ✅ Banco de Dados
**Descrição:** Modelos e migrações implementados
- ✅ Modelos SQLAlchemy (User, AuthorizedPlate, AccessLog)
- ✅ Migrações Alembic
- ✅ Scripts SQL para Supabase
**Arquivos:** `apps/api/src/api/v1/models/`

---

## 🚧 LISTA: EM ANDAMENTO

### 🚧 RF-010: Acionamento Manual Remoto (Integração IoT)
**Descrição:** Completar comunicação entre API e dispositivo IoT
- ✅ Endpoint backend implementado
- ⏳ Falta: Comunicação com dispositivo IoT
- ⏳ Falta: Integração com módulo relé
**Próximos Passos:**
1. Implementar endpoint no IoT para receber comandos
2. Configurar WebSocket/HTTP para comunicação
3. Integrar acionamento do relé físico
**Arquivos:** `apps/api/src/api/v1/endpoints/gate_control.py`

### 🚧 RF-005: Acionamento do Portão
**Descrição:** Integrar controle físico do portão via relé
- ✅ Cliente API implementado
- ✅ Envio de logs funcionando
- ⏳ Falta: Integração GPIO do Raspberry Pi
- ⏳ Falta: Controle do módulo relé
**Próximos Passos:**
1. Implementar controle GPIO
2. Integrar módulo relé 5V
3. Testar acionamento físico
**Arquivos:** `apps/iot-device/services/api_client.py`

### 🚧 RNF-001: Latência de Processamento (< 5s)
**Descrição:** Otimizar para atingir latência < 5 segundos
- ✅ Sistema funcional
- ⏳ Falta: Medição de latência atual
- ⏳ Falta: Otimizações necessárias
**Próximos Passos:**
1. Medir latência end-to-end atual
2. Otimizar processamento de imagens
3. Implementar cache de whitelist (se necessário)
**Arquivos:** `apps/iot-device/main.py`

---

## ⏳ LISTA: PENDENTES

### ⏳ RF-007: Autenticação de Administrador (Frontend)
**Descrição:** Implementar interface de login no frontend
**Tarefas:**
- [ ] Criar página de login (`(public)/login/page.tsx`)
- [ ] Formulário de login com validação
- [ ] Integração com endpoint `/api/v1/login/access-token`
- [ ] Armazenar JWT em cookie httpOnly
- [ ] Layout protegido (`(auth)/layout.tsx`)
- [ ] Botão "Sair"
**Repositório:** siscav-web (separado)
**Prioridade:** Alta

### ⏳ RF-008: Gerenciamento da Lista de Acesso (Frontend)
**Descrição:** Interface CRUD completa no frontend
**Tarefas:**
- [ ] Página de whitelist (`(auth)/whitelist/page.tsx`)
- [ ] Tabela de dados (MUI DataGrid)
- [ ] Modal para criar nova placa
- [ ] Funcionalidade de edição
- [ ] Diálogo de confirmação para deletar
- [ ] Integração com API
**Repositório:** siscav-web (separado)
**Prioridade:** Alta

### ⏳ RF-009: Visualização de Logs de Acesso (Frontend)
**Descrição:** Interface de visualização de logs
**Tarefas:**
- [ ] Página de logs (`(auth)/logs/page.tsx`)
- [ ] Tabela com paginação
- [ ] Filtros: placa, status, datas
- [ ] Visualização de imagens
- [ ] Integração com API
**Repositório:** siscav-web (separado)
**Prioridade:** Alta

### ⏳ RF-010: Acionamento Manual Remoto (Frontend)
**Descrição:** Botão de acionamento remoto no painel
**Tarefas:**
- [ ] Adicionar botão no dashboard
- [ ] Integrar com `POST /api/v1/gate/trigger`
- [ ] Feedback visual de sucesso/erro
**Repositório:** siscav-web (separado)
**Prioridade:** Média

### ⏳ RNF-002: Precisão do ALPR
**Descrição:** Validar precisão de 95% diurno e 85% noturno
**Tarefas:**
- [ ] Testes em condições reais
- [ ] Coletar métricas de precisão
- [ ] Ajustar algoritmos se necessário
- [ ] Documentar resultados
**Prioridade:** Média

### ⏳ RNF-003: Disponibilidade do Sistema (99.5%)
**Descrição:** Implementar watchdog e reinicialização automática
**Tarefas:**
- [ ] Configurar serviço systemd no Raspberry Pi
- [ ] Implementar watchdog
- [ ] Configurar monitoramento de saúde da API
- [ ] Testar recuperação de falhas
**Prioridade:** Alta

### ⏳ RNF-004: Operação Offline (Contingência)
**Descrição:** Cache local da whitelist no dispositivo IoT
**Tarefas:**
- [ ] Sincronização periódica da whitelist
- [ ] Armazenar cache local (SQLite/JSON)
- [ ] Modificar lógica para usar cache quando offline
- [ ] Testar cenário de perda de conectividade
**Prioridade:** Baixa

### ⏳ RNF-005: Comunicação Criptografada (TLS)
**Descrição:** Configurar HTTPS em produção
**Tarefas:**
- [ ] Configurar certificado SSL/TLS
- [ ] Configurar reverse proxy (Nginx/Traefik)
- [ ] Validar comunicação HTTPS do IoT
- [ ] Documentar configuração
**Prioridade:** Alta (para produção)

### ⏳ RNF-006: Segurança do Painel (OWASP Top 10)
**Descrição:** Revisar e validar proteções de segurança
**Tarefas:**
- [ ] Revisar código para SQL Injection
- [ ] Implementar proteção CSRF no frontend
- [ ] Validar sanitização de inputs
- [ ] Revisar headers de segurança HTTP
- [ ] Executar scan de vulnerabilidades
**Prioridade:** Alta

### ⏳ RNF-007: Interface Intuitiva
**Descrição:** Desenvolver UI/UX do painel
**Tarefas:**
- [ ] Design de interface com MUI
- [ ] Implementar responsividade
- [ ] Testes de usabilidade
- [ ] Documentação de uso
**Repositório:** siscav-web (separado)
**Prioridade:** Alta

---

## 🔒 LISTA: BLOQUEADAS

### 🔒 RF-005: Acionamento do Portão (Hardware)
**Descrição:** Integração física com módulo relé
**Bloqueio:** Aguardando montagem de hardware pelo cliente
**Observação:** Cliente responsável pela montagem (conforme especificação)
**Próximos Passos (após hardware):**
1. Integrar código GPIO
2. Testar acionamento do relé
3. Validar com portão real

### 🔒 Compatibilidade com Câmera Hikvision
**Descrição:** Verificar compatibilidade da câmera fornecida
**Bloqueio:** Depende de análise técnica da câmera específica
**Próximos Passos:**
1. Analisar especificações
2. Testar integração com OpenCV
3. Validar qualidade para ALPR

---

## 📊 Resumo por Status

- ✅ **Concluídas:** 12 tarefas
- 🚧 **Em Andamento:** 3 tarefas
- ⏳ **Pendentes:** 10 tarefas
- 🔒 **Bloqueadas:** 2 tarefas

**Total:** 27 tarefas mapeadas

---

## 🎯 Priorização Sugerida para Próxima Sprint

### Alta Prioridade
1. Finalizar integração GPIO (RF-005)
2. Iniciar desenvolvimento do frontend (RF-007, RF-008, RF-009)
3. Implementar watchdog (RNF-003)
4. Revisão de segurança (RNF-006)

### Média Prioridade
1. Otimizar latência (RNF-001)
2. Testes de precisão (RNF-002)
3. Acionamento remoto frontend (RF-010)

### Baixa Prioridade
1. Operação offline (RNF-004)
2. Configuração TLS (RNF-005) - necessário apenas para produção

---

**Nota:** Este documento pode ser usado para criar cards diretamente no Trello. Cada seção corresponde a uma lista no Trello.

