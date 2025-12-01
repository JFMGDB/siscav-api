from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.v1.api import api_router
from app.api.v1.core.rate_limit import limiter

app = FastAPI(title="Sistema de Controle de Acesso Veicular API", version="0.1.0")

# Configura rate limiting global
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,  # noqa: ARG001
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Handler customizado para exceções de rate limiting."""
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


# Endpoint raiz
@app.get("/")
def read_root():
    return {"message": "SISCAV API está online"}


# Agrega os roteadores da API v1
app.include_router(api_router, prefix="/api/v1")
