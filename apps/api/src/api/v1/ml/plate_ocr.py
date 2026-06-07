"""Pipeline OCR de placas (EasyOCR + OpenCV), extraído do script `recognize-plate.py`.

Dependências em `requirements.txt` (numpy, opencv-python-headless, easyocr).
Se não carregarem no processo, `ml_stack_available()` é False e a rota HTTP responde 503.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, TypedDict

from apps.api.src.api.v1.utils.plate import validate_brazilian_plate

logger = logging.getLogger(__name__)

_PLATE_ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
_PLATE_LEN = 7

_ml_lock = threading.Lock()
_reader = None
_ml_available: bool | None = None


class PlateOcrCandidate(TypedDict):
    plate_raw: str
    plate_color_hint: str


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


def _get_reader():
    global _reader
    if not ml_stack_available():
        msg = "ML stack not installed"
        raise RuntimeError(msg)
    with _ml_lock:
        if _reader is None:
            import easyocr

            logger.warning("Carregando EasyOCR (primeira requisição pode demorar)...")
            _reader = easyocr.Reader(["en"], gpu=False)
        return _reader


def warm_up_easyocr() -> None:
    """Load EasyOCR models at startup so the first HTTP request is not blocked for minutes."""
    if not ml_stack_available():
        return
    _get_reader()
    logger.info("EasyOCR warm-up completed")


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
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    placa_bin = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    if np.sum(placa_bin == 0) > np.sum(placa_bin == 255):
        placa_bin = cv2.bitwise_not(placa_bin)

    return placa_bin, cor


def _append_candidate(
    texto: str,
    cor: str,
    seen: set[str],
    out: list[PlateOcrCandidate],
) -> None:
    if len(texto) != _PLATE_LEN or texto in seen:
        return
    valid, _ = validate_brazilian_plate(texto)
    if not valid:
        return
    seen.add(texto)
    out.append({"plate_raw": texto, "plate_color_hint": cor})


def _extract_valid_plates(
    merged: str,
    cor: str,
    seen: set[str],
    out: list[PlateOcrCandidate],
) -> None:
    if len(merged) < _PLATE_LEN:
        return
    for i in range(len(merged) - _PLATE_LEN + 1):
        chunk = merged[i : i + _PLATE_LEN]
        _append_candidate(chunk, cor, seen, out)


def _ocr_text_from_image(placa_img: np.ndarray) -> str:
    best = _best_valid_plate_from_image(placa_img)
    return best[0] if best else ""


def _best_valid_plate_from_image(placa_img: np.ndarray) -> tuple[str, float] | None:
    reader = _get_reader()
    results = reader.readtext(placa_img, detail=1, allowlist=_PLATE_ALLOWLIST)
    best: tuple[str, float] | None = None

    def consider(text: str, conf: float) -> None:
        nonlocal best
        merged = "".join(c for c in text.upper() if c.isalnum())
        chunks: list[str] = []
        if len(merged) == _PLATE_LEN:
            chunks.append(merged)
        if len(merged) > _PLATE_LEN:
            for i in range(len(merged) - _PLATE_LEN + 1):
                chunks.append(merged[i : i + _PLATE_LEN])
        for chunk in chunks:
            valid, _ = validate_brazilian_plate(chunk)
            if valid and (best is None or conf > best[1]):
                best = (chunk, conf)

    for _bbox, text, conf in results:
        consider(text, float(conf))

    if best:
        return best

    paragraph = reader.readtext(
        placa_img, detail=0, paragraph=True, allowlist=_PLATE_ALLOWLIST
    )
    consider("".join(paragraph), 0.0)
    return best


def _full_frame_fallback(frame_bgr: np.ndarray, seen: set[str], out: list[PlateOcrCandidate]) -> None:
    """When contour detection finds nothing, try preprocessing + OCR on plate-like regions."""
    import cv2

    h, w = frame_bgr.shape[:2]
    regions: list[np.ndarray] = [frame_bgr]
    if h > 80 and w > 80:
        y0 = int(h * 0.45)
        regions.append(frame_bgr[y0:h, :])
        x0, x1 = int(w * 0.1), int(w * 0.9)
        regions.append(frame_bgr[y0:h, x0:x1])

    for region in regions:
        placa_final, cor = preprocess_placa(region, "carro")
        merged = _ocr_text_from_image(placa_final)
        _append_candidate(merged, cor, seen, out)
        _extract_valid_plates(merged, cor, seen, out)
        if out:
            return

    for region in regions:
        merged = _ocr_text_from_image(region)
        _extract_valid_plates(merged, "desconhecida", seen, out)
        if out:
            return


def _upscale_if_small(frame_bgr: np.ndarray) -> np.ndarray:
    import cv2

    h, w = frame_bgr.shape[:2]
    if h >= 720 or w >= 1280:
        return frame_bgr
    scale = 2 if max(h, w) < 640 else 1.5
    return cv2.resize(
        frame_bgr,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )


def recognize_plates_from_bgr(frame_bgr: np.ndarray) -> list[PlateOcrCandidate]:
    """Procura regiões candidatas (contornos) e devolve placas com 7 caracteres alfanuméricos."""
    import cv2

    if not ml_stack_available():
        return []

    frame_bgr = _upscale_if_small(frame_bgr)

    seen: set[str] = set()
    out: list[PlateOcrCandidate] = []

    # Webcam frames often lack clean contours; try full-frame OCR first.
    _full_frame_fallback(frame_bgr, seen, out)
    if out:
        return out

    gray_eq = cv2.equalizeHist(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY))
    edges = cv2.Canny(gray_eq, 80, 180)
    contornos, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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

        placa_final, cor = preprocess_placa(placa, tipo)
        merged = _ocr_text_from_image(placa_final)
        _append_candidate(merged, cor, seen, out)
        _extract_valid_plates(merged, cor, seen, out)

    return out
