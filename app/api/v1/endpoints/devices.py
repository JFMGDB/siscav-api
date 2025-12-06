"""Endpoints para gerenciamento de dispositivos IoT."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.src.api.v1.controllers.device_controller import DeviceController
from apps.api.src.api.v1.deps import get_current_user, get_device_controller
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.device import (
    BluetoothDevice,
    ConnectionRequest,
    ConnectionResponse,
    ConnectionStatus,
    DisconnectResponse,
)

router = APIRouter(tags=["devices"])


@router.get("/scan", response_model=list[BluetoothDevice])
def scan_bluetooth_devices(
    device_controller: Annotated[DeviceController, Depends(get_device_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[BluetoothDevice]:
    """
    Escanear dispositivos Bluetooth disponíveis.

    Retorna uma lista de dispositivos Bluetooth visíveis que podem ser usados como câmera.
    Esta é uma simulação para fins de apresentação - em produção, seria integrado com
    a API Web Bluetooth do navegador.

    **Nota:** Esta funcionalidade requer que o frontend use a Web Bluetooth API
    diretamente no navegador, pois APIs de Bluetooth não podem ser acessadas
    diretamente via HTTP por questões de segurança.

    Args:
        device_controller: Controller de dispositivos injetado via dependency injection
        current_user: Usuário autenticado

    Returns:
        Lista de dispositivos Bluetooth detectados
    """
    return device_controller.scan_bluetooth_devices()


@router.post("/connect", response_model=ConnectionResponse)
def connect_bluetooth_device(
    request: ConnectionRequest,
    device_controller: Annotated[DeviceController, Depends(get_device_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConnectionResponse:
    """
    Conectar a um dispositivo Bluetooth.

    Estabelece conexão com a câmera Bluetooth selecionada.

    **Fluxo recomendado:**
    1. Frontend usa Web Bluetooth API para escanear dispositivos
    2. Usuário seleciona o dispositivo
    3. Frontend estabelece conexão Bluetooth
    4. Frontend obtém stream de vídeo via getUserMedia ou similar
    5. Stream é usado para captura de imagens

    **Nota:** A conexão Bluetooth real deve ser gerenciada pelo navegador
    via Web Bluetooth API por questões de segurança. Este endpoint serve
    como referência para integração.

    Args:
        request: Dados da requisição de conexão
        device_controller: Controller de dispositivos injetado via dependency injection
        current_user: Usuário autenticado

    Returns:
        ConnectionResponse: Resposta da tentativa de conexão

    Raises:
        HTTPException: Se device_id não for fornecido
    """
    if not request.device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="device_id é obrigatório"
        )

    return device_controller.connect_device(request)


@router.get("/status", response_model=ConnectionStatus)
def get_connection_status(
    device_controller: Annotated[DeviceController, Depends(get_device_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ConnectionStatus:
    """
    Verificar status da conexão Bluetooth.

    Retorna informações sobre o dispositivo atualmente conectado.

    Args:
        device_controller: Controller de dispositivos injetado via dependency injection
        current_user: Usuário autenticado

    Returns:
        ConnectionStatus: Status da conexão Bluetooth
    """
    return device_controller.get_connection_status()


@router.post("/disconnect", response_model=DisconnectResponse)
def disconnect_bluetooth_device(
    device_controller: Annotated[DeviceController, Depends(get_device_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DisconnectResponse:
    """
    Desconectar dispositivo Bluetooth.

    Encerra a conexão com a câmera Bluetooth atual.

    Args:
        device_controller: Controller de dispositivos injetado via dependency injection
        current_user: Usuário autenticado

    Returns:
        DisconnectResponse: Resposta da desconexão
    """
    return device_controller.disconnect_device()
