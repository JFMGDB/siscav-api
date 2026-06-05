from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccessStatus(str, Enum):
    Authorized = "Authorized"
    Denied = "Denied"


class AccessLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único do registro de acesso.")
    timestamp: datetime = Field(..., description="Data e hora do acesso.")
    plate_string_detected: str = Field(
        ..., description="Texto da placa detectado pelo OCR.", example="ABC1234"
    )
    status: AccessStatus = Field(..., description="Status do acesso (Autorizado/Negado).")
    image_storage_key: str = Field(
        ..., description="Caminho ou chave para recuperação da imagem armazenada."
    )
    authorized_plate_id: UUID | None = Field(
        None, description="ID da placa autorizada associada, se houver."
    )
    is_automatic: bool = Field(
        False,
        description="True quando a aprovação ocorreu sem intervenção humana (ingestão IoT).",
    )
    ocr_success: bool = Field(
        True,
        description="True quando a placa detectada segue formato brasileiro válido.",
    )


class WhitelistFromDeniedBody(BaseModel):
    description: str | None = Field(
        None,
        description="Descrição opcional ao cadastrar a placa na whitelist.",
    )


class DashboardDailyMetrics(BaseModel):
    date: date
    traffic_volume: int
    auto_approval_rate_percent: float
    ocr_success_rate_percent: float = Field(
        ...,
        description=(
            "Taxa de sucesso das tentativas OCR (POST /ml/recognize-plate) no dia, "
            "com base em placas válidas extraídas."
        ),
    )
