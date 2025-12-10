"""Testes unitários para módulo de segurança."""

from datetime import timedelta

import pytest

from apps.api.src.api.v1.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Testes para hash e verificação de senhas."""

    def test_hash_password(self):
        """Testa que uma senha é hasheada corretamente."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_different_passwords_produce_different_hashes(self):
        """Testa que senhas diferentes produzem hashes diferentes."""
        password1 = "password1"
        password2 = "password2"
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        assert hash1 != hash2

    def test_hash_same_password_produces_different_hashes(self):
        """Testa que a mesma senha produz hashes diferentes (salt)."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Testa verificação de senha correta."""
        password = "correct_password"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Testa verificação de senha incorreta."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Testa verificação de senha vazia."""
        password = "some_password"
        hashed = get_password_hash(password)
        assert verify_password("", hashed) is False


class TestAccessToken:
    """Testes para criação de tokens de acesso."""

    def test_create_access_token(self):
        """Testa criação de token de acesso."""
        subject = "test_user_id"
        token = create_access_token(subject)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Testa criação de token com expiração customizada."""
        subject = "test_user_id"
        expires_delta = timedelta(minutes=30)
        token = create_access_token(subject, expires_delta=expires_delta)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_different_subjects(self):
        """Testa que tokens para diferentes subjects são diferentes."""
        subject1 = "user1"
        subject2 = "user2"
        token1 = create_access_token(subject1)
        token2 = create_access_token(subject2)
        assert token1 != token2

    def test_create_access_token_uuid_subject(self):
        """Testa criação de token com UUID como subject."""
        from uuid import uuid4

        subject = str(uuid4())
        token = create_access_token(subject)
        assert isinstance(token, str)
        assert len(token) > 0

