from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from apps.api.src.api.v1.api import api_router
from apps.api.src.api.v1.core.limiter import limiter

description = """
SISCAV API - Sistema de Controle de Acesso Veicular.

## Visão Geral

Esta API fornece o backend para o sistema SISCAV, integrando dispositivos IoT (câmeras e microcomputadores) com um servidor central para controle automatizado de acesso veicular.

## Funcionalidades Principais

*   **Autenticação**: Login seguro via OAuth2 (JWT) com rate limiting.
*   **Gestão de Whitelist**: CRUD para placas autorizadas.
*   **Registro de Acesso**: Recebimento e processamento de logs de acesso (imagens e placas) dos dispositivos IoT.
*   **Validação Automática**: Verificação de placas contra a whitelist para autorização de acesso.
*   **Controle Remoto**: Acionamento remoto do portão via módulo relé.

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
