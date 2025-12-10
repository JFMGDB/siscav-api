"""Testes unitários para utilitários de placas veiculares."""

import pytest

from apps.api.src.api.v1.utils.plate import normalize_plate, validate_brazilian_plate


class TestNormalizePlate:
    """Testes para a função normalize_plate."""

    def test_normalize_plate_with_hyphen(self):
        """Testa normalização de placa com hífen."""
        assert normalize_plate("ABC-1234") == "ABC1234"

    def test_normalize_plate_with_space(self):
        """Testa normalização de placa com espaço."""
        assert normalize_plate("abc 1234") == "ABC1234"

    def test_normalize_plate_mercosul_format(self):
        """Testa normalização de placa no formato Mercosul."""
        assert normalize_plate("ABC1D23") == "ABC1D23"

    def test_normalize_plate_already_normalized(self):
        """Testa normalização de placa já normalizada."""
        assert normalize_plate("XYZ9A12") == "XYZ9A12"

    def test_normalize_plate_lowercase(self):
        """Testa normalização de placa em minúsculas."""
        assert normalize_plate("abc1234") == "ABC1234"

    def test_normalize_plate_mixed_case(self):
        """Testa normalização de placa com maiúsculas e minúsculas."""
        assert normalize_plate("AbC-1234") == "ABC1234"

    def test_normalize_plate_removes_special_chars(self):
        """Testa que caracteres especiais são removidos."""
        assert normalize_plate("ABC@#$1234") == "ABC1234"


class TestValidateBrazilianPlate:
    """Testes para a função validate_brazilian_plate."""

    def test_validate_old_format_with_hyphen(self):
        """Testa validação de placa no formato antigo com hífen."""
        is_valid, error = validate_brazilian_plate("ABC-1234")
        assert is_valid is True
        assert error is None

    def test_validate_old_format_without_hyphen(self):
        """Testa validação de placa no formato antigo sem hífen."""
        is_valid, error = validate_brazilian_plate("ABC1234")
        assert is_valid is True
        assert error is None

    def test_validate_mercosul_format(self):
        """Testa validação de placa no formato Mercosul."""
        is_valid, error = validate_brazilian_plate("ABC1D23")
        assert is_valid is True
        assert error is None

    def test_validate_mercosul_format_with_hyphen(self):
        """Testa validação de placa Mercosul com hífen."""
        is_valid, error = validate_brazilian_plate("ABC-1D23")
        assert is_valid is True
        assert error is None

    def test_validate_invalid_length_short(self):
        """Testa validação de placa com tamanho insuficiente."""
        is_valid, error = validate_brazilian_plate("ABC123")
        assert is_valid is False
        assert "7 caracteres" in error

    def test_validate_invalid_length_long(self):
        """Testa validação de placa com tamanho excessivo."""
        is_valid, error = validate_brazilian_plate("ABC12345")
        assert is_valid is False
        assert "7 caracteres" in error

    def test_validate_invalid_format(self):
        """Testa validação de placa com formato inválido."""
        is_valid, error = validate_brazilian_plate("1234ABC")
        assert is_valid is False
        assert "formato brasileiro" in error

    def test_validate_empty_string(self):
        """Testa validação de string vazia."""
        is_valid, error = validate_brazilian_plate("")
        assert is_valid is False
        assert "7 caracteres" in error

    def test_validate_with_special_chars(self):
        """Testa validação de placa com caracteres especiais (após normalização)."""
        is_valid, error = validate_brazilian_plate("ABC-1234")
        assert is_valid is True
        assert error is None
