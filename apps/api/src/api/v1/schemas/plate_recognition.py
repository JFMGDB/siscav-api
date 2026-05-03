"""Schemas para OCR de placas (rota /ml/recognize-plate)."""

from pydantic import BaseModel, Field


class PlateRecognizeItem(BaseModel):
    """Uma placa candidata devolvida pelo pipeline OpenCV + EasyOCR."""

    plate_raw: str = Field(description="Texto OCR (7 caracteres alfanuméricos, sem normalizar)")
    normalized_plate: str = Field(description="Valor após normalize_plate() para comparar com whitelist")
    plate_color_hint: str = Field(
        description="Heurística de cor de fundo da região: branca, amarela, cinza, desconhecida"
    )


class PlateRecognizeResponse(BaseModel):
    candidates: list[PlateRecognizeItem] = Field(
        default_factory=list,
        description="Lista de candidatos únicos encontrados no frame (pode estar vazia)",
    )
