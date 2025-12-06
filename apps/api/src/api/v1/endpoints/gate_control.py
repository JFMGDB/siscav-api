"""Endpoints para controle remoto do portão."""

from typing import Annotated

from fastapi import APIRouter, Depends

from apps.api.src.api.v1.controllers.gate_controller import GateController
from apps.api.src.api.v1.deps import get_current_user, get_gate_controller
from apps.api.src.api.v1.models.user import User

router = APIRouter()


@router.post("/trigger")
def trigger_gate(
    gate_controller: Annotated[GateController, Depends(get_gate_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """
    Acionar o portão remotamente.

    Este endpoint permite que um administrador autenticado acione
    a abertura do portão através do módulo relé.

    **Nota:** Em produção, este endpoint deve se comunicar com o
    dispositivo IoT para acionar o módulo relé físico.

    Args:
        gate_controller: Controller de controle de portão injetado via dependency injection
        current_user: Usuário autenticado

    Returns:
        dict: Status da operação

    Raises:
        HTTPException: Se houver erro no acionamento
    """
    return gate_controller.trigger_gate()


