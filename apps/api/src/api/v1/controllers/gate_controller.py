"""Controller para lógica de negócio de controle de portão."""

import json
import logging
import urllib.error
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from apps.api.src.api.v1.core.config import Settings
from apps.api.src.api.v1.schemas.gate_control import GateTriggerResponse

logger = logging.getLogger(__name__)

_HTTP_STATUS_OK_MIN = 200
_HTTP_STATUS_OK_MAX = 300


def _raise_actuator_bad_status(code: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Atuador retornou status HTTP {code}",
    )


class GateController:
    """Controller para operações de controle de portão."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def trigger_gate(self) -> GateTriggerResponse:
        """
        Aciona o portão remotamente (simulado ou via HTTP ao atuador).

        Sem `GATE_ACTUATOR_URL`: retorna `integration=simulated` (nenhum hardware contactado).
        Com URL: POST JSON `{"action": "open"}`; sucesso só com HTTP 2xx do atuador.
        Falhas de rede/HTTP propagam como HTTPException (uso manual em /gate_control/trigger).
        """
        result = self._call_actuator(timeout_seconds=self._settings.gate_actuator_timeout_seconds)
        if result.status == "error" and result.integration == "live":
            if result.downstream_status_code is not None:
                _raise_actuator_bad_status(result.downstream_status_code)
            if result.reason == "actuator_timeout":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Tempo esgotado ao contactar o atuador do portão",
                )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=result.message,
            )
        return result

    def trigger_gate_safe(
        self,
        *,
        timeout_seconds: float | None = None,
    ) -> GateTriggerResponse:
        """
        Aciona o portão após autorização de access log.

        Nunca levanta HTTPException: falhas do atuador retornam `status=error` com `reason`.
        """
        timeout = (
            timeout_seconds
            if timeout_seconds is not None
            else self._settings.gate_auto_open_timeout_seconds
        )
        result = self._call_actuator(timeout_seconds=timeout)
        if result.status == "error":
            logger.warning(
                "Gate auto-open failed: reason=%s integration=%s",
                result.reason,
                result.integration,
            )
        return result

    def _call_actuator(self, *, timeout_seconds: float) -> GateTriggerResponse:
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
                status="ok",
            )

        payload = json.dumps({"action": "open"}).encode("utf-8")
        req = Request(
            raw_url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(req, timeout=timeout_seconds) as resp:
                code = resp.getcode()
            if _HTTP_STATUS_OK_MIN <= code < _HTTP_STATUS_OK_MAX:
                return GateTriggerResponse(
                    integration="live",
                    message="Atuador respondeu com sucesso (HTTP 2xx).",
                    acknowledged=True,
                    downstream_status_code=code,
                    status="ok",
                )
            logger.warning("Gate actuator returned non-2xx after urlopen: %s", code)
            return GateTriggerResponse(
                integration="live",
                message=f"Atuador retornou status HTTP {code}.",
                acknowledged=False,
                downstream_status_code=code,
                status="error",
                reason="actuator_http_error",
            )
        except TimeoutError:
            return GateTriggerResponse(
                integration="live",
                message="Access authorized; gate actuator did not respond within timeout.",
                acknowledged=False,
                downstream_status_code=None,
                status="error",
                reason="actuator_timeout",
            )
        except urllib.error.HTTPError as e:
            return GateTriggerResponse(
                integration="live",
                message=f"Atuador retornou erro HTTP {e.code}: {e.reason}.",
                acknowledged=False,
                downstream_status_code=e.code,
                status="error",
                reason="actuator_http_error",
            )
        except urllib.error.URLError as e:
            reason = (
                "connection_refused"
                if "refused" in str(e.reason).lower()
                else "actuator_network_error"
            )
            return GateTriggerResponse(
                integration="live",
                message=f"Falha de rede ao contactar o atuador: {e.reason!s}.",
                acknowledged=False,
                downstream_status_code=None,
                status="error",
                reason=reason,
            )
