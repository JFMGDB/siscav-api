"""Unit tests for plate OCR normalization helpers."""

from apps.api.src.api.v1.ml.plate_ocr import _normalize_plate_candidate, _repair_plate_ocr


class TestPlateOcrHelpers:
    def test_normalize_accepts_valid_mercosul(self):
        assert _normalize_plate_candidate("ABC1D23") == "ABC1D23"

    def test_repair_common_confusions_mercosul(self):
        assert _repair_plate_ocr("AB01D23") == "ABO1D23"
        assert _repair_plate_ocr("ABC1D2O") == "ABC1D20"

    def test_repair_common_confusions_old_format(self):
        assert _repair_plate_ocr("ABCO234") == "ABC0234"

    def test_normalize_rejects_short_noise(self):
        assert _normalize_plate_candidate("ABC12") is None
