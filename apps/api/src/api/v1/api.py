"""Agregador de roteadores da API v1.

Este módulo centraliza todos os roteadores da versão 1 da API,
organizando-os por domínio de funcionalidade.
"""

from fastapi import APIRouter

from apps.api.src.api.v1.endpoints.access_logs import router as access_logs_router
from apps.api.src.api.v1.endpoints.auth import router as auth_router
from apps.api.src.api.v1.endpoints.devices import router as devices_router
from apps.api.src.api.v1.endpoints.gate_control import router as gate_control_router
from apps.api.src.api.v1.endpoints.health import router as health_router
from apps.api.src.api.v1.endpoints.whitelist import router as whitelist_router

api_router = APIRouter()

# Health check (sem prefixo, acessível em /api/v1/health)
api_router.include_router(health_router)

# Autenticação
api_router.include_router(auth_router, tags=["login"])

# Dispositivos IoT
api_router.include_router(devices_router, prefix="/devices", tags=["devices"])

# Gerenciamento de whitelist (placas autorizadas)
api_router.include_router(whitelist_router, prefix="/whitelist", tags=["whitelist"])

# Logs de acesso
api_router.include_router(access_logs_router, prefix="/access_logs", tags=["access_logs"])

# Controle de portão
api_router.include_router(gate_control_router, prefix="/gate_control", tags=["gate_control"])
