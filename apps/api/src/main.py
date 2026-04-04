import logging
import traceback

from apps.api.src.api.v1.core.config import assert_production_secrets_valid

assert_production_secrets_valid()

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from apps.api.src.api.v1.api import api_router
from apps.api.src.api.v1.core.limiter import limiter

logger = logging.getLogger(__name__)

description = """
SISCAV API - Sistema de Controle de Acesso Veicular.

## Visão Geral

Esta API fornece o backend para o sistema SISCAV, integrando dispositivos IoT (câmeras e microcomputadores) com um servidor central para controle automatizado de acesso veicular.

## Funcionalidades Principais

*   **Autenticação**: Login seguro via OAuth2 (JWT) com rate limiting.
*   **Gestão de Whitelist**: CRUD para placas autorizadas.
*   **Registro de Acesso**: Recebimento e processamento de logs de acesso (imagens e placas) dos dispositivos IoT via `POST /api/v1/access_logs/` — requer cabeçalho **`X-Device-Key`** quando `DEVICE_INGEST_KEY` está definido (em desenvolvimento sem chave configurada, o envio pode ser permitido; veja `env.local.example`).
*   **Listagem de logs (JSON)**: `GET /api/v1/access_logs/` exige **Bearer JWT** de qualquer utilizador autenticado (não é obrigatório ser administrador).
*   **Validação Automática**: Verificação de placas contra a whitelist para autorização de acesso.
*   **Controle Remoto**: Acionamento remoto do portão (`POST /api/v1/gate_control/trigger`) exige **JWT de administrador** (`is_admin`).
*   **Download de imagem de log**: `GET /api/v1/access_logs/images/{filename}` exige **JWT de administrador** (`is_admin`); utilizador sem `is_admin` recebe **403**.

## Tecnologias

*   Python 3.10+
*   FastAPI
*   SQLAlchemy
*   PostgreSQL
"""

app = FastAPI(
    title="Sistema de Controle de Acesso Veicular (SISCAV) API",
    description=description,
    version="1.0.0",
    contact={
        "name": "Equipe SISCAV",
        "email": "contato@siscav.com.br",
    },
    license_info={
        "name": "MIT",
    },
)

# Configurar rate limiting global
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# Handler global para exceções não tratadas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para capturar exceções não tratadas e retornar detalhes úteis."""
    logger.error(
        f"Erro não tratado: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )
    
    # Retornar detalhes do erro em desenvolvimento
    import os
    if os.getenv("ENVIRONMENT", "development") == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"Internal server error: {type(exc).__name__}: {str(exc)}",
                "type": type(exc).__name__,
                "traceback": traceback.format_exc() if os.getenv("DEBUG", "false").lower() == "true" else None,
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

# Configuração CORS
# Permite requisições do frontend em desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js default
        "http://localhost:5173",      # Vite default
        "http://localhost:8000",      # Frontend alternativo
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoint raiz
@app.get("/")
def read_root():
    """
    Endpoint raiz da API.

    Retorna mensagem de confirmação de que o servidor está online.
    """
    return {"message": "SISCAV API está online"}


# Agrega os roteadores da API v1
app.include_router(api_router, prefix="/api/v1")
