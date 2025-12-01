from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from jose import jwt
from passlib.context import CryptContext

from app.api.v1.core.config import get_settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
settings = get_settings()


def _create_token(
    subject: str | UUID,
    token_type: str,
    expires_delta: timedelta | None = None,
    default_expires_delta: timedelta | None = None,
) -> str:
    """Cria um token JWT genérico.

    Função auxiliar interna para evitar duplicação de código entre
    create_access_token e create_refresh_token (princípio DRY).

    Args:
        subject: ID do usuário (UUID ou string).
        token_type: Tipo do token ("access" ou "refresh").
        expires_delta: Tempo de expiração customizado.
        default_expires_delta: Tempo de expiração padrão se expires_delta não for fornecido.

    Returns:
        Token JWT codificado como string.

    Raises:
        ValueError: Se subject for None ou vazio.
    """
    if not subject:
        error_msg = "Subject cannot be None or empty"
        raise ValueError(error_msg)

    now = datetime.now(UTC)
    # Garante que default_expires_delta não seja None antes de usar
    if expires_delta:
        expire = now + expires_delta
    elif default_expires_delta:
        expire = now + default_expires_delta
    else:
        error_msg = "Either expires_delta or default_expires_delta must be provided"
        raise ValueError(error_msg)

    # jti (JWT ID) garante unicidade mesmo quando criados no mesmo segundo
    to_encode = {
        "exp": expire,
        "iat": now,
        "sub": str(subject),
        "type": token_type,
        "jti": str(uuid4()),
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str | UUID, expires_delta: timedelta | None = None) -> str:
    """Cria um token de acesso JWT.

    Args:
        subject: ID do usuário (UUID ou string).
        expires_delta: Tempo de expiração customizado. Se None, usa o padrão das configurações.

    Returns:
        Token JWT codificado como string.

    Raises:
        ValueError: Se subject for None ou vazio.
    """
    default_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(subject, "access", expires_delta, default_expires)


def create_refresh_token(subject: str | UUID, expires_delta: timedelta | None = None) -> str:
    """Cria um token de refresh JWT.

    Args:
        subject: ID do usuário (UUID ou string).
        expires_delta: Tempo de expiração customizado. Se None, usa o padrão das configurações.

    Returns:
        Token JWT de refresh codificado como string.

    Raises:
        ValueError: Se subject for None ou vazio.
    """
    default_expires = timedelta(days=settings.refresh_token_expire_days)
    return _create_token(subject, "refresh", expires_delta, default_expires)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado.

    Args:
        plain_password: Senha em texto plano fornecida pelo usuário.
        hashed_password: Hash da senha armazenado no banco de dados.

    Returns:
        True se a senha corresponder ao hash, False caso contrário.

    Raises:
        ValueError: Se plain_password ou hashed_password forem None ou vazios.
    """
    if not plain_password:
        error_msg = "Plain password cannot be None or empty"
        raise ValueError(error_msg)
    if not hashed_password:
        error_msg = "Hashed password cannot be None or empty"
        raise ValueError(error_msg)

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha usando Argon2.

    Args:
        password: Senha em texto plano a ser hasheada.

    Returns:
        Hash da senha codificado como string.

    Raises:
        ValueError: Se password for None ou vazio.
    """
    if not password:
        error_msg = "Password cannot be None or empty"
        raise ValueError(error_msg)

    return pwd_context.hash(password)
