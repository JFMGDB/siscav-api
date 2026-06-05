"""Superadmin account management endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from apps.api.src.api.v1.controllers.user_controller import UserController
from apps.api.src.api.v1.deps import get_current_superadmin_user, get_user_controller
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.schemas.user import PaginatedUserList, UserRead, UserStats, UserUpdate

router = APIRouter()


@router.get("/stats", response_model=UserStats)
def read_user_stats(
    user_controller: Annotated[UserController, Depends(get_user_controller)],
    _current_user: Annotated[User, Depends(get_current_superadmin_user)],
) -> UserStats:
    """Global account counters for the superadmin hub."""
    return user_controller.get_stats()


@router.get("/", response_model=PaginatedUserList)
def read_users(
    user_controller: Annotated[UserController, Depends(get_user_controller)],
    _current_user: Annotated[User, Depends(get_current_superadmin_user)],
    skip: Annotated[
        int,
        Query(ge=0, description="Records to skip (pagination). Default 0."),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Max records returned. Default 100."),
    ] = 100,
) -> PaginatedUserList:
    """Paginated list of all accounts (superadmin only)."""
    return user_controller.list_users(skip=skip, limit=limit)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    body: UserUpdate,
    user_controller: Annotated[UserController, Depends(get_user_controller)],
    _current_user: Annotated[User, Depends(get_current_superadmin_user)],
) -> UserRead:
    """Update a client admin email and/or password (roles are immutable via API)."""
    return user_controller.update_user(user_id, body)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    user_controller: Annotated[UserController, Depends(get_user_controller)],
    current_user: Annotated[User, Depends(get_current_superadmin_user)],
) -> None:
    """Delete a client admin account. Cannot delete self or the last superadmin."""
    user_controller.delete_user(user_id, current_user.id)
