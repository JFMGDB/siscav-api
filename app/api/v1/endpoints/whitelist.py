from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.core.utils import normalize_plate
from app.api.v1.crud import crud_authorized_plate
from app.api.v1.db.session import get_db
from app.api.v1.deps import get_current_user
from app.api.v1.models.authorized_plate import AuthorizedPlate
from app.api.v1.models.user import User
from app.api.v1.schemas.authorized_plate import (
    AuthorizedPlateCreate,
    AuthorizedPlateRead,
)
from app.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()


def get_plate_or_404(db: Session, id: UUID) -> AuthorizedPlate:
    """Obtém uma placa autorizada por ID ou retorna 404 se não encontrada.

    Helper para evitar duplicação de código seguindo o princípio DRY.
    """
    plate = crud_authorized_plate.get(db, id=id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    return plate


@router.get("/", response_model=PaginatedResponse[AuthorizedPlateRead])
def read_authorized_plates(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001
    skip: int = Query(default=0, ge=0, description="Número de registros a pular"),
    limit: int = Query(default=100, ge=1, le=1000, description="Número máximo de registros"),
) -> PaginatedResponse[AuthorizedPlateRead]:
    """
    Lista placas autorizadas com paginação.

    Retorna uma lista paginada de placas autorizadas com metadados de paginação.
    """
    plates = crud_authorized_plate.get_multi(db, skip=skip, limit=limit)
    total = crud_authorized_plate.count(db)

    items = [AuthorizedPlateRead.model_validate(plate, from_attributes=True) for plate in plates]

    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.post("/", response_model=AuthorizedPlateRead)
def create_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    plate_in: AuthorizedPlateCreate,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001
) -> AuthorizedPlateRead:
    """
    Cria uma nova placa autorizada.

    Adiciona uma placa à whitelist de veículos autorizados.
    A placa é normalizada automaticamente antes de ser salva.
    """
    # Normaliza a placa antes de criar
    # A função normalize_plate valida se a placa é vazia e levanta ValueError
    try:
        normalized_plate = normalize_plate(plate_in.plate)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    try:
        plate = crud_authorized_plate.create(db, obj_in=plate_in, normalized_plate=normalized_plate)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return AuthorizedPlateRead.model_validate(plate, from_attributes=True)


@router.get("/{id}", response_model=AuthorizedPlateRead)
def read_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001
) -> AuthorizedPlateRead:
    """
    Obtém uma placa autorizada por ID.

    Retorna os detalhes de uma placa específica da whitelist.
    """
    plate = get_plate_or_404(db, id)
    return AuthorizedPlateRead.model_validate(plate, from_attributes=True)


@router.put("/{id}", response_model=AuthorizedPlateRead)
def update_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    id: UUID,
    plate_in: AuthorizedPlateCreate,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001
) -> AuthorizedPlateRead:
    """
    Atualiza uma placa autorizada.

    Modifica os dados de uma placa existente na whitelist.
    A placa é normalizada automaticamente antes de ser atualizada.
    """
    plate = get_plate_or_404(db, id)

    # Normaliza a placa antes de atualizar
    # A função normalize_plate valida se a placa é vazia e levanta ValueError
    try:
        normalized_plate = normalize_plate(plate_in.plate)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    try:
        updated_plate = crud_authorized_plate.update(
            db, db_obj=plate, obj_in=plate_in, normalized_plate=normalized_plate
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return AuthorizedPlateRead.model_validate(updated_plate, from_attributes=True)


@router.delete("/{id}", response_model=AuthorizedPlateRead)
def delete_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],  # noqa: ARG001
) -> AuthorizedPlateRead:
    """
    Remove uma placa autorizada.

    Remove uma placa da whitelist de veículos autorizados.
    """
    plate = get_plate_or_404(db, id)
    # Cria resposta antes de deletar para evitar race condition
    response = AuthorizedPlateRead.model_validate(plate, from_attributes=True)
    db.delete(plate)
    db.commit()
    return response
