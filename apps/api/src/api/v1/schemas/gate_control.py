"""Schemas para controle do portão."""

from typing import Literal

from pydantic import BaseModel, Field


class GateTriggerResponse(BaseModel):
    """Resposta de `POST /api/v1/gate_control/trigger`.

    **Contrato:** `integration` indica se o comando foi apenas simulado na API
    (`simulated`, sem `GATE_ACTUATOR_URL`) ou encaminhado a um atuador HTTP (`live`).
    Corpo JSON enviado ao atuador (modo live): `{"action": "open"}`.
    """

    integration: Literal["simulated", "live"] = Field(
        ...,
        description='simulated = nenhum atuador configurado; live = POST HTTP ao GATE_ACTUATOR_URL.',
    )
    message: str = Field(..., description="Mensagem legível para operadores.")
    acknowledged: bool = Field(
        False,
        description="True quando o atuador respondeu 2xx (apenas integration=live).",
    )
    downstream_status_code: int | None = Field(
        None,
        description="Código HTTP devolvido pelo atuador, se aplicável.",
    )
