"""Schemas para controle do portão."""

from typing import Literal

from pydantic import BaseModel, Field

GateTriggerReason = Literal[
    "actuator_timeout",
    "connection_refused",
    "actuator_http_error",
    "actuator_network_error",
]


class GateTriggerResponse(BaseModel):
    """Resposta de `POST /api/v1/gate_control/trigger` e auto-open em access logs.

    **Contrato:** `integration` indica se o comando foi apenas simulado na API
    (`simulated`, sem `GATE_ACTUATOR_URL`) ou encaminhado a um atuador HTTP (`live`).
    Corpo JSON enviado ao atuador (modo live): `{"action": "open"}`.

    Em auto-open (`POST /access_logs/`), falhas do atuador usam `status=error` e `reason`
    sem alterar o HTTP status do log (201 Created).
    """

    integration: Literal["simulated", "live"] = Field(
        ...,
        description="simulated = nenhum atuador configurado; live = POST HTTP ao GATE_ACTUATOR_URL.",
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
    status: Literal["ok", "error"] | None = Field(
        None,
        description="ok = sucesso ou simulado; error = atuador configurado mas falhou (auto-open).",
    )
    reason: GateTriggerReason | None = Field(
        None,
        description="Motivo da falha do atuador quando status=error.",
    )
