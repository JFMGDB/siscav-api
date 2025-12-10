"""Configuração de rate limiting para a aplicação."""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter global compartilhado
limiter = Limiter(key_func=get_remote_address)


