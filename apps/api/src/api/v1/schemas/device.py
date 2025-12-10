"""Schemas para dispositivos IoT."""

from pydantic import BaseModel


class BluetoothDevice(BaseModel):
    """Schema para dispositivo Bluetooth."""

    id: str
    name: str
    type: str
    signal_strength: int


class ConnectionRequest(BaseModel):
    """Schema para requisição de conexão."""

    device_id: str


class ConnectionResponse(BaseModel):
    """Schema para resposta de conexão."""

    status: str
    device_id: str
    message: str
    camera_index: int


class ConnectionStatus(BaseModel):
    """Schema para status de conexão."""

    connected: bool
    device_id: str | None = None
    device_name: str | None = None
    message: str


class DisconnectResponse(BaseModel):
    """Schema para resposta de desconexão."""

    status: str
    message: str

