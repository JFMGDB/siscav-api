# Documentação da API

Esta pasta contém toda a documentação relacionada à API do sistema SISCAV.

## Índice

- [Documentação Técnica da API](../../apps/api/docs/technical-documentation.md)
   - Visão geral da arquitetura
   - Decisões técnicas
   - Recursos e endpoints
   - Acesso ao Swagger UI
- [Documentação de Integração Frontend](./FRONTEND_INTEGRATION.md)
   - Guia completo de integração de autenticação
   - Exemplos de código (TypeScript/React)
   - Gerenciamento de tokens
   - Tratamento de erros

**Nota**: A documentação técnica da API foi movida para `apps/api/docs/technical-documentation.md` para ficar próximo ao código-fonte.

Para informações sobre padrões de código e arquitetura, consulte também [Development - Padrões de Código](../development/coding-standards.md)

## Descrição

A API SISCAV é construída com FastAPI e serve como o backend central do sistema. Ela gerencia:

- Autenticação de administradores (JWT)
- Gerenciamento de whitelist de placas
- Recebimento e processamento de logs de acesso enviados por clientes de borda (`POST /api/v1/access_logs/`)
- Controle remoto do portão
- Servir imagens de acesso de forma segura

## Primeiro administrador

Contas criadas via `POST /api/v1/register` têm `is_admin = false`. Para promover o primeiro operador (PostgreSQL ou SQLite):

```sql
UPDATE users SET is_admin = 1 WHERE email = 'seu-email@exemplo.com';
```

No SQLite use `1` ou `true` conforme o cliente SQL. Após a migração `20260404_0002`, a coluna `is_admin` passa a existir em todas as bases novas.

## Whitelist (placas autorizadas)

Base path: **`/api/v1/whitelist/`**. Todas as operações exigem **`Authorization: Bearer`** com JWT válido (qualquer utilizador autenticado).

- **Normalização:** o servidor calcula `normalized_plate` a partir do texto enviado (remove caracteres não alfanuméricos e compara em maiúsculas). O valor normalizado é **único**: duas submissões que resultem no mesmo `normalized_plate` geram **409 Conflict**.
- **Formatos:** placas brasileiras no padrão **Mercosul** (ex. `ABC1D23`) ou **legado** três letras + quatro dígitos (ex. `ABC-1234`), validadas por `validate_brazilian_plate` / schema `AuthorizedPlateCreate`.
- **Erros comuns:** **400** / **422** formato inválido; **409** placa duplicada na whitelist; **404** ID inexistente em GET/PUT/DELETE.

## Logs de acesso

| Operação | Autenticação |
|----------|----------------|
| Registrar tentativa (`POST /api/v1/access_logs/`, multipart) | Cabeçalho **`X-Device-Key`** igual a `DEVICE_INGEST_KEY` (quando definido) |
| Listar registros (`GET /api/v1/access_logs/`) | **`Authorization: Bearer`** — qualquer utilizador autenticado |
| Obter imagem (`GET /api/v1/access_logs/images/{filename}`) | **`Authorization: Bearer`** de utilizador com **`is_admin`**; caso contrário **403** |

## Gate control

`POST /api/v1/gate_control/trigger` — **`Authorization: Bearer`** de administrador (`is_admin`).

- **`GATE_ACTUATOR_URL`:** se **não** definido, a resposta tem **`integration: "simulated"`** — nenhum comando é enviado a hardware; é apenas o modo honesto da API.
- Se definido, a API faz **POST** com corpo `{"action": "open"}` e só considera sucesso com **HTTP 2xx** do atuador (`integration: "live"`). Falhas de rede ou HTTP de erro → **502**/**503** com `detail` explícito.
- **`GATE_ACTUATOR_TIMEOUT_SECONDS`** (opcional, padrão 5): timeout em segundos.

## Dispositivos (Bluetooth) — demonstração

Rotas sob **`/api/v1/devices/`** (scan, connect, status, disconnect) são **simulação** para demos: cada resposta inclui **`demo: true`**.

- **`IOT_DEVICE_DEMO_API`:** em **`ENVIRONMENT=production`** / **`prod`** o valor predefinido é **desligado** → respostas **501** (API desativada; Bluetooth real é no **navegador** via Web Bluetooth, não neste servidor).
- Para ligar explicitamente: `IOT_DEVICE_DEMO_API=true` (ou omitir em development, onde o padrão é ligado).

## Princípios Aplicados

- **SOLID**: Separação de responsabilidades em camadas (Routers, CRUD, Schemas, Models)
- **DRY**: Reutilização de utilitários e funções compartilhadas
- **Componentização**: Estrutura modular e extensível













