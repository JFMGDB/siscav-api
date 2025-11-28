from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.src.api.v1.crud import crud_authorized_plate
from apps.api.src.api.v1.db.session import get_db
from apps.api.src.api.v1.deps import get_current_user
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.authorized_plate import (
    AuthorizedPlateCreate,
    AuthorizedPlateRead,
)

router = APIRouter()


@router.get("/", response_model=list[AuthorizedPlateRead])
def read_authorized_plates(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> list[AuthorizedPlateRead]:
    """
    Retrieve authorized plates.
    """
    return crud_authorized_plate.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=AuthorizedPlateRead)
def create_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    plate_in: AuthorizedPlateCreate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Create new authorized plate.
    """
    return crud_authorized_plate.create(db, obj_in=plate_in)


@router.get("/{id}", response_model=AuthorizedPlateRead)
def read_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Get authorized plate by ID.
    """
    plate = crud_authorized_plate.get(db, id=id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    return plate


@router.put("/{id}", response_model=AuthorizedPlateRead)
def update_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    id: UUID,
    plate_in: AuthorizedPlateCreate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Update an authorized plate.
    """
    plate = crud_authorized_plate.get(db, id=id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    plate = crud_authorized_plate.update(db, db_obj=plate, obj_in=plate_in)
    return plate


@router.delete("/{id}", response_model=AuthorizedPlateRead)
def delete_authorized_plate(
    *,
    db: Annotated[Session, Depends(get_db)],
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthorizedPlateRead:
    """
    Delete an authorized plate.
    """
    plate = crud_authorized_plate.get(db, id=id)
    if not plate:
        raise HTTPException(status_code=404, detail="Plate not found")
    plate = crud_authorized_plate.remove(db, id=id)
    return plate
