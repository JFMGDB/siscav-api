"""Translate Pydantic/FastAPI validation error messages to pt-BR."""

_PYDANTIC_TYPE_MSG: dict[str, str] = {
    "missing": "Campo obrigatório ausente.",
    "string_type": "Informe um texto válido.",
    "string_too_short": "Texto muito curto.",
    "string_too_long": "Texto muito longo.",
    "value_error.email": "Informe um e-mail válido.",
    "value_error": "Valor inválido.",
    "int_parsing": "Informe um número inteiro válido.",
    "float_parsing": "Informe um número válido.",
    "uuid_parsing": "Identificador inválido.",
    "enum": "Valor não permitido.",
    "greater_than_equal": "Valor abaixo do mínimo permitido.",
    "less_than_equal": "Valor acima do máximo permitido.",
}


def translate_validation_msg(msg: str, error_type: str) -> str:
    """Return pt-BR message for a Pydantic validation error."""
    if error_type in _PYDANTIC_TYPE_MSG:
        return _PYDANTIC_TYPE_MSG[error_type]
    if error_type.startswith("value_error."):
        return "Valor inválido."
    if "at least" in msg.lower() and "character" in msg.lower():
        return "Texto muito curto."
    if "valid email" in msg.lower():
        return "Informe um e-mail válido."
    return "Valor inválido."


def translate_validation_errors(errors: list[dict]) -> list[dict]:
    """Copy validation errors with translated msg fields."""
    translated: list[dict] = []
    for err in errors:
        item = dict(err)
        err_type = str(item.get("type", ""))
        msg = str(item.get("msg", ""))
        item["msg"] = translate_validation_msg(msg, err_type)
        translated.append(item)
    return translated
