"""Schemas de paginação padronizados para endpoints da API."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parâmetros de paginação para requisições."""

    skip: int = Field(default=0, ge=0, description="Número de registros a pular")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Número máximo de registros a retornar"
    )


class PaginatedResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Resposta paginada padronizada."""

    items: list[T] = Field(description="Lista de itens da página atual")
    total: int = Field(description="Total de itens disponíveis")
    skip: int = Field(description="Número de registros pulados")
    limit: int = Field(description="Número máximo de registros por página")
    has_next: bool = Field(description="Indica se há próxima página")
    has_prev: bool = Field(description="Indica se há página anterior")
