from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuthorizedPlateBase(BaseModel):
    plate: str
    normalized_plate: str
    description: str | None = None


class AuthorizedPlateCreate(AuthorizedPlateBase):
    pass


class AuthorizedPlateRead(AuthorizedPlateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


