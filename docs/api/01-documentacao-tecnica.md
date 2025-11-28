# Documentação Técnica da API SISCAV

**Versão:** 1.0.0
**Data:** 28/11/2025
**Autor:** José Felipe Morais Guerra de Barros; Anderson Marcone da Silva Marinho;

---

## 1. Introdução

Este documento descreve a API do Sistema de Controle de Acesso Veicular (SISCAV). A API serve como o backend central que orquestra a comunicação entre os dispositivos IoT (câmeras/endpoints) e o banco de dados, além de fornecer interfaces de gerenciamento para administradores.

A documentação interativa completa dos endpoints, incluindo esquemas de requisição e resposta, está disponível via **Swagger UI** integrado à aplicação.

## 2. Acesso à Documentação Interativa (Swagger)

A API utiliza o padrão OpenAPI (anteriormente Swagger) para especificação automática.

### Como Acessar

1.  Inicie o servidor de desenvolvimento:
    ```bash
    uvicorn apps.api.src.main:app --reload
    ```
2.  Acesse o navegador no endereço:
    *   **Swagger UI:** `http://127.0.0.1:8000/docs`
    *   **ReDoc:** `http://127.0.0.1:8000/redoc`

O Swagger UI permite testar as requisições diretamente pelo navegador.

## 3. Visão Geral da Arquitetura

O sistema segue uma arquitetura cliente-servidor RESTful.

*   **Backend:** Python com FastAPI.
*   **Banco de Dados:** PostgreSQL (gerenciado via SQLAlchemy e Alembic).
*   **Autenticação:** OAuth2 com JWT (JSON Web Tokens).
*   **IoT Integration:** Endpoints específicos para recebimento de imagens e metadados dos dispositivos de borda.

### Diagrama de Fluxo Simplificado

1.  **IoT Device** captura imagem -> OCR local (opcional) -> Envia para API (`POST /access_logs/`).
2.  **API** recebe dados -> Normaliza Placa -> Consulta Whitelist (Banco de Dados).
3.  **API** decide acesso (Authorized/Denied) -> Salva Log -> Retorna decisão.
4.  **IoT Device** recebe decisão -> Aciona Relé (se autorizado).

## 4. Decisões Técnicas

### 4.1. Framework: FastAPI
Optamos pelo **FastAPI** devido a:
*   **Performance:** Alta performance com suporte nativo a assincronismo (`async/await`), crucial para lidar com múltiplas requisições de dispositivos IoT simultaneamente.
*   **Documentação Automática:** Geração nativa de OpenAPI/Swagger, garantindo que a documentação esteja sempre sincronizada com o código.
*   **Validação de Dados:** Integração forte com **Pydantic**, garantindo integridade dos dados recebidos (ex: formatos de placa, imagens).

### 4.2. Padrões de Projeto
*   **SOLID:** O código é estruturado em camadas (Routers, Controllers/Endpoints, CRUD, Schemas, Models), facilitando manutenção e testes.
*   **DRY (Don't Repeat Yourself):** Reutilização de esquemas Pydantic e funções utilitárias de banco de dados.
*   **Componentização:** A estrutura de pastas separa claramente as responsabilidades (`api/v1/endpoints`, `core`, `db`, `schemas`).

### 4.3. Segurança
*   **JWT:** Utilizado para autenticação stateless, ideal para APIs REST.
*   **Hashing de Senhas:** Utilização de algoritmos robustos (Argon2/Bcrypt) via `passlib`.
*   **CORS:** Configurado para permitir requisições do frontend em desenvolvimento (localhost nas portas 3000, 5173, 8000).

### 4.4. Integração IoT (Câmera)
*   **Dispositivo de Captura:** O sistema utiliza uma câmera conectada via **Bluetooth** (ex: smartphone).
*   **Gerenciamento via Frontend:** A conexão e o pareamento com a câmera são realizados diretamente pela interface web. O usuário pode buscar dispositivos próximos e conectar-se sem necessidade de configuração manual no sistema operacional/terminal.
*   **Processamento:** O endpoint IoT recebe o stream de vídeo após a conexão estabelecida.

## 5. Recursos da API

### Autenticação (`/auth`)
*   **POST /login/access-token**: Endpoint para troca de credenciais (email/senha) por token JWT.

### Gestão de Dispositivos (`/devices`)
Endpoints para gerenciamento da conexão Bluetooth (funcionalidade de apresentação).
*   **GET /scan**: Listar dispositivos Bluetooth visíveis.
*   **POST /connect**: Conectar à câmera selecionada.

### Whitelist (`/whitelist`)
Gerenciamento de placas autorizadas. Acesso restrito a administradores autenticados.
*   **GET /**: Listar placas.
*   **POST /**: Adicionar nova placa.
*   **GET /{id}**: Obter detalhes de uma placa específica.
*   **PUT /{id}**: Atualizar dados de uma placa.
*   **DELETE /{id}**: Remover placa da whitelist.

### Logs de Acesso (`/access_logs`)
*   **POST /**: Endpoint principal utilizado pelos dispositivos IoT. Recebe a imagem e a leitura da placa, processa a regra de negócio e retorna a autorização.

## 6. Modelagem de Dados (Resumo)

*   **User**: Usuários do sistema (administradores).
*   **AuthorizedPlate**: Placas permitidas (Whitelist). Campos: `plate` (original), `normalized_plate` (busca), `description`.
*   **AccessLog**: Histórico de tentativas de acesso. Campos: `timestamp`, `plate_detected`, `image_path`, `status` (Authorized/Denied).

---