from fastapi import APIRouter

from app.api.v1.endpoints.access_logs import router as access_logs_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.whitelist import router as whitelist_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router, tags=["login"])
api_router.include_router(whitelist_router, prefix="/whitelist", tags=["whitelist"])
api_router.include_router(access_logs_router, prefix="/access_logs", tags=["access_logs"])
