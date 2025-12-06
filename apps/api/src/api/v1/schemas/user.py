from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email do usuário (usado para login).", example="admin@siscav.com.br")


class UserCreate(UserBase):
    password: str = Field(..., description="Senha do usuário (será hasheada antes de salvar).", min_length=8)


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
