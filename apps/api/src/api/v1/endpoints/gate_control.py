"""Endpoints para controle remoto do portão."""

from typing import Annotated

from fastapi import APIRouter, Depends

from apps.api.src.api.v1.controllers.gate_controller import GateController
from apps.api.src.api.v1.deps import get_current_admin_user, get_gate_controller
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.gate_control import GateTriggerResponse

router = APIRouter()


@router.post("/trigger", response_model=GateTriggerResponse)
def trigger_gate(
    gate_controller: Annotated[GateController, Depends(get_gate_controller)],
    _current_user: Annotated[User, Depends(get_current_admin_user)],
) -> GateTriggerResponse:
    """
    Acionar o portão remotamente.

    Requer JWT de **administrador** (`is_admin`).

    **Contrato (alteração):** a resposta inclui `integration`: `simulated` se
    `GATE_ACTUATOR_URL` não estiver definido (nenhum hardware contactado), ou
    `live` após POST JSON `{"action": "open"}` ao atuador com resposta 2xx.
    Falhas do atuador → **502**/**503** com `detail` explícito.

    Args:
        gate_controller: Controller de controle de portão injetado via dependency injection
        current_user: Administrador autenticado

    Returns:
        GateTriggerResponse: Modo simulado ou live e estado do ack downstream.

    Raises:
        HTTPException: Erro de rede ou resposta inválida do atuador (modo live).
    """
    return gate_controller.trigger_gate()
