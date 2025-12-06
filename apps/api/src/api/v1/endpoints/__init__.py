"""Endpoints FastAPI - Camada de roteamento HTTP (Views).

Este módulo contém os roteadores FastAPI que definem os endpoints da API.
Os endpoints são responsáveis apenas por roteamento HTTP, delegando
a lógica de negócio para os controllers.
"""

from apps.api.src.api.v1.endpoints.access_logs import router as access_logs_router
from apps.api.src.api.v1.endpoints.auth import router as auth_router
from apps.api.src.api.v1.endpoints.devices import router as devices_router
from apps.api.src.api.v1.endpoints.gate_control import router as gate_control_router
from apps.api.src.api.v1.endpoints.health import router as health_router
from apps.api.src.api.v1.endpoints.whitelist import router as whitelist_router

__all__ = [
    "health_router",
    "auth_router",
    "devices_router",
    "whitelist_router",
    "access_logs_router",
    "gate_control_router",
]

