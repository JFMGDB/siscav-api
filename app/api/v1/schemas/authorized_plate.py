from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.api.v1.core.utils import sanitize_text, validate_plate_format


class AuthorizedPlateBase(BaseModel):
    plate: str
    description: str | None = None

    @field_validator("plate")
    @classmethod
    def validate_plate_format(cls, v: str) -> str:
        """Valida o formato da placa brasileira."""
        if not validate_plate_format(v):
            error_msg = (
                "Formato de placa inválido. Use o formato antigo (ABC-1234) ou Mercosul (ABC1D23)"
            )
            raise ValueError(error_msg)
        return v.upper().strip()

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """Sanitiza o campo description para prevenir XSS."""
        if v is None:
            return None
        # Limita description a 500 caracteres (tamanho razoável para descrição)
        return sanitize_text(v, max_length=500) if v else None


class AuthorizedPlateCreate(AuthorizedPlateBase):
    """Schema para criação de placa autorizada.

    O campo normalized_plate é calculado automaticamente no endpoint/CRUD
    a partir do campo plate. Não deve ser fornecido pelo cliente.
    """


class AuthorizedPlateRead(AuthorizedPlateBase):
    id: UUID
    normalized_plate: str
    created_at: datetime
    updated_at: datetime
