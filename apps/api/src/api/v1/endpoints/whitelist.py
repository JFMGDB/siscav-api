"""Endpoints para gerenciamento de placas autorizadas (whitelist)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from apps.api.src.api.v1.controllers.plate_controller import PlateController
from apps.api.src.api.v1.deps import get_current_user, get_plate_controller
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.authorized_plate import (
    AuthorizedPlateCreate,
    AuthorizedPlateRead,
)

router = APIRouter()


@router.get("/", response_model=list[AuthorizedPlateRead])
def read_authorized_plates(
    plate_controller: Annotated[PlateController, Depends(get_plate_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0, description="Número de registros a pular")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Número máximo de registros")] = 100,
) -> list[AuthorizedPlateRead]:
    """
    Listar placas autorizadas.

    Retorna uma lista paginada de placas cadastradas na whitelist.
    
    **Parâmetros:**
    - skip: Número de registros para pular (paginação, mínimo 0)
    - limit: Número máximo de registros a retornar (mínimo 1, máximo 100)
    """
    return plate_controller.get_all(skip=skip, limit=limit)


@router.post("/", response_model=AuthorizedPlateRead)
def create_authorized_plate(
    plate_in: AuthorizedPlateCreate,
    plate_controller: Annotated[PlateController, Depends(get_plate_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Cadastrar nova placa autorizada.

    Adiciona uma nova placa à whitelist. A placa será normalizada automaticamente.
    """
    return plate_controller.create(plate_in)


@router.get("/{id}", response_model=AuthorizedPlateRead)
def read_authorized_plate(
    id: UUID,
    plate_controller: Annotated[PlateController, Depends(get_plate_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Obter placa autorizada por ID.

    Retorna os detalhes de uma placa específica.
    """
    return plate_controller.get_by_id(id)


@router.put("/{id}", response_model=AuthorizedPlateRead)
def update_authorized_plate(
    id: UUID,
    plate_in: AuthorizedPlateCreate,
    plate_controller: Annotated[PlateController, Depends(get_plate_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Atualizar placa autorizada.

    Atualiza os dados de uma placa existente.
    """
    return plate_controller.update(id, plate_in)


@router.delete("/{id}", response_model=AuthorizedPlateRead)
def delete_authorized_plate(
    id: UUID,
    plate_controller: Annotated[PlateController, Depends(get_plate_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Remover placa autorizada.

    Remove uma placa da whitelist.
    """
    return plate_controller.delete(id)
