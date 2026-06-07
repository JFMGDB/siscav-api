"""Testes unitários para GateController."""

from unittest.mock import MagicMock, patch

from apps.api.src.api.v1.controllers.gate_controller import GateController


class TestGateController:
    """Testes para GateController."""

    def test_trigger_gate_simulated_without_url(self):
        """Sem URL de atuador → integration simulated."""
        settings = MagicMock()
        settings.gate_actuator_url = None
        settings.gate_actuator_timeout_seconds = 5
        controller = GateController(settings)
        result = controller.trigger_gate()

        assert result.integration == "simulated"
        assert result.acknowledged is False
        assert result.status == "ok"
        assert "simulado" in result.message.lower() or "GATE_ACTUATOR" in result.message

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_trigger_gate_safe_timeout_returns_error_envelope(self, mock_urlopen: MagicMock):
        mock_urlopen.side_effect = TimeoutError()
        settings = MagicMock()
        settings.gate_actuator_url = "http://127.0.0.1:9080/open"
        settings.gate_actuator_timeout_seconds = 5
        settings.gate_auto_open_timeout_seconds = 2.0
        controller = GateController(settings)
        result = controller.trigger_gate_safe()

        assert result.status == "error"
        assert result.reason == "actuator_timeout"
        assert result.integration == "live"
        assert result.acknowledged is False

    @patch("apps.api.src.api.v1.controllers.gate_controller.urlopen")
    def test_trigger_gate_safe_connection_reset_returns_error_envelope(
        self, mock_urlopen: MagicMock
    ):
        mock_urlopen.side_effect = ConnectionResetError(
            10054, "An existing connection was forcibly closed by the remote host"
        )
        settings = MagicMock()
        settings.gate_actuator_url = "http://127.0.0.1:9080/open"
        settings.gate_actuator_timeout_seconds = 5
        settings.gate_auto_open_timeout_seconds = 2.0
        controller = GateController(settings)
        result = controller.trigger_gate_safe()

        assert result.status == "error"
        assert result.reason == "actuator_network_error"
        assert result.integration == "live"
        assert result.acknowledged is False
