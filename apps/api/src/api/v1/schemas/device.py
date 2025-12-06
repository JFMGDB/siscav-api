"""Schemas para gerenciamento de dispositivos IoT."""

from typing import Optional

from pydantic import BaseModel


class BluetoothDevice(BaseModel):
    """Representa um dispositivo Bluetooth detectado."""

    id: str
    name: str
    type: str = "camera"
    signal_strength: Optional[int] = None


class ConnectionRequest(BaseModel):
    """Request para conectar a um dispositivo."""

    device_id: str


class ConnectionResponse(BaseModel):
    """Resposta da tentativa de conexão."""

    status: str
    device_id: str
    message: str
    camera_index: Optional[int] = None


class ConnectionStatus(BaseModel):
    """Status da conexão Bluetooth."""

    connected: bool
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    message: str


class DisconnectResponse(BaseModel):
    """Resposta da desconexão de dispositivo."""

    status: str
    message: str

