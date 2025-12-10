"""Testes unitários para utilitários de placa."""

import pytest

from app.api.v1.utils.plate import normalize_plate, validate_brazilian_plate


class TestNormalizePlate:
    """Testes para função normalize_plate."""

    def test_normalize_plate_with_hyphen(self):
        """Testa normalização de placa com hífen."""
        result = normalize_plate("ABC-1234")
        assert result == "ABC1234"

    def test_normalize_plate_with_space(self):
        """Testa normalização de placa com espaço."""
        result = normalize_plate("ABC 1234")
        assert result == "ABC1234"

    def test_normalize_plate_lowercase(self):
        """Testa normalização de placa em minúsculas."""
        result = normalize_plate("abc-1234")
        assert result == "ABC1234"

    def test_normalize_plate_mercosul(self):
        """Testa normalização de placa Mercosul."""
        result = normalize_plate("ABC1D23")
        assert result == "ABC1D23"

    def test_normalize_plate_with_special_chars(self):
        """Testa normalização removendo caracteres especiais."""
        result = normalize_plate("ABC.1234")
        assert result == "ABC1234"


class TestValidateBrazilianPlate:
    """Testes para função validate_brazilian_plate."""

    def test_validate_old_format_with_hyphen(self):
        """Testa validação de formato antigo com hífen."""
        is_valid, error = validate_brazilian_plate("ABC-1234")
        assert is_valid is True
        assert error is None

    def test_validate_old_format_without_hyphen(self):
        """Testa validação de formato antigo sem hífen."""
        is_valid, error = validate_brazilian_plate("ABC1234")
        assert is_valid is True
        assert error is None

    def test_validate_mercosul_format(self):
        """Testa validação de formato Mercosul."""
        is_valid, error = validate_brazilian_plate("ABC1D23")
        assert is_valid is True
        assert error is None

    def test_validate_invalid_length(self):
        """Testa validação de placa com comprimento inválido."""
        is_valid, error = validate_brazilian_plate("ABC123")
        assert is_valid is False
        assert error is not None
        assert "7 caracteres" in error

    def test_validate_invalid_format(self):
        """Testa validação de placa com formato inválido."""
        is_valid, error = validate_brazilian_plate("INVALID")
        assert is_valid is False
        assert error is not None

    def test_validate_empty_string(self):
        """Testa validação de string vazia."""
        is_valid, error = validate_brazilian_plate("")
        assert is_valid is False
        assert error is not None

    def test_validate_normalizes_before_validation(self):
        """Testa que validação normaliza antes de validar."""
        # Placa válida com espaços/hífens deve passar
        is_valid, error = validate_brazilian_plate("ABC-1234")
        assert is_valid is True

        is_valid, error = validate_brazilian_plate("abc 1234")
        assert is_valid is True

