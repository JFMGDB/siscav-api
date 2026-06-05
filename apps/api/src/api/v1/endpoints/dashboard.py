"""Endpoints de métricas operacionais do dashboard."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.deps import get_access_log_controller, get_current_client_admin_user
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.access_log import DashboardDailyMetrics
from apps.api.src.api.v1.utils.timezone_br import BRAZIL_TZ

router = APIRouter()


@router.get("/metrics", response_model=DashboardDailyMetrics)
def get_daily_metrics(
    access_log_controller: Annotated[AccessLogController, Depends(get_access_log_controller)],
    _current_user: Annotated[User, Depends(get_current_client_admin_user)],
    day: Annotated[
        date | None,
        Query(
            alias="date",
            description="Dia civil (YYYY-MM-DD) em America/Sao_Paulo. Padrão: hoje.",
        ),
    ] = None,
) -> DashboardDailyMetrics:
    """Métricas consolidadas de acesso para um dia específico."""
    target = day or datetime.now(BRAZIL_TZ).date()
    access_metrics, ocr_success_rate_percent = access_log_controller.get_daily_metrics(target)
    return DashboardDailyMetrics(
        date=target,
        traffic_volume=access_metrics.traffic_volume,
        auto_approval_rate_percent=access_metrics.auto_approval_rate_percent,
        ocr_success_rate_percent=ocr_success_rate_percent,
    )
