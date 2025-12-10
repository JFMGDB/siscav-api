"""Configurações do dispositivo IoT."""

import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
ACCESS_LOGS_ENDPOINT = f"{API_BASE_URL}/access_logs/"

# Camera Configuration
CAMERA_ID = int(os.getenv("CAMERA_ID", "0"))
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "320"))  # Reduzido para melhor performance
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "240"))  # Reduzido para melhor performance
FPS_LIMIT = int(os.getenv("FPS_LIMIT", "10"))  # Limitar FPS para reduzir carga

# OCR Configuration
OCR_LANGUAGES = ["en"]  # Inglês para caracteres alfanuméricos de placas
GPU_ENABLED = os.getenv("GPU_ENABLED", "false").lower() == "true"

# Plate Detection Configuration
PLATE_DETECTION_COOLDOWN = float(os.getenv("PLATE_DETECTION_COOLDOWN", "5.0"))  # segundos (aumentado para reduzir processamento)
MIN_PLATE_CONFIDENCE = float(os.getenv("MIN_PLATE_CONFIDENCE", "0.5"))

# Application Logic
MAX_RUNTIME_SECONDS = int(os.getenv("MAX_RUNTIME_SECONDS", "300"))
ENABLE_SOUND = os.getenv("ENABLE_SOUND", "true").lower() == "true"
ENABLE_DISPLAY = os.getenv("ENABLE_DISPLAY", "true").lower() == "true"

# Arduino Configuration
ARDUINO_ENABLED = os.getenv("ARDUINO_ENABLED", "true").lower() == "true"
ARDUINO_PORT = os.getenv("ARDUINO_PORT", None)  # None = auto-detect (ex: COM3, /dev/ttyUSB0)
ARDUINO_BAUD_RATE = int(os.getenv("ARDUINO_BAUD_RATE", "9600"))

# Demo Mode - Whitelist local (não precisa de API/banco de dados)
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
DEMO_WHITELIST = [
    "BRA2E19",  # Placa Mercosul de demonstração
    "ABC1234",  # Placa formato antigo
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
