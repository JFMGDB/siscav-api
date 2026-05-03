"""Testes unitários para DeviceController."""

from apps.api.src.api.v1.controllers.device_controller import DeviceController
from apps.api.src.api.v1.schemas.device import ConnectionRequest


class TestDeviceController:
    """Testes para DeviceController."""

    def test_scan_bluetooth_devices(self):
        """Testa escaneamento de dispositivos Bluetooth."""
        controller = DeviceController()
        devices = controller.scan_bluetooth_devices()

        assert isinstance(devices, list)
        assert len(devices) > 0
        assert all(hasattr(device, "id") for device in devices)
        assert all(hasattr(device, "name") for device in devices)

    def test_connect_device(self):
        """Testa conexão com dispositivo."""
        controller = DeviceController()
        request = ConnectionRequest(device_id="test_device_123")

        response = controller.connect_device(request)

        assert response.status == "connected"
        assert response.device_id == "test_device_123"
        assert response.message is not None
        assert response.camera_index is not None

    def test_get_connection_status(self):
        """Testa obtenção de status de conexão."""
        controller = DeviceController()
        status = controller.get_connection_status()

        assert status.connected is False
        assert status.device_id is None
        assert status.message is not None

    def test_disconnect_device(self):
        """Testa desconexão de dispositivo."""
        controller = DeviceController()
        response = controller.disconnect_device()

        assert response.status == "disconnected"
        assert response.message is not None

