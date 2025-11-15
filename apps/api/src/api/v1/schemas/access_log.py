from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class AccessStatus(str, Enum):
    Authorized = "Authorized"
    Denied = "Denied"


class AccessLogRead(BaseModel):
    id: UUID
    timestamp: datetime
    plate_string_detected: str
    status: AccessStatus
    image_storage_key: str
    authorized_plate_id: UUID | None = None
