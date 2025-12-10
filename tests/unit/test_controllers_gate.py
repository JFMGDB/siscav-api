"""Testes unitários para GateController."""

from app.api.v1.controllers.gate_controller import GateController


class TestGateController:
    """Testes para GateController."""

    def test_trigger_gate(self):
        """Testa acionamento do portão."""
        controller = GateController()
        result = controller.trigger_gate()

        assert isinstance(result, dict)
        assert "status" in result
        assert "message" in result
        assert result["status"] == "success"
        assert "sucesso" in result["message"].lower()

