from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from apps.api.src.api.v1.utils.plate import normalize_plate, validate_brazilian_plate


class AuthorizedPlateBase(BaseModel):
    plate: str = Field(..., description="A placa do veículo (formato original).", example="ABC-1234")
    description: str | None = Field(None, description="Descrição opcional do veículo ou proprietário.", example="Carro do Diretor")

    @field_validator("plate")
    @classmethod
    def validate_plate(cls, v: str) -> str:
        """Valida o formato da placa brasileira."""
        is_valid, error_msg = validate_brazilian_plate(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class AuthorizedPlateCreate(AuthorizedPlateBase):
    """
    Schema para criação de placa autorizada.
    
    O campo normalized_plate é opcional e será calculado automaticamente
    se não fornecido.
    """
    normalized_plate: str | None = Field(
        None,
        description="Placa normalizada (calculada automaticamente se não fornecida).",
        example="ABC1234",
    )


class AuthorizedPlateRead(AuthorizedPlateBase):
    """Schema para leitura de placa autorizada."""
    id: UUID
    normalized_plate: str = Field(..., description="Placa normalizada (sempre presente na leitura).")
    created_at: datetime
    updated_at: datetime
