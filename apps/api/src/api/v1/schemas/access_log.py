from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class AccessStatus(str, Enum):
    Authorized = "Authorized"
    Denied = "Denied"


class AccessLogRead(BaseModel):
    id: UUID = Field(..., description="ID único do registro de acesso.")
    timestamp: datetime = Field(..., description="Data e hora do acesso.")
    plate_string_detected: str = Field(..., description="Texto da placa detectado pelo OCR.", example="ABC1234")
    status: AccessStatus = Field(..., description="Status do acesso (Autorizado/Negado).")
    image_storage_key: str = Field(..., description="Caminho ou chave para recuperação da imagem armazenada.")
    authorized_plate_id: UUID | None = Field(None, description="ID da placa autorizada associada, se houver.")
