"""Pipeline OCR de placas (EasyOCR + OpenCV), extraído do script `recognize-plate.py`.

Instalação opcional::

    pip install -r requirements-ml.txt

Sem estas dependências, `ml_stack_available()` é False e a rota HTTP responde 503.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

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


def ler_placa(placa_img: np.ndarray) -> str:
    reader = _get_reader()
    resultado = reader.readtext(placa_img, detail=0, paragraph=True)
    if not resultado:
        return ""
    texto = "".join(resultado).replace(" ", "").upper()
    return "".join(c for c in texto if c.isalnum())


def recognize_plates_from_bgr(frame_bgr: np.ndarray) -> list[PlateOcrCandidate]:
    """Procura regiões candidatas (contornos) e devolve placas com 7 caracteres alfanuméricos."""
    import cv2

    if not ml_stack_available():
        return []

    gray_eq = cv2.equalizeHist(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY))
    edges = cv2.Canny(gray_eq, 100, 200)
    contornos, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    seen: set[str] = set()
    out: list[PlateOcrCandidate] = []

    for c in contornos:
        x, y, w, h = cv2.boundingRect(c)
        if w <= 100 or h <= 30:
            continue
        placa = frame_bgr[y : y + h, x : x + w]
        if placa.size == 0:
            continue
        tipo = "moto" if w <= h else "carro"

        placa_final, cor = preprocess_placa(placa, tipo)
        texto = ler_placa(placa_final)

        if len(texto) != 7:
            continue
        if texto in seen:
            continue
        seen.add(texto)
        out.append({"plate_raw": texto, "plate_color_hint": cor})

    return out
