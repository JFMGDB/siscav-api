"""Endpoints para verificação de saúde da API."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """
    Verificação de saúde da API.

    Retorna o status operacional do servidor. Útil para monitoramento e health checks.
    """
    return {"status": "ok"}
