"""Controller for superadmin account management."""

import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core import error_messages as err
from apps.api.src.api.v1.core.security import get_password_hash
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from apps.api.src.api.v1.schemas.user import (
    PaginatedUserList,
    UserRead,
    UserStats,
    UserUpdate,
)

logger = logging.getLogger(__name__)


class UserController:
    """Superadmin user listing and lifecycle operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository

    def get_stats(self) -> UserStats:
        return UserStats(
            total_accounts=self.user_repository.count_all(self.db),
            client_admin_count=self.user_repository.count_client_admins(self.db),
            superadmin_count=self.user_repository.count_superadmins(self.db),
        )

    def list_users(self, skip: int = 0, limit: int = 100) -> PaginatedUserList:
        total = self.user_repository.count_all(self.db)
        users = self.user_repository.list_users(self.db, skip=skip, limit=limit)
        return PaginatedUserList(
            items=[UserRead.model_validate(user) for user in users],
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + len(users) < total,
            has_prev=skip > 0,
        )

    def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead:
        if data.email is None and data.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err.UPDATE_FIELD_REQUIRED,
            )

        user = self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err.USER_NOT_FOUND,
            )

        email = str(data.email) if data.email is not None else None
        if email is not None and email != user.email:
            existing = self.user_repository.get_by_email(self.db, email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=err.EMAIL_ALREADY_REGISTERED,
                )

        hashed_password = get_password_hash(data.password) if data.password is not None else None

        try:
            updated = self.user_repository.update(
                self.db,
                user_id,
                email=email,
                hashed_password=hashed_password,
            )
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=err.EMAIL_ALREADY_REGISTERED,
            ) from e

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err.USER_NOT_FOUND,
            )

        logger.info("User updated by superadmin: id=%s email=%s", user_id, updated.email)
        return UserRead.model_validate(updated)

    def delete_user(self, user_id: UUID, actor_id: UUID) -> None:
        if user_id == actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=err.CANNOT_DELETE_OWN_ACCOUNT,
            )

        user = self.user_repository.get_by_id(self.db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err.USER_NOT_FOUND,
            )

        if user.is_superadmin:
            superadmin_count = self.user_repository.count_superadmins(self.db)
            if superadmin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=err.CANNOT_DELETE_LAST_SUPERADMIN,
                )

        deleted = self.user_repository.delete(self.db, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err.USER_NOT_FOUND,
            )

        logger.info("User deleted by superadmin: id=%s email=%s", user_id, user.email)
