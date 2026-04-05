# Documentação operacional — API SISCAV

Esta seção descreve como **operar e validar a API** deste repositório. Documentação específica de um cliente Python IoT que existia em `apps/iot-device/` **não se aplica mais** — o tree atual é centrado em `apps/api/src/`.

## Verificar se a API está no ar

```bash
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health
```

Com a API rodando: **http://localhost:8000/docs** (Swagger).

## Variáveis de ambiente críticas

Resumo; detalhes em `apps/api/src/api/v1/core/config.py` e em [`docs/installation.md`](../installation.md).

| Variável | Uso |
|----------|-----|
| `DATABASE_URL` ou `POSTGRES_*` | Conexão PostgreSQL; sem isso, desenvolvimento pode usar SQLite (fallback em código). |
| `SECRET_KEY` | JWT; em `production`/`prod` não pode ser o valor de desenvolvimento. |
| `DEVICE_INGEST_KEY` | Se definido fora de ambiente de dev, ingestão `POST /api/v1/access_logs/` exige header `X-Device-Key`. |
| `GATE_ACTUATOR_URL` | Opcional; se vazio, acionamento de portão é simulado. |
| `UPLOAD_DIR`, `MAX_FILE_SIZE_MB` | Armazenamento de imagens de log de acesso. |

## Postman

Coleção e ambiente na pasta **`docs/`**:

- [`SISCAV_API.postman_collection.json`](../SISCAV_API.postman_collection.json)
- [`SISCAV_API.postman_environment.json`](../SISCAV_API.postman_environment.json)

Importe no Postman e ajuste `base_url` e tokens conforme o ambiente.

## Logs

A API usa `logging` padrão; mensagens aparecem no terminal do Uvicorn. Não há APM ou export OTLP configurado no código atual.

## Integração de dispositivos

Qualquer cliente que envie placas e imagens deve seguir o contrato em [`docs/iot/README.md`](../iot/README.md).

## CI

O pipeline em `.github/workflows/ci.yml` executa `ruff` e `pytest` com `requirements-dev.txt`.
