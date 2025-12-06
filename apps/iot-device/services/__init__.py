"""Serviços do dispositivo IoT."""

from . import api_client
from . import camera
from . import plate_detector
from . import arduino

# OCR é opcional (requer easyocr)
try:
    from . import ocr
except ImportError:
    ocr = None












