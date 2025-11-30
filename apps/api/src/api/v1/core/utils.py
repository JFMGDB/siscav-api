"""Funções utilitárias compartilhadas entre módulos da API."""


def normalize_plate(plate: str) -> str:
    """Normaliza uma placa de veículo para comparação.

    Remove todos os caracteres não alfanuméricos e converte para maiúsculas.
    Esta função garante consistência na normalização de placas em todo o sistema.

    Args:
        plate: String da placa como inserida pelo usuário (ex: "ABC-1234").

    Returns:
        String normalizada sem caracteres especiais e em maiúsculas (ex: "ABC1234").

    Examples:
        >>> normalize_plate("ABC-1234")
        'ABC1234'
        >>> normalize_plate("abc 1234")
        'ABC1234'
        >>> normalize_plate("XYZ.9999")
        'XYZ9999'
    """
    return "".join(c for c in plate if c.isalnum()).upper()
