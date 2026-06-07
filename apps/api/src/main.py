import logging
import os
import traceback
from contextlib import asynccontextmanager

from apps.api.src.api.v1.core.config import assert_production_secrets_valid, get_settings

assert_production_secrets_valid()

from fastapi import FastAPI, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from apps.api.src.api.v1.api import api_router
from apps.api.src.api.v1.core import error_messages as err
from apps.api.src.api.v1.core.limiter import limiter
from apps.api.src.api.v1.core.validation_errors import translate_validation_errors
from apps.api.src.api.v1.ml.classifier import get_vehicle_classifier

logger = logging.getLogger(__name__)
settings = get_settings()

description = """
SISCAV API - Sistema de Controle de Acesso Veicular.

## Visão Geral

Esta API fornece o backend para o sistema SISCAV, integrando dispositivos IoT (câmeras e microcomputadores) com um servidor central para controle automatizado de acesso veicular.

## Funcionalidades Principais

*   **Autenticação**: Login seguro via OAuth2 (JWT) com rate limiting.
*   **Gestão de Whitelist**: CRUD para placas autorizadas.
*   **Registro de Acesso**: Recebimento e processamento de logs de acesso (imagens e placas) dos dispositivos IoT via `POST /api/v1/access_logs/` — requer cabeçalho **`X-Device-Key`** quando `DEVICE_INGEST_KEY` está definido (em desenvolvimento sem chave configurada, o envio pode ser permitido; veja `env.local.example`).
*   **Listagem de logs (JSON)**: `GET /api/v1/access_logs/` exige **Bearer JWT** de administrador do cliente (`is_admin`, não superadmin).
*   **Validação Automática**: Verificação de placas contra a whitelist para autorização de acesso.
*   **Controle Remoto**: Acionamento remoto do portão (`POST /api/v1/gate_control/trigger`) exige **JWT de administrador do cliente**.
*   **Download de imagem de log**: `GET /api/v1/access_logs/images/{filename}` exige **JWT de administrador do cliente**.
*   **OCR opcional (frame → candidatos de placa)**: `POST /api/v1/ml/recognize-plate` (multipart, JPEG/PNG/WebP) exige **JWT de administrador do cliente**; sem pacotes ML instalados (`requirements-ml.txt`) responde **503**.
*   **Classificação veicular (frame → categoria)**: `POST /api/v1/ml/classify-vehicle` (multipart: `file` + `plate_hint` opcional) exige **JWT de administrador do cliente**; backend **stub** ou **onnx** via `VEHICLE_CLASSIFIER_BACKEND`.
*   **Gate**: `POST /api/v1/gate_control/trigger` — resposta com `integration` **simulated** (sem `GATE_ACTUATOR_URL`) ou **live** (POST ao atuador com 2xx); falhas do atuador → 502/503.

## Tecnologias

*   Python 3.10+
*   FastAPI
*   SQLAlchemy
*   PostgreSQL
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    if get_settings().vehicle_classifier_backend == "onnx":
        classifier = get_vehicle_classifier()
        warm_up = getattr(classifier, "warm_up", None)
        if callable(warm_up):
            try:
                await run_in_threadpool(warm_up)
                logger.info("ONNX ambulance classifier warm-up completed")
            except Exception:
                logger.warning(
                    "ONNX ambulance classifier warm-up failed; "
                    "classification may be unavailable until model loads",
                    exc_info=True,
                )
    yield


app = FastAPI(
    title="Sistema de Controle de Acesso Veicular (SISCAV) API",
    description=description,
    version="1.0.0",
    lifespan=lifespan,
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


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    _ = (request, exc)
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": err.RATE_LIMIT_EXCEEDED},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    _ = request
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": translate_validation_errors(exc.errors())}),
    )


app.add_middleware(SlowAPIMiddleware)


# Handler global para exceções não tratadas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para capturar exceções não tratadas e retornar detalhes úteis."""
    logger.exception(
        "Unhandled error: %s: %s",
        type(exc).__name__,
        exc,
        extra={"path": request.url.path, "method": request.method},
    )

    # Retornar detalhes do erro em desenvolvimento
    if os.getenv("ENVIRONMENT", "development") == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"{err.INTERNAL_SERVER_ERROR} ({type(exc).__name__}: {exc!s})",
                "type": type(exc).__name__,
                "traceback": traceback.format_exc()
                if os.getenv("DEBUG", "false").lower() == "true"
                else None,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": err.INTERNAL_SERVER_ERROR},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
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
