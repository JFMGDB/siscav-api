"""Utilitários compartilhados.

Este módulo contém funções utilitárias reutilizáveis em toda a aplicação.
"""

from apps.api.src.api.v1.utils.plate import (
    normalize_plate,
    validate_brazilian_plate,
)

__all__ = [
    "normalize_plate",
    "validate_brazilian_plate",
]
