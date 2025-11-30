"""Script standalone para detecção e reconhecimento de placas veiculares.

Este script é uma ferramenta de desenvolvimento/teste que utiliza OpenCV e EasyOCR
para detectar e reconhecer placas de veículos através de uma câmera USB. Ele não
faz parte da API FastAPI e deve ser executado independentemente.

Funcionalidades:
- Captura de vídeo em tempo real via câmera USB
- Detecção de placas usando processamento de imagem (OpenCV)
- Reconhecimento de texto usando OCR (EasyOCR)
- Classificação de tipo de placa (branca, amarela, cinza)
- Salvamento de imagens e dados em CSV

Uso:
    python apps/api/src/api/v1/ml/recognize-plate.py

Nota: Este script requer acesso a uma câmera USB e as dependências opencv-python
e easyocr instaladas.
"""

import csv
import platform
import time
import warnings
from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np

# winsound é específico do Windows, usar import condicional
if platform.system() == "Windows":
    try:
        import winsound  # type: ignore[reportMissingImports]
    except ImportError:
        winsound = None  # type: ignore[assignment]
else:
    winsound = None  # type: ignore[assignment]

# Silencia avisos do EasyOCR
warnings.filterwarnings("ignore", category=UserWarning)

# =============== CONFIGURAÇÕES ==================
CAMERA_USB = 0
DETECTED_PLATES_DIR = Path("placas_detectadas")
CSV_FILE = Path("numeros.csv")
MAX_TIME = 300  # segundos

# Constantes para detecção de cor de placa
SATURATION_THRESHOLD_WHITE = 40
VALUE_THRESHOLD_WHITE = 130
HUE_MIN_YELLOW = 15
HUE_MAX_YELLOW = 40
SATURATION_THRESHOLD_YELLOW = 60
VALUE_THRESHOLD_GRAY = 120
BINARY_MAX_VALUE = 255

# Constantes para detecção de contornos
MIN_WIDTH = 100
MIN_HEIGHT = 30
PLATE_LENGTH = 7
ESC_KEY = 27

DETECTED_PLATES_DIR.mkdir(parents=True, exist_ok=True)


# =============== FUNÇÕES ==================
# Variável de módulo para armazenar a instância singleton do EasyOCR Reader
_reader_instance: easyocr.Reader | None = None  # type: ignore[type-arg]


def get_reader() -> easyocr.Reader:  # type: ignore[type-arg]
    """Inicializa e retorna uma instância singleton do EasyOCR Reader.

    Usa lazy initialization para evitar inicialização custosa no import do módulo.
    A inicialização do EasyOCR pode levar vários segundos, então só é feita quando
    necessário (quando read_plate() é chamada pela primeira vez).

    Returns:
        easyocr.Reader: Instância do EasyOCR Reader configurada para inglês.
    """
    global _reader_instance  # noqa: PLW0603
    if _reader_instance is None:
        _reader_instance = easyocr.Reader(["en"], gpu=False)  # type: ignore[assignment]
    return _reader_instance


def detect_plate_color_type(plate_img: Any) -> str:
    """Tenta identificar se a placa é branca (nova), amarela ou cinza (antiga)."""
    hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    mean_v, mean_h, mean_s = np.mean(v), np.mean(h), np.mean(s)

    if mean_s < SATURATION_THRESHOLD_WHITE and mean_v > VALUE_THRESHOLD_WHITE:
        return "white"
    if HUE_MIN_YELLOW < mean_h < HUE_MAX_YELLOW and mean_s > SATURATION_THRESHOLD_YELLOW:
        return "yellow"
    if mean_v < VALUE_THRESHOLD_GRAY:
        return "gray"
    return "unknown"


def preprocess_plate(plate_img: Any, vehicle_type: str = "car") -> tuple[Any, str]:
    """Pré-processa imagem da placa para OCR (tons de cinza e contraste)."""
    color = detect_plate_color_type(plate_img)
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

    if color in ["yellow", "gray"]:
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0, 0), 3), -0.5, 0)
    else:
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

    if vehicle_type == "motorcycle":
        height = 50
        width = 7 * 20
        gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
    else:
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    plate_binary = cv2.adaptiveThreshold(
        gray, BINARY_MAX_VALUE, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    if np.sum(plate_binary == 0) > np.sum(plate_binary == BINARY_MAX_VALUE):
        plate_binary = cv2.bitwise_not(plate_binary)

    return plate_binary, color


def read_plate(plate_img: Any) -> str:
    """Lê o texto da placa usando OCR."""
    reader = get_reader()
    result = reader.readtext(plate_img, detail=0, paragraph=True)
    if not result:
        return ""
    # result é uma lista de strings quando detail=0
    text = "".join(str(r) for r in result).replace(" ", "").upper()
    return "".join([c for c in text if c.isalnum()])


def save_csv(text: str, color: str) -> None:
    """Salva o texto e cor da placa em arquivo CSV."""
    file_exists = CSV_FILE.exists()
    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Placa", "Tipo", "DataHora"])
        writer.writerow([text, color, time.strftime("%Y-%m-%d %H:%M:%S")])


def save_image(plate_img: Any, text: str, color: str) -> None:
    """Salva a imagem da placa processada."""
    file_path = DETECTED_PLATES_DIR / f"{text}{color}{int(time.time())}.png"
    cv2.imwrite(str(file_path), plate_img)


# =============== CAPTURA DE CÂMERA ==================
cap = cv2.VideoCapture(CAMERA_USB)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

start_time = time.time()

# ================= LOOP PRINCIPAL =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Trabalha internamente com tons de cinza, mas exibe colorido
    gray_eq = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    edges = cv2.Canny(gray_eq, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > MIN_WIDTH and h > MIN_HEIGHT:
            plate = frame[y : y + h, x : x + w]
            vehicle_type = "car" if w > h else "motorcycle"

            processed_plate, color = preprocess_plate(plate, vehicle_type)
            text = read_plate(processed_plate)

            if len(text) == PLATE_LENGTH:
                save_csv(text, color)
                save_image(processed_plate, text, color)

                if vehicle_type == "motorcycle" and winsound is not None:
                    # pyright: ignore[reportAttributeAccessIssue] - winsound é específico do Windows
                    winsound.Beep(1000, 300)

                # Desenha retângulo colorido na imagem original
                box_color = (0, 255, 0) if vehicle_type == "car" else (0, 255, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)

    cv2.imshow("Detecção de Placas - Câmera Colorida", frame)

    if cv2.waitKey(1) & 0xFF == ESC_KEY:
        break
    if time.time() - start_time > MAX_TIME:
        break

cap.release()
cv2.destroyAllWindows()
