"""Funções utilitárias compartilhadas entre módulos da API."""

import re

# Constante para o código ASCII do espaço (primeiro caractere imprimível)
# Usado na sanitização de texto para filtrar caracteres de controle
_ASCII_SPACE = 32


def validate_plate_format(plate: str) -> bool:
    """Valida o formato de uma placa de veículo brasileira.

    Suporta dois formatos:
    - Formato antigo: ABC-1234 (3 letras, hífen, 4 dígitos)
    - Formato Mercosul: ABC1D23 (3 letras, 1 dígito, 1 letra, 2 dígitos)

    Args:
        plate: String da placa a ser validada.

    Returns:
        True se a placa estiver em formato válido, False caso contrário.

    Examples:
        >>> validate_plate_format("ABC-1234")
        True
        >>> validate_plate_format("ABC1D23")
        True
        >>> validate_plate_format("ABC1234")
        False
        >>> validate_plate_format("INVALID")
        False
    """
    if not plate:
        return False

    # Remove espaços e converte para maiúsculas
    plate_clean = plate.strip().upper()

    # Formato antigo: ABC-1234
    pattern_old = r"^[A-Z]{3}-[0-9]{4}$"
    # Formato Mercosul: ABC1D23
    pattern_mercosul = r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$"

    return bool(re.match(pattern_old, plate_clean) or re.match(pattern_mercosul, plate_clean))


def normalize_plate(plate: str) -> str:
    """Normaliza uma placa de veículo para comparação.

    Remove todos os caracteres não alfanuméricos e converte para maiúsculas.
    Esta função garante consistência na normalização de placas em todo o sistema.

    Args:
        plate: String da placa como inserida pelo usuário (ex: "ABC-1234").

    Returns:
        String normalizada sem caracteres especiais e em maiúsculas (ex: "ABC1234").

    Raises:
        ValueError: Se a placa for vazia ou None, ou se resultar em string vazia após normalização.

    Examples:
        >>> normalize_plate("ABC-1234")
        'ABC1234'
        >>> normalize_plate("abc 1234")
        'ABC1234'
        >>> normalize_plate("XYZ.9999")
        'XYZ9999'
        >>> normalize_plate("ABC1D23")
        'ABC1D23'
    """
    if not plate:
        error_msg = "Plate cannot be empty"
        raise ValueError(error_msg)

    normalized = "".join(c for c in plate if c.isalnum()).upper()

    if not normalized:
        error_msg = "Plate cannot be empty after normalization"
        raise ValueError(error_msg)

    return normalized


def sanitize_text(text: str, max_length: int | None = None) -> str:
    """Sanitiza texto de entrada para prevenir XSS e outros ataques.

    Remove caracteres de controle perigosos e limita o comprimento.
    Nota: Esta função NÃO escapa HTML porque FastAPI/Pydantic já fazem isso
    automaticamente em respostas JSON. Escapar aqui causaria dupla codificação.

    Args:
        text: String de texto a ser sanitizada.
        max_length: Comprimento máximo permitido. Se None, não limita o tamanho.

    Returns:
        String sanitizada com caracteres de controle removidos.

    Examples:
        >>> sanitize_text("Texto normal")
        "Texto normal"
        >>> sanitize_text("Texto\\x00com\\x01controle", max_length=10)
        "Textocomcon"
        >>> sanitize_text("Texto muito longo", max_length=10)
        "Texto muit"
    """
    if not text:
        return ""

    # Remove caracteres de controle (exceto quebras de linha e tabs)
    # Mantém apenas caracteres imprimíveis e alguns caracteres de controle seguros
    sanitized = "".join(
        char for char in text if ord(char) >= _ASCII_SPACE or char in ("\n", "\r", "\t")
    )

    # Limita o comprimento se especificado
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()
