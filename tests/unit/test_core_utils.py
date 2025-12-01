"""Testes unitários para funções utilitárias."""

import pytest

from app.api.v1.core.utils import normalize_plate, sanitize_text, validate_plate_format


class TestValidatePlateFormat:
    """Testes para validação de formato de placa brasileira."""

    def test_validate_old_format_valid(self):
        """Testa validação de placa no formato antigo válida."""
        assert validate_plate_format("ABC-1234") is True
        assert validate_plate_format("XYZ-9999") is True

    def test_validate_mercosul_format_valid(self):
        """Testa validação de placa no formato Mercosul válida."""
        assert validate_plate_format("ABC1D23") is True
        assert validate_plate_format("XYZ9Z99") is True

    def test_validate_old_format_case_insensitive(self):
        """Testa que validação aceita maiúsculas e minúsculas."""
        assert validate_plate_format("abc-1234") is True
        assert validate_plate_format("AbC-1234") is True

    def test_validate_mercosul_format_case_insensitive(self):
        """Testa que validação Mercosul aceita maiúsculas e minúsculas."""
        assert validate_plate_format("abc1d23") is True
        assert validate_plate_format("AbC1D23") is True

    def test_validate_invalid_format(self):
        """Testa validação de formatos inválidos."""
        assert validate_plate_format("ABC1234") is False  # Sem hífen
        assert validate_plate_format("ABC-123") is False  # Poucos dígitos
        assert validate_plate_format("AB-1234") is False  # Poucas letras
        assert validate_plate_format("INVALID") is False
        assert validate_plate_format("1234-ABC") is False  # Ordem invertida

    def test_validate_empty_string(self):
        """Testa validação de string vazia."""
        assert validate_plate_format("") is False
        assert validate_plate_format("   ") is False

    def test_validate_with_spaces(self):
        """Testa que espaços são removidos antes da validação."""
        assert validate_plate_format(" ABC-1234 ") is True
        assert validate_plate_format("ABC1D23 ") is True


class TestNormalizePlate:
    """Testes para normalização de placas."""

    def test_normalize_old_format(self):
        """Testa normalização de placa formato antigo."""
        assert normalize_plate("ABC-1234") == "ABC1234"
        assert normalize_plate("XYZ-9999") == "XYZ9999"

    def test_normalize_mercosul_format(self):
        """Testa normalização de placa formato Mercosul."""
        assert normalize_plate("ABC1D23") == "ABC1D23"
        assert normalize_plate("XYZ9Z99") == "XYZ9Z99"

    def test_normalize_with_spaces(self):
        """Testa normalização removendo espaços."""
        assert normalize_plate("ABC 1234") == "ABC1234"
        assert normalize_plate(" ABC-1234 ") == "ABC1234"

    def test_normalize_with_dots(self):
        """Testa normalização removendo pontos."""
        assert normalize_plate("ABC.1234") == "ABC1234"

    def test_normalize_case_insensitive(self):
        """Testa que normalização converte para maiúsculas."""
        assert normalize_plate("abc-1234") == "ABC1234"
        assert normalize_plate("AbC-1234") == "ABC1234"

    def test_normalize_empty_string_raises(self):
        """Testa que string vazia levanta ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            normalize_plate("")

    def test_normalize_only_special_chars_raises(self):
        """Testa que apenas caracteres especiais levanta ValueError."""
        with pytest.raises(ValueError, match="cannot be empty after normalization"):
            normalize_plate("---")

    def test_normalize_none_raises(self):
        """Testa que None levanta ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            normalize_plate(None)  # type: ignore[arg-type]


class TestSanitizeText:
    """Testes para sanitização de texto."""

    def test_sanitize_normal_text(self):
        """Testa sanitização de texto normal."""
        text = "Texto normal sem caracteres especiais"
        assert sanitize_text(text) == text

    def test_sanitize_removes_control_chars(self):
        """Testa que caracteres de controle são removidos."""
        text = "Texto\x00com\x01caracteres\x02de\x03controle"
        result = sanitize_text(text)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x02" not in result
        assert "\x03" not in result
        assert "Texto" in result
        assert "com" in result

    def test_sanitize_preserves_newlines(self):
        """Testa que quebras de linha são preservadas."""
        text = "Linha 1\nLinha 2\rLinha 3\r\nLinha 4"
        result = sanitize_text(text)
        assert "\n" in result
        assert "\r" in result
        assert "\r\n" in result or ("\r" in result and "\n" in result)

    def test_sanitize_preserves_tabs(self):
        """Testa que tabs são preservadas."""
        text = "Coluna1\tColuna2\tColuna3"
        result = sanitize_text(text)
        assert "\t" in result

    def test_sanitize_with_max_length(self):
        """Testa sanitização com limite de comprimento."""
        text = "Texto muito longo que deve ser truncado"
        result = sanitize_text(text, max_length=10)
        assert len(result) == 10
        assert result == "Texto muit"

    def test_sanitize_empty_string(self):
        """Testa sanitização de string vazia."""
        assert sanitize_text("") == ""
        assert sanitize_text("   ") == ""

    def test_sanitize_strips_whitespace(self):
        """Testa que espaços em branco são removidos."""
        text = "   Texto com espaços   "
        result = sanitize_text(text)
        assert result == "Texto com espaços"

    def test_sanitize_removes_only_control_chars(self):
        """Testa que apenas caracteres de controle são removidos, não caracteres especiais."""
        text = "Texto com <tags> e 'aspas' e \"aspas duplas\""
        result = sanitize_text(text)
        # Caracteres especiais devem ser preservados (FastAPI/Pydantic fazem escape)
        assert "<" in result
        assert ">" in result
        assert "'" in result
        assert '"' in result

    def test_sanitize_with_unicode(self):
        """Testa sanitização com caracteres Unicode."""
        text = "Texto com acentuação: ção, ão, í, é"
        result = sanitize_text(text)
        assert "ção" in result
        assert "ão" in result
        assert "í" in result
        assert "é" in result
