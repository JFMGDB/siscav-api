"""Testes unitários para funções de segurança."""

from datetime import timedelta
from uuid import uuid4

import pytest

from app.api.v1.core.config import get_settings
from app.api.v1.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)

settings = get_settings()


class TestPasswordHashing:
    """Testes para hashing e verificação de senhas."""

    def test_hash_password(self):
        """Testa que hash de senha é gerado corretamente."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$argon2")

    def test_verify_password_correct(self):
        """Testa verificação de senha correta."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Testa verificação de senha incorreta."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_different_passwords_different_hashes(self):
        """Testa que senhas diferentes geram hashes diferentes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_hash_same_password_different_hashes(self):
        """Testa que mesma senha gera hashes diferentes (salt)."""
        password = "same_password"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes devem ser diferentes devido ao salt
        assert hash1 != hash2
        # Mas ambos devem verificar a mesma senha
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestAccessToken:
    """Testes para criação e validação de tokens JWT."""

    def test_create_access_token(self):
        """Testa criação de token de acesso."""
        user_id = uuid4()
        token = create_access_token(str(user_id))

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_uuid(self):
        """Testa criação de token com UUID diretamente."""
        user_id = uuid4()
        token = create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_create_access_token_with_expires_delta(self):
        """Testa criação de token com tempo de expiração customizado."""
        user_id = uuid4()
        expires_delta = timedelta(minutes=30)
        token = create_access_token(user_id, expires_delta=expires_delta)

        assert token is not None
        assert isinstance(token, str)

    def test_create_access_token_different_users_different_tokens(self):
        """Testa que usuários diferentes geram tokens diferentes."""
        user_id1 = uuid4()
        user_id2 = uuid4()

        token1 = create_access_token(user_id1)
        token2 = create_access_token(user_id2)

        assert token1 != token2

    def test_create_access_token_same_user_same_expiration(self):
        """Testa que tokens com mesmo payload e expiração são sempre diferentes devido ao jti."""
        user_id = uuid4()
        expires_delta = timedelta(minutes=15)

        # Tokens criados com mesmo usuário e mesma expiração são sempre diferentes
        # devido ao campo jti (JWT ID) que usa uuid4() para garantir unicidade
        token1 = create_access_token(user_id, expires_delta=expires_delta)
        token2 = create_access_token(user_id, expires_delta=expires_delta)

        # Tokens devem ser diferentes devido ao jti único
        assert token1 != token2
        assert token1 is not None
        assert token2 is not None
        assert isinstance(token1, str)
        assert isinstance(token2, str)


class TestRefreshToken:
    """Testes para criação de tokens de refresh."""

    def test_create_refresh_token(self):
        """Testa criação de token de refresh."""
        user_id = uuid4()
        token = create_refresh_token(str(user_id))

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_with_uuid(self):
        """Testa criação de token de refresh com UUID diretamente."""
        user_id = uuid4()
        token = create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token_with_expires_delta(self):
        """Testa criação de token de refresh com tempo de expiração customizado."""
        user_id = uuid4()
        expires_delta = timedelta(days=7)
        token = create_refresh_token(user_id, expires_delta=expires_delta)

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token_different_users_different_tokens(self):
        """Testa que usuários diferentes geram tokens de refresh diferentes."""
        user_id1 = uuid4()
        user_id2 = uuid4()

        token1 = create_refresh_token(user_id1)
        token2 = create_refresh_token(user_id2)

        assert token1 != token2

    def test_create_refresh_token_empty_subject_raises(self):
        """Testa que subject vazio levanta ValueError."""
        with pytest.raises(ValueError, match="cannot be None or empty"):
            create_refresh_token("")

        with pytest.raises(ValueError, match="cannot be None or empty"):
            create_refresh_token(None)  # type: ignore[arg-type]

    def test_create_access_token_empty_subject_raises(self):
        """Testa que create_access_token com subject vazio levanta ValueError."""
        with pytest.raises(ValueError, match="cannot be None or empty"):
            create_access_token("")

        with pytest.raises(ValueError, match="cannot be None or empty"):
            create_access_token(None)  # type: ignore[arg-type]
