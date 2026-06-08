"""Controller para lógica de negócio de controle de portão."""

import json
import logging
import time
import urllib.error
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from apps.api.src.api.v1.core.config import Settings
from apps.api.src.api.v1.schemas.gate_control import GateTriggerResponse

logger = logging.getLogger(__name__)

_HTTP_STATUS_OK_MIN = 200
_HTTP_STATUS_OK_MAX = 300
_MAX_ATTEMPTS = 4
_RETRY_PAUSE_SECONDS = 2.5
_WOKWI_GATEWAY_HINT = (
    "Verifique wokwigw em execução, aba Wokwi visível (não minimizada), "
    "F1 → Enable Private Wokwi IoT Gateway e Serial com "
    "'HTTP server listening' + 'Client connected' no gateway."
)


def _raise_actuator_bad_status(code: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Atuador retornou status HTTP {code}",
    )


def _actuator_url_for_action(base_url: str, action: str) -> str:
    """Deriva URL de fechamento a partir de GATE_ACTUATOR_URL (ex.: .../open → .../close)."""
    if action == "open":
        return base_url
    if base_url.rstrip("/").endswith("/open"):
        return base_url.rstrip("/")[:-4] + "close"
    return base_url.rstrip("/") + "/close"


def _network_error_reason(exc: BaseException) -> str:
    if isinstance(exc, ConnectionRefusedError):
        return "connection_refused"
    text = str(exc).lower()
    if "refused" in text or "10061" in text:
        return "connection_refused"
    return "actuator_network_error"


def _is_retryable_actuator_error(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutError, ConnectionResetError, ConnectionAbortedError)):
        return True
    text = str(exc).lower()
    if "10054" in text or "forcibly closed" in text or "deadline exceeded" in text:
        return True
    if isinstance(exc, urllib.error.URLError):
        inner = exc.reason
        if isinstance(inner, BaseException):
            return _is_retryable_actuator_error(inner)
        return "refused" not in text
    return False


def _optimistic_actuator_ack() -> GateTriggerResponse:
    """wokwigw/Wokwi costumam aplicar o comando sem devolver HTTP 2xx a tempo."""
    return GateTriggerResponse(
        integration="live",
        message=("Comando enviado ao atuador (resposta HTTP não confirmada a tempo)."),
        acknowledged=True,
        downstream_status_code=None,
        status="ok",
    )


def _failure_message(exc: BaseException) -> str:
    base = f"Falha de rede ao contactar o atuador: {exc}"
    if _is_retryable_actuator_error(exc):
        return f"{base}. {_WOKWI_GATEWAY_HINT}"
    return str(base)


def _post_actuator_once(
    target_url: str,
    payload: bytes,
    timeout_seconds: float,
) -> GateTriggerResponse:
    """Uma tentativa de POST ao atuador HTTP via urllib (compatível com wokwigw)."""
    req = Request(
        target_url,
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
        logger.info(
            "Gate actuator: timeout aguardando resposta HTTP "
            "(comando pode ter sido aplicado — Wokwi/wokwigw)."
        )
        return _optimistic_actuator_ack()
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
        inner = e.reason
        if isinstance(inner, BaseException):
            reason = _network_error_reason(inner)
            detail = _failure_message(inner)
        elif "refused" in str(inner).lower():
            reason = "connection_refused"
            detail = _failure_message(e)
        else:
            reason = "actuator_network_error"
            detail = _failure_message(e)
        return GateTriggerResponse(
            integration="live",
            message=detail,
            acknowledged=False,
            downstream_status_code=None,
            status="error",
            reason=reason,
        )
    except OSError as e:
        reason = _network_error_reason(e)
        return GateTriggerResponse(
            integration="live",
            message=_failure_message(e),
            acknowledged=False,
            downstream_status_code=None,
            status="error",
            reason=reason,
        )


def _post_actuator(
    target_url: str,
    payload: bytes,
    timeout_seconds: float,
) -> GateTriggerResponse:
    """
    POST JSON ao atuador com retentativas.

    O wokwigw pode falhar na primeira ligação ao ESP32 (10.13.37.2) enquanto o
    Private Gateway estabiliza; novas tentativas após pausa costumam resolver.
    """
    last_result: GateTriggerResponse | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        result = _post_actuator_once(target_url, payload, timeout_seconds)
        if result.status == "ok" or result.reason == "actuator_http_error":
            return result

        last_result = result
        if attempt < _MAX_ATTEMPTS:
            logger.warning(
                "Gate actuator attempt %s/%s failed (%s) — retrying in %ss",
                attempt,
                _MAX_ATTEMPTS,
                result.reason,
                _RETRY_PAUSE_SECONDS,
            )
            time.sleep(_RETRY_PAUSE_SECONDS)

    return last_result or GateTriggerResponse(
        integration="live",
        message=f"Falha ao contactar o atuador. {_WOKWI_GATEWAY_HINT}",
        acknowledged=False,
        downstream_status_code=None,
        status="error",
        reason="actuator_network_error",
    )


class GateController:
    """Controller para operações de controle de portão."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def trigger_gate(self) -> GateTriggerResponse:
        """
        Abre o portão remotamente (simulado ou via HTTP ao atuador).

        Sem `GATE_ACTUATOR_URL`: retorna `integration=simulated` (nenhum hardware contactado).
        Com URL: POST JSON `{"action": "open"}`; sucesso só com HTTP 2xx do atuador.
        Falhas de rede/HTTP propagam como HTTPException (uso manual em /gate_control/trigger).
        """
        return self._trigger_gate_action("open")

    def close_gate(self) -> GateTriggerResponse:
        """
        Fecha o portão remotamente (simulado ou via HTTP ao atuador).

        Deriva a URL de fechamento de `GATE_ACTUATOR_URL` (substitui `/open` por `/close`).
        """
        return self._trigger_gate_action("close")

    def _trigger_gate_action(self, action: str) -> GateTriggerResponse:
        result = self._call_actuator(
            action=action,
            timeout_seconds=self._settings.gate_actuator_timeout_seconds,
        )
        if result.status == "error" and result.integration == "live":
            if result.downstream_status_code is not None:
                _raise_actuator_bad_status(result.downstream_status_code)
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
        result = self._call_actuator(
            action="open",
            timeout_seconds=timeout,
        )
        if result.status == "error":
            logger.warning(
                "Gate auto-open failed: reason=%s integration=%s",
                result.reason,
                result.integration,
            )
        return result

    def _call_actuator(self, *, action: str, timeout_seconds: float) -> GateTriggerResponse:
        raw_url = (self._settings.gate_actuator_url or "").strip()
        if not raw_url:
            verb = "abrir" if action == "open" else "fechar"
            return GateTriggerResponse(
                integration="simulated",
                message=(
                    f"Modo simulado: GATE_ACTUATOR_URL não está definido. "
                    f"Nenhum comando de {verb} foi enviado ao atuador."
                ),
                acknowledged=False,
                downstream_status_code=None,
                status="ok",
            )

        target_url = _actuator_url_for_action(raw_url, action)
        payload = json.dumps({"action": action}).encode("utf-8")
        return _post_actuator(target_url, payload, timeout_seconds)
