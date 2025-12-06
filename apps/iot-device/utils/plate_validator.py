"""Utilitários para validação de placas veiculares brasileiras."""

import re
from typing import Tuple


def normalize_plate(plate: str) -> str:
    """
    Normaliza uma placa removendo caracteres especiais e convertendo para maiúsculas.

    Args:
        plate: String da placa

    Returns:
        Placa normalizada
    """
    return "".join(c for c in plate if c.isalnum()).upper()


def validate_brazilian_plate(plate: str) -> Tuple[bool, str]:
    """
    Valida se uma placa segue o formato brasileiro.

    Formatos aceitos:
    - Antigo: 3 letras + 4 dígitos (ex: ABC1234)
    - Mercosul: 3 letras + 1 dígito + 1 letra + 2 dígitos (ex: ABC1D23)

    Args:
        plate: String da placa (pode conter hífens ou espaços)

    Returns:
        Tupla (is_valid, normalized_plate)
    """
    normalized = normalize_plate(plate)

    if len(normalized) != 7:
        return False, normalized

    # Formato antigo: 3 letras + 4 dígitos
    old_format = re.match(r"^[A-Z]{3}\d{4}$", normalized)

    # Formato Mercosul: 3 letras + 1 dígito + 1 letra + 2 dígitos
    mercosul_format = re.match(r"^[A-Z]{3}\d[A-Z]\d{2}$", normalized)

    if old_format or mercosul_format:
        return True, normalized

    return False, normalized













