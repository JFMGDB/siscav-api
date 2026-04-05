"""Controller para lógica de negócio de autenticação."""

import logging
from datetime import timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from apps.api.src.api.v1.core.config import get_settings
from apps.api.src.api.v1.core.security import (
    create_access_token,
    create_password_reset_token,
    get_password_hash,
    verify_password,
)
from apps.api.src.api.v1.models.user import User
from apps.api.src.api.v1.repositories.user_repository import UserRepository
from apps.api.src.api.v1.schemas.token import TokenPayload
from apps.api.src.api.v1.schemas.user import UserCreate, UserRead

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

    def register_user(self, user_data: UserCreate) -> UserRead:
        """
        Registra um novo usuário no sistema.

        Args:
            user_data: Dados do novo usuário (email e senha)

        Returns:
            UserRead: Dados do usuário criado (sem senha)

        Raises:
            HTTPException: Se o email já estiver em uso ou ocorrer erro
        """
        logger.info(f"Tentativa de registro de novo usuário: {user_data.email}")

        # Verificar se o email já existe
        existing_user = self.user_repository.get_by_email(self.db, user_data.email)
        if existing_user:
            logger.warning(f"Tentativa de registro com email já existente: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Hash da senha
        hashed_password = get_password_hash(user_data.password)

        # Criar usuário
        try:
            user = self.user_repository.create(
                self.db, user_data=user_data, hashed_password=hashed_password
            )
            logger.info(f"Usuário registrado com sucesso: {user_data.email} (ID: {user.id})")
            return UserRead.model_validate(user)
        except IntegrityError as e:
            # Violação de constraint (ex: email duplicado)
            self.db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
            logger.warning(
                f"Tentativa de registro com email duplicado ou constraint violada: {user_data.email} - {error_msg}"
            )

            # Verificar se é erro de email duplicado
            if (
                "email" in error_msg.lower()
                or "unique" in error_msg.lower()
                or "UNIQUE constraint" in error_msg
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                ) from e

            # Outra violação de constraint
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data provided",
            ) from e
        except ValidationError as e:
            # Erro de validação do Pydantic
            self.db.rollback()
            error_details = "; ".join([f"{err['loc']}: {err['msg']}" for err in e.errors()])
            logger.warning(
                f"Erro de validação ao registrar usuário: {user_data.email} - {error_details}"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {error_details}",
            ) from e
        except SQLAlchemyError as e:
            # Erros do SQLAlchemy (conexão, etc.)
            self.db.rollback()
            error_msg = str(e)
            logger.error(
                f"Erro de banco de dados ao registrar usuário: {user_data.email} - {error_msg}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating user",
            ) from e
        except Exception as e:
            # Outros erros inesperados
            self.db.rollback()
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(
                f"Erro inesperado ao registrar usuário: {user_data.email} - {error_type}: {error_msg}",
                exc_info=True,
            )
            # Retornar mensagem mais específica para ajudar no debug
            detail_msg = f"Error creating user: {error_type}"
            if "uuid" in error_msg.lower() or "guid" in error_msg.lower():
                detail_msg = "Database configuration error: UUID type not supported. Please check database setup."
            elif "connection" in error_msg.lower() or "connect" in error_msg.lower():
                detail_msg = "Database connection error. Please check database configuration."
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail_msg,
            ) from e

    def request_password_reset(self, email: str) -> tuple[str | None, str]:
        """Gera token de reset se o email existir. Resposta pública é sempre genérica.

        Returns:
            Tupla (token_jwt ou None, mensagem pública idêntica para existir ou não o email).
        """
        msg = (
            "If an account exists for this email, password reset instructions "
            "have been issued."
        )
        normalized = email.strip()
        user = self.user_repository.get_by_email(self.db, normalized)
        if not user:
            logger.info("Password reset requested for unknown email (no token issued)")
            return None, msg
        delta = timedelta(minutes=settings.password_reset_token_expire_minutes)
        token = create_password_reset_token(user.id, expires_delta=delta)
        logger.info("Password reset token issued for user id=%s", user.id)
        return token, msg

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        """Valida JWT `password_reset` e atualiza a senha."""
        if not token or not token.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token cannot be empty",
            )
        try:
            payload = jwt.decode(
                token.strip(), settings.secret_key, algorithms=[settings.algorithm]
            )
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired reset token",
            ) from e
        if token_data.type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
        if not token_data.sub:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid reset token",
            )
        try:
            user_id = UUID(token_data.sub)
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user in reset token",
            ) from e
        hashed = get_password_hash(new_password)
        updated = self.user_repository.update_password_hash(self.db, user_id, hashed)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        logger.info("Password reset completed for user id=%s", user_id)

