"""Configuração de rate limiting para endpoints da API."""

import os
from collections.abc import Callable
from functools import wraps
from typing import Any

from slowapi import Limiter
from slowapi.util import get_remote_address

# Instância global do limiter
# Usa MemoryStorage para garantir isolamento em testes
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


def _is_testing() -> bool:
    """Verifica se está em modo de teste.

    Verifica a variável de ambiente no momento da execução,
    não no momento da importação do módulo.
    """
    return os.getenv("TESTING") == "true"


def rate_limit(limit: str):
    """Decorator condicional para rate limiting.

    Aplica rate limiting apenas quando não estiver em modo de teste.
    Em ambiente de testes, retorna a função original sem aplicar limites.

    Args:
        limit: String de limite no formato do slowapi (ex: "5/minute").

    Returns:
        Decorator que aplica rate limiting condicionalmente.
    """

    def decorator(func: Callable) -> Callable:
        # Aplica o rate limiting do slowapi
        rate_limited_func = limiter.limit(limit)(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Verifica no momento da execução se está em modo de teste
            # Se estiver, chama a função original sem rate limiting
            if _is_testing():
                return func(*args, **kwargs)

            # Em produção, usa a função com rate limiting
            return rate_limited_func(*args, **kwargs)

        return wrapper

    return decorator
