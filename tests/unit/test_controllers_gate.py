"""Testes unitários para GateController."""

from unittest.mock import MagicMock, patch

from apps.api.src.api.v1.controllers.gate_controller import (
    GateController,
    _actuator_url_for_action,
)


class TestGateController:
    """Testes para GateController."""

    def test_actuator_url_for_action_derives_close_from_open(self):
        assert (
            _actuator_url_for_action("http://127.0.0.1:9080/open", "close")
            == "http://127.0.0.1:9080/close"
        )
        assert (
            _actuator_url_for_action("http://127.0.0.1:9080/open", "open")
            == "http://127.0.0.1:9080/open"
        )

    def test_trigger_gate_simulated_without_url(self):
        """Sem URL de atuador → integration simulated."""
        settings = MagicMock()
        settings.gate_actuator_url = None
        settings.gate_actuator_timeout_seconds = 30
        controller = GateController(settings)
        result = controller.trigger_gate()

        assert result.integration == "simulated"
        assert result.acknowledged is False
        assert result.status == "ok"
        assert "simulado" in result.message.lower() or "GATE_ACTUATOR" in result.message

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_trigger_gate_safe_timeout_acknowledges_optimistically(
        self, mock_urlopen: MagicMock
    ):
        mock_urlopen.side_effect = TimeoutError()
        settings = MagicMock()
        settings.gate_actuator_url = "http://127.0.0.1:9080/open"
        settings.gate_actuator_timeout_seconds = 30
        settings.gate_auto_open_timeout_seconds = 15.0
        controller = GateController(settings)
        result = controller.trigger_gate_safe()

        assert result.status == "ok"
        assert result.integration == "live"
        assert result.acknowledged is True

    @patch("apps.api.src.api.v1.controllers.gate_controller.time.sleep")
    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_trigger_gate_safe_connection_reset_returns_error_envelope(
        self, mock_urlopen: MagicMock, _mock_sleep: MagicMock
    ):
        mock_urlopen.side_effect = ConnectionResetError(
            10054, "An existing connection was forcibly closed by the remote host"
        )
        settings = MagicMock()
        settings.gate_actuator_url = "http://127.0.0.1:9080/open"
        settings.gate_actuator_timeout_seconds = 30
        settings.gate_auto_open_timeout_seconds = 15.0
        controller = GateController(settings)
        result = controller.trigger_gate_safe()

        assert result.status == "error"
        assert result.reason == "actuator_network_error"
        assert result.integration == "live"
        assert result.acknowledged is False
        assert mock_urlopen.call_count == 4

    @patch("apps.api.src.api.v1.controllers.gate_controller.time.sleep")
    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_trigger_gate_safe_retries_then_succeeds(
        self, mock_urlopen: MagicMock, _mock_sleep: MagicMock
    ):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_resp
        mock_cm.__exit__.return_value = None
        mock_urlopen.side_effect = [
            ConnectionResetError(10054, "forcibly closed"),
            mock_cm,
        ]

        settings = MagicMock()
        settings.gate_actuator_url = "http://127.0.0.1:9080/open"
        settings.gate_actuator_timeout_seconds = 30
        settings.gate_auto_open_timeout_seconds = 15.0
        controller = GateController(settings)
        result = controller.trigger_gate_safe()

        assert result.status == "ok"
        assert result.acknowledged is True
        assert mock_urlopen.call_count == 2

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_close_gate_live_calls_close_url(self, mock_urlopen: MagicMock):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_resp
        mock_cm.__exit__.return_value = None
        mock_urlopen.return_value = mock_cm

        settings = MagicMock()
        settings.gate_actuator_url = "http://127.0.0.1:9080/open"
        settings.gate_actuator_timeout_seconds = 30
        controller = GateController(settings)
        result = controller.close_gate()

        assert result.integration == "live"
        assert result.acknowledged is True
        call_req = mock_urlopen.call_args[0][0]
        assert call_req.full_url == "http://127.0.0.1:9080/close"
        assert call_req.data == b'{"action": "close"}'
