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
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="Registros a pular (paginação). Padrão 0; mínimo 0.",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Máximo de registros retornados. Padrão 100; entre 1 e 100.",
        ),
    ] = 100,
) -> list[AuthorizedPlateRead]:
    """
    Listar placas autorizadas.

    Requer `Authorization: Bearer` com JWT de utilizador autenticado.

    Retorna uma lista paginada de placas cadastradas na whitelist.
    **Paginação:** `skip` ≥ 0 (padrão 0), `limit` entre 1 e 100 (padrão 100).
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

    Requer `Authorization: Bearer` com JWT de utilizador autenticado.

    O corpo segue **`AuthorizedPlateCreate`**: validação com `validate_brazilian_plate`
    (Mercosul, ex. `ABC1D23`, e legado três letras + quatro dígitos, ex. `ABC-1234`).
    A placa é normalizada para `normalized_plate` (única na whitelist).

    Se já existir outro registo com o mesmo `normalized_plate`, a API responde **409 Conflict**
    com detalhe **`Plate already exists in whitelist`**.
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

    Requer `Authorization: Bearer` com JWT de utilizador autenticado.

    Mesma validação que **POST /** (`AuthorizedPlateCreate`, Mercosul ou legado).
    Se a nova placa normalizada colidir com **outro** ID, resposta **409 Conflict** com
    **`Plate already exists in whitelist`**. ID inexistente → **404**.
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
