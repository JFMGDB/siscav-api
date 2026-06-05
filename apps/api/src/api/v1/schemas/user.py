from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr = Field(
        ..., description="Email do usuário (usado para login).", example="admin@siscav.com.br"
    )


class UserCreate(UserBase):
    password: str = Field(
        ..., description="Senha do usuário (será hasheada antes de salvar).", min_length=8
    )


class UserRead(UserBase):
    id: UUID
    is_admin: bool = Field(
        ..., description="Operational administrator privileges for the client context."
    )
    is_superadmin: bool = Field(
        ..., description="Siscav system superadministrator privileges."
    )
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(
        default=None,
        description="New email address (must remain unique).",
    )
    password: str | None = Field(
        default=None,
        description="New password (min 8 characters, will be hashed).",
        min_length=8,
    )


class UserStats(BaseModel):
    total_accounts: int
    client_admin_count: int
    superadmin_count: int


class PaginatedUserList(BaseModel):
    items: list[UserRead]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
