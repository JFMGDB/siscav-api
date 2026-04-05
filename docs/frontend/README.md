# Frontend operador (SISCAV)

A interface web para **operadores** (dashboard, pré-visualização de câmara, etc.) é implementada em **Next.js** com **TypeScript**, num **repositório Git separado** deste (`siscav-api`). Este diretório contém apenas **documentação** para esse cliente.

## Documentos

| Documento | Descrição |
|-----------|-----------|
| [camera-preview-nextjs.md](camera-preview-nextjs.md) | Guia: ligação **USB** (`getUserMedia`) e **Wi‑Fi/URL** (stream MJPEG/HLS/snapshot) com pré-visualização em tempo real no browser. |

## API e autenticação

- Contrato JWT e fluxos: [`docs/api/FRONTEND_INTEGRATION.md`](../api/FRONTEND_INTEGRATION.md).
- CORS em desenvolvimento: a API já permite origem **Next.js** em `http://localhost:3000` — ver `apps/api/src/main.py` (`CORSMiddleware`).

## Variáveis de ambiente (no repo Next)

Definir no projeto frontend, por exemplo:

- `NEXT_PUBLIC_SISCAV_API_URL` — URL base da API (ex. `http://127.0.0.1:8000`).

Isto **não** substitui a URL da câmara IP na rede local; são conceitos distintos (API vs stream de vídeo).
