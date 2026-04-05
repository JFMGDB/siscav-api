# Cliente de borda (IoT / ALPR) e a API SISCAV

## Estado do repositório

O aplicativo Python que rodava em **`apps/iot-device/`** (câmera, OCR, envio para a API) **não faz mais parte deste repositório**. O que permanece aqui é a **API FastAPI** em `apps/api/src/`, que define o contrato para qualquer cliente (script, gateway, firmware com TLS, etc.).

Se você mantém um cliente ALPR em outro repo ou branch, use este documento apenas como referência de **integração HTTP**.

## O que a API espera do dispositivo

### Ingestão de log de acesso (principal)

- **Método / rota:** `POST /api/v1/access_logs/`
- **Formato:** `multipart/form-data`
  - Campo **`plate`**: string da placa (será normalizada no servidor).
  - Campo **`file`**: imagem (JPEG/PNG/WebP, etc., conforme validação em `apps/api/src/api/v1/controllers/access_log_controller.py`).
- **Autenticação opcional do dispositivo:** se a variável de ambiente **`DEVICE_INGEST_KEY`** estiver definida em ambiente não-development, o cliente deve enviar o header **`X-Device-Key`** com o mesmo valor (comparação segura no servidor — ver `apps/api/src/api/v1/deps.py`).

A API grava o arquivo em disco sob **`UPLOAD_DIR`** (padrão `uploads/`), registra status (autorizado / não autorizado / inválido, etc.) e relaciona com a whitelist.

### Outros endpoints úteis para integração

- **`GET /api/v1/health`** — disponibilidade.
- **Autenticação de usuários humanos:** OAuth2 password em **`POST /api/v1/login/access-token`**, refresh em **`POST /api/v1/login/refresh`** (detalhes em `docs/api/FRONTEND_INTEGRATION.md`).
- **Acionamento de portão (admin):** `POST /api/v1/gate_control/trigger` — requer JWT de usuário **admin** (`is_admin`); pode chamar URL configurada em **`GATE_ACTUATOR_URL`** (ver `apps/api/src/api/v1/controllers/gate_controller.py`).

Variáveis de ambiente relevantes estão documentadas em `apps/api/src/api/v1/core/config.py` e nos exemplos `env.local.example` / `env.supabase.example` na raiz do repositório.

## Script auxiliar no repositório (não é serviço IoT)

Existe código experimental / utilitário em **`apps/api/src/api/v1/ml/recognize-plate.py`**, **fora** da árvore de rotas HTTP da aplicação. Não substitui um pipeline IoT completo; trate como ferramenta local opcional.

## Onde documentar um novo cliente

- Contratos e exemplos HTTP: [`docs/api_curl_tests_guide.md`](../api_curl_tests_guide.md), coleção Postman em [`docs/`](../SISCAV_API.postman_collection.json).
- Visão de segurança e pontos de atenção: [`.planning/codebase/CONCERNS.md`](../../.planning/codebase/CONCERNS.md) (mapa do codebase GSD).

## Hardware / Arduino

Documentação histórica de hardware está em [`../hardware/README.md`](../hardware/README.md). Firmware que existia em `arduino/cancela_control/` pode não estar mais no tree; recupere via histórico Git se necessário.
