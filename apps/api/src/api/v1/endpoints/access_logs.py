"""Endpoints para gerenciamento de logs de acesso veicular."""

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.deps import get_access_log_controller, get_current_user
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.access_log import AccessLogRead, AccessStatus

router = APIRouter()


@router.post("/", response_model=AccessLogRead)
def create_access_log(
    file: Annotated[UploadFile, File()],
    plate: Annotated[str, Form()],
    access_log_controller: Annotated[AccessLogController, Depends(get_access_log_controller)],
) -> AccessLogRead:
    """
    Registrar acesso veicular.

    Recebe a imagem e a placa detectada pelo dispositivo IoT.
    1. Valida o arquivo de imagem.
    2. Normaliza a placa.
    3. Verifica se a placa está na whitelist.
    4. Armazena a imagem.
    5. Cria um registro de log com o status (Authorized/Denied).

    Args:
        file: Arquivo de imagem do veículo
        plate: String da placa detectada pelo OCR
        access_log_controller: Controller de logs de acesso injetado via dependency injection

    Returns:
        AccessLogRead: Registro de acesso criado

    Raises:
        HTTPException: Se o arquivo for inválido ou muito grande
    """
    return access_log_controller.create_access_log(plate=plate, file=file)


@router.get("/images/{image_filename}")
def get_access_log_image(
    image_filename: str,
    access_log_controller: Annotated[AccessLogController, Depends(get_access_log_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """
    Servir imagem de acesso veicular.

    Este endpoint serve as imagens capturadas pelos dispositivos IoT.
    O acesso é restrito apenas para administradores autenticados.

    Args:
        image_filename: Nome do arquivo de imagem
        access_log_controller: Controller de logs de acesso injetado via dependency injection
        current_user: Usuário autenticado

    Returns:
        Response: Arquivo de imagem com Content-Type apropriado

    Raises:
        HTTPException: Se a imagem não for encontrada ou acesso negado
    """
    image_path = access_log_controller.get_image_path(image_filename)

    # Determinar Content-Type baseado na extensão
    content_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    content_type = content_type_map.get(
        image_path.suffix.lower(), "application/octet-stream"
    )

    # Ler e retornar o arquivo
    with image_path.open("rb") as f:
        image_data = f.read()

    return Response(content=image_data, media_type=content_type)


@router.get("/", response_model=list[AccessLogRead])
def list_access_logs(
    access_log_controller: Annotated[AccessLogController, Depends(get_access_log_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0, description="Número de registros a pular")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Número máximo de registros")] = 100,
    plate: Annotated[Optional[str], Query(description="Filtrar por placa (busca parcial)")] = None,
    status: Annotated[Optional[AccessStatus], Query(description="Filtrar por status")] = None,
    start_date: Annotated[Optional[datetime], Query(description="Data inicial (ISO 8601)")] = None,
    end_date: Annotated[Optional[datetime], Query(description="Data final (ISO 8601)")] = None,
) -> list[AccessLogRead]:
    """
    Lista registros de acesso veicular com filtros opcionais.
    
    Este endpoint permite visualizar todos os logs de acesso registrados,
    incluindo o conteúdo extraído da placa pelo OCR. Útil para análise
    e demonstração do sistema.
    
    Args:
        access_log_controller: Controller de logs de acesso injetado via dependency injection
        current_user: Usuário autenticado (requerido)
        skip: Número de registros a pular para paginação
        limit: Número máximo de registros a retornar (máximo 100)
        plate: Filtrar por placa (busca parcial, case-insensitive)
        status: Filtrar por status de acesso (Authorized/Denied)
        start_date: Data inicial para filtrar (formato ISO 8601)
        end_date: Data final para filtrar (formato ISO 8601)
        
    Returns:
        Lista de registros de acesso ordenados por timestamp (mais recente primeiro)
        
    Example:
        GET /api/v1/access_logs/?limit=10&status=Authorized
        GET /api/v1/access_logs/?plate=ABC1234
    """
    return access_log_controller.get_all(
        skip=skip,
        limit=limit,
        plate_filter=plate,
        status_filter=status,
        start_date=start_date,
        end_date=end_date,
    )
