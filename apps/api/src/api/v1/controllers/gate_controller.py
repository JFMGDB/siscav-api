"""Controller para lógica de negócio de controle de portão."""

import json
import logging
import socket
import urllib.error
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from apps.api.src.api.v1.core.config import Settings
from apps.api.src.api.v1.schemas.gate_control import GateTriggerResponse

logger = logging.getLogger(__name__)


class GateController:
    """Controller para operações de controle de portão."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def trigger_gate(self) -> GateTriggerResponse:
        """
        Aciona o portão remotamente (simulado ou via HTTP ao atuador).

        Sem `GATE_ACTUATOR_URL`: retorna `integration=simulated` (nenhum hardware contactado).
        Com URL: POST JSON `{"action": "open"}`; sucesso só com HTTP 2xx do atuador.
        """
        raw_url = (self._settings.gate_actuator_url or "").strip()
        if not raw_url:
            return GateTriggerResponse(
                integration="simulated",
                message=(
                    "Modo simulado: GATE_ACTUATOR_URL não está definido. "
                    "Nenhum comando foi enviado a um relé ou atuador físico."
                ),
                acknowledged=False,
                downstream_status_code=None,
            )

        timeout = self._settings.gate_actuator_timeout_seconds
        payload = json.dumps({"action": "open"}).encode("utf-8")
        req = Request(
            raw_url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(req, timeout=timeout) as resp:
                code = resp.getcode()
                if 200 <= code < 300:
                    return GateTriggerResponse(
                        integration="live",
                        message="Atuador respondeu com sucesso (HTTP 2xx).",
                        acknowledged=True,
                        downstream_status_code=code,
                    )
                logger.warning("Gate actuator returned non-2xx after urlopen: %s", code)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Atuador retornou status HTTP {code}",
                )
        except HTTPException:
            raise
        except socket.timeout:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Tempo esgotado ao contactar o atuador do portão",
            ) from None
        except urllib.error.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Atuador retornou erro HTTP {e.code}: {e.reason}",
            ) from e
        except urllib.error.URLError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Falha de rede ao contactar o atuador: {e.reason!s}",
            ) from e
