"""Testes unitários para GateController."""

from unittest.mock import MagicMock

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
        assert "simulado" in result.message.lower() or "GATE_ACTUATOR" in result.message
