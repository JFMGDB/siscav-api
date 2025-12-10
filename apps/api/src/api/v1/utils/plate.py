"""Utilitários para normalização e validação de placas veiculares."""

import re
from typing import Optional


def normalize_plate(plate: str) -> str:
    """
    Normaliza uma placa veicular removendo caracteres especiais e convertendo para maiúsculas.
    
    Esta função garante consistência na comparação de placas, removendo hífens,
    espaços e outros caracteres não alfanuméricos.
    
    Args:
        plate: String da placa no formato original (ex: "ABC-1234", "abc 1234")
        
    Returns:
        String normalizada (ex: "ABC1234")
        
    Examples:
        >>> normalize_plate("ABC-1234")
        'ABC1234'
        >>> normalize_plate("abc 1234")
        'ABC1234'
        >>> normalize_plate("XYZ9A12")
        'XYZ9A12'
    """
    return "".join(c for c in plate if c.isalnum()).upper()


def validate_brazilian_plate(plate: str) -> tuple[bool, Optional[str]]:
    """
    Valida se uma placa segue o formato brasileiro (Mercosul ou antigo).
    
    Formatos aceitos:
    - Antigo: 3 letras + 4 dígitos (ex: ABC1234)
    - Mercosul: 3 letras + 1 dígito + 1 letra + 2 dígitos (ex: ABC1D23)
    
    Args:
        plate: String da placa (pode conter hífens ou espaços)
        
    Returns:
        Tupla (is_valid, error_message)
        - is_valid: True se a placa é válida
        - error_message: Mensagem de erro se inválida, None se válida
        
    Examples:
        >>> validate_brazilian_plate("ABC-1234")
        (True, None)
        >>> validate_brazilian_plate("ABC1D23")
        (True, None)
        >>> validate_brazilian_plate("ABC123")
        (False, 'Placa deve ter 7 caracteres alfanuméricos')
    """
    normalized = normalize_plate(plate)
    
    if len(normalized) != 7:
        return False, "Placa deve ter 7 caracteres alfanuméricos"
    
    # Formato antigo: 3 letras + 4 dígitos
    old_format = re.match(r"^[A-Z]{3}\d{4}$", normalized)
    
    # Formato Mercosul: 3 letras + 1 dígito + 1 letra + 2 dígitos
    mercosul_format = re.match(r"^[A-Z]{3}\d[A-Z]\d{2}$", normalized)
    
    if old_format or mercosul_format:
        return True, None
    
    return False, "Placa não segue o formato brasileiro (ABC1234 ou ABC1D23)"

