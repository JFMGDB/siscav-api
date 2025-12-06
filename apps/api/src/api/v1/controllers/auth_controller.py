"""Controller para lógica de negócio de autenticação."""

import logging
from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.security import create_access_token, verify_password
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository

settings = get_settings()
logger = logging.getLogger(__name__)


class AuthController:
    """Controller para operações de autenticação."""

    def __init__(self, db: Session):
        """
        Inicializa o controller com uma sessão do banco de dados.

        Args:
            db: Sessão do banco de dados
        """
        self.db = db
        # Repositories são classes com métodos estáticos, não requerem instanciação
        self.user_repository = UserRepository

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Autentica um usuário com email e senha.

        Args:
            email: Email do usuário
            password: Senha em texto plano

        Returns:
            User se autenticação bem-sucedida, None caso contrário
        """
        logger.debug(f"Tentativa de autenticação para email: {email}")
        user = self.user_repository.get_by_email(self.db, email)
        if not user:
            logger.warning(f"Tentativa de login com email não encontrado: {email}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Senha incorreta para email: {email}")
            return None

        logger.info(f"Autenticação bem-sucedida para usuário: {email} (ID: {user.id})")
        return user

    def create_access_token_for_user(self, user: User) -> str:
        """
        Cria um token de acesso JWT para um usuário.

        Args:
            user: Usuário autenticado

        Returns:
            Token JWT de acesso
        """
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        return create_access_token(user.id, expires_delta=access_token_expires)

