"""Pipeline OCR de placas (EasyOCR + OpenCV), extraído do script `recognize-plate.py`.

Dependências em `requirements.txt` (numpy, opencv-python-headless, easyocr).
Se não carregarem no processo, `ml_stack_available()` é False e a rota HTTP responde 503.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, TypedDict

from apps.api.src.api.v1.utils.plate import validate_brazilian_plate

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

_PLATE_ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_PLATE_LEN = 7
_MAX_READTEXT_DIM = 960
_EASYOCR_CANVAS_SIZE = 960
_MAX_CONTOUR_CANDIDATES = 3
_MIN_OCR_CONFIDENCE = 0.52
_HIGH_CONFIDENCE_EARLY_EXIT = 0.78

_ml_lock = threading.Lock()
_reader = None
_ml_available: bool | None = None
_warm_up_ready = False
_warm_up_error: str | None = None


class PlateOcrCandidate(TypedDict):
    plate_raw: str
    plate_color_hint: str
    confidence: float


def ml_stack_available() -> bool:
    """True se opencv + numpy + easyocr estão instalados."""
    global _ml_available
    if _ml_available is not None:
        return _ml_available
    try:
        import cv2  # noqa: F401
        import easyocr  # noqa: F401
        import numpy as np  # noqa: F401
    except ImportError:
        _ml_available = False
        return False
    _ml_available = True
    return True


def ocr_engine_ready() -> bool:
    """True when warm-up completed successfully."""
    return _warm_up_ready and _warm_up_error is None


def ocr_engine_unavailable_reason() -> str | None:
    """Human-readable reason when OCR cannot run."""
    if not ml_stack_available():
        return "ML stack not installed (pip install -r requirements-ml.txt)"
    return _warm_up_error


def _get_reader():
    global _reader, _warm_up_error
    if not ml_stack_available():
        msg = "ML stack not installed"
        raise RuntimeError(msg)
    with _ml_lock:
        if _reader is None:
            import easyocr

            logger.info("Loading EasyOCR Reader (CPU)...")
            try:
                _reader = easyocr.Reader(["en"], gpu=False)
            except Exception as exc:
                _warm_up_error = f"EasyOCR Reader failed to load: {exc}"
                logger.exception(_warm_up_error)
                raise
        return _reader


def warm_up_easyocr() -> None:
    """Load EasyOCR and run a tiny inference so the first HTTP request is fast."""
    global _warm_up_ready, _warm_up_error
    if not ml_stack_available():
        return
    try:
        reader = _get_reader()
        import numpy as np

        dummy = np.zeros((32, 128, 3), dtype=np.uint8)
        reader.readtext(
            dummy,
            detail=1,
            allowlist=_PLATE_ALLOWLIST,
            canvas_size=_EASYOCR_CANVAS_SIZE,
            mag_ratio=1.0,
            paragraph=False,
        )
        _warm_up_ready = True
        _warm_up_error = None
        logger.info("EasyOCR warm-up completed (Reader + dummy inference)")
    except Exception as exc:
        _warm_up_ready = False
        _warm_up_error = f"EasyOCR warm-up failed: {exc}"
        logger.exception(_warm_up_error)
        raise


def _cap_for_readtext(img: np.ndarray, max_dim: int = _MAX_READTEXT_DIM) -> np.ndarray:
    import cv2

    h, w = img.shape[:2]
    longest = max(h, w)
    if longest <= max_dim:
        return img
    scale = max_dim / longest
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def detectar_tipo_cor(placa_img: np.ndarray) -> str:
    import cv2
    import numpy as np

    hsv = cv2.cvtColor(placa_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    media_v, media_h, media_s = np.mean(v), np.mean(h), np.mean(s)

    if media_s < 40 and media_v > 130:
        return "branca"
    if 15 < media_h < 40 and media_s > 60:
        return "amarela"
    if media_v < 120:
        return "cinza"
    return "desconhecida"


def preprocess_placa(placa_img: np.ndarray, tipo: str = "carro") -> tuple[np.ndarray, str]:
    import cv2
    import numpy as np

    cor = detectar_tipo_cor(placa_img)
    gray = cv2.cvtColor(placa_img, cv2.COLOR_BGR2GRAY)

    if cor in ("amarela", "cinza"):
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0, 0), 3), -0.5, 0)
    else:
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

    if tipo == "moto":
        altura = 50
        largura = 7 * 20
        gray = cv2.resize(gray, (largura, altura), interpolation=cv2.INTER_CUBIC)
    else:
        longest = max(gray.shape[:2])
        if longest < 200:
            gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        elif longest < 400:
            gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    placa_bin = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    if np.sum(placa_bin == 0) > np.sum(placa_bin == 255):
        placa_bin = cv2.bitwise_not(placa_bin)

    return placa_bin, cor


def _repair_plate_ocr(text: str) -> str | None:
    """Fix common OCR confusions using Brazilian plate position rules."""
    merged = "".join(c for c in text.upper() if c.isalnum())
    if len(merged) != _PLATE_LEN:
        return None

    letter_to_digit = str.maketrans("OQIZSGB", "0012586")
    digit_to_letter = str.maketrans("0158", "OISB")

    def try_layout(letter_positions: set[int], digit_positions: set[int]) -> str | None:
        chars: list[str] = []
        for i, ch in enumerate(merged):
            if i in letter_positions and ch.isdigit():
                chars.append(ch.translate(digit_to_letter))
            elif i in digit_positions and ch.isalpha():
                chars.append(ch.translate(letter_to_digit))
            else:
                chars.append(ch)
        candidate = "".join(chars)
        valid, _ = validate_brazilian_plate(candidate)
        return candidate if valid else None

    return try_layout({0, 1, 2, 4}, {3, 5, 6}) or try_layout({0, 1, 2}, {3, 4, 5, 6})


def _normalize_plate_candidate(text: str) -> str | None:
    merged = "".join(c for c in text.upper() if c.isalnum())
    if len(merged) != _PLATE_LEN:
        return None
    valid, _ = validate_brazilian_plate(merged)
    if valid:
        return merged
    return _repair_plate_ocr(merged)


def _readtext_for_plate(reader, img: np.ndarray) -> list:
    import cv2

    if img.ndim == 2:
        longest = max(img.shape[:2])
        if longest > _MAX_READTEXT_DIM:
            scale = _MAX_READTEXT_DIM / longest
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    else:
        img = _cap_for_readtext(img)
    return reader.readtext(
        img,
        detail=1,
        allowlist=_PLATE_ALLOWLIST,
        canvas_size=_EASYOCR_CANVAS_SIZE,
        mag_ratio=1.0,
        paragraph=False,
    )


def _best_valid_plate_from_image(
    placa_img: np.ndarray,
    tipo: str = "carro",
) -> tuple[str, float] | None:
    reader = _get_reader()
    best: tuple[str, float] | None = None

    def consider(text: str, conf: float) -> None:
        nonlocal best
        if conf < _MIN_OCR_CONFIDENCE:
            return
        merged = "".join(c for c in text.upper() if c.isalnum())
        if len(merged) != _PLATE_LEN:
            return
        plate = _normalize_plate_candidate(merged)
        if plate and (best is None or conf > best[1]):
            best = (plate, conf)

    placa_bin, _cor = preprocess_placa(placa_img, tipo)
    for img in (placa_bin, _cap_for_readtext(placa_img)):
        for _bbox, text, conf in _readtext_for_plate(reader, img):
            consider(text, float(conf))
        if best and best[1] >= _HIGH_CONFIDENCE_EARLY_EXIT:
            return best

    return best


def _scan_plate_region(
    placa_img: np.ndarray,
    tipo: str,
) -> tuple[str, float, str] | None:
    hit = _best_valid_plate_from_image(placa_img, tipo)
    if not hit:
        return None
    plate, confidence = hit
    return plate, confidence, detectar_tipo_cor(placa_img)


def _collect_frame_candidates(frame_bgr: np.ndarray) -> list[PlateOcrCandidate]:
    import cv2

    best_by_plate: dict[str, PlateOcrCandidate] = {}

    def register(plate: str, confidence: float, cor: str) -> None:
        existing = best_by_plate.get(plate)
        if existing is None or confidence > existing["confidence"]:
            best_by_plate[plate] = {
                "plate_raw": plate,
                "plate_color_hint": cor,
                "confidence": confidence,
            }

    gray_eq = cv2.equalizeHist(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY))
    edges = cv2.Canny(gray_eq, 80, 180)
    contornos, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contour_regions: list[tuple[int, np.ndarray, str]] = []
    for c in contornos:
        x, y, w, h = cv2.boundingRect(c)
        if w < 40 or h < 12:
            continue
        aspect = w / max(h, 1)
        if aspect < 1.2 or aspect > 8.0:
            continue
        placa = frame_bgr[y : y + h, x : x + w]
        if placa.size == 0:
            continue
        tipo = "moto" if w <= h else "carro"
        contour_regions.append((w * h, placa, tipo))

    contour_regions.sort(key=lambda item: item[0], reverse=True)
    for _area, placa, tipo in contour_regions[:_MAX_CONTOUR_CANDIDATES]:
        hit = _scan_plate_region(placa, tipo)
        if hit:
            register(*hit)
            if hit[1] >= _HIGH_CONFIDENCE_EARLY_EXIT:
                break

    if not best_by_plate:
        hit = _scan_plate_region(_cap_for_readtext(frame_bgr), "carro")
        if hit:
            register(*hit)

    return sorted(best_by_plate.values(), key=lambda item: item["confidence"], reverse=True)


def _upscale_if_small(frame_bgr: np.ndarray) -> np.ndarray:
    import cv2

    h, w = frame_bgr.shape[:2]
    longest = max(h, w)
    if longest >= 640:
        return frame_bgr
    return cv2.resize(
        frame_bgr,
        None,
        fx=1.5,
        fy=1.5,
        interpolation=cv2.INTER_CUBIC,
    )


def recognize_plates_from_bgr(frame_bgr: np.ndarray) -> list[PlateOcrCandidate]:
    """Procura regiões candidatas (contornos) e devolve placas com 7 caracteres alfanuméricos."""
    if not ml_stack_available():
        return []

    frame_bgr = _upscale_if_small(frame_bgr)
    return _collect_frame_candidates(frame_bgr)
