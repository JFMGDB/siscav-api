from fastapi import APIRouter

from apps.api.src.api.v1.endpoints.health import router as health_router


api_router = APIRouter()
api_router.include_router(health_router)


