"""Serviço de OCR para reconhecimento de placas veiculares."""

import cv2
import numpy as np
import warnings
from typing import Optional, Tuple

from apps.iot_device.config import OCR_LANGUAGES, GPU_ENABLED
from apps.iot_device.utils.plate_validator import normalize_plate, validate_brazilian_plate

# Tentar importar EasyOCR, mas não falhar se não estiver disponível
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

# Silenciar avisos do EasyOCR
warnings.filterwarnings("ignore", category=UserWarning)


class OCRService:
    """Serviço de reconhecimento óptico de caracteres para placas veiculares."""

    def __init__(self):
        """
        Inicializa o serviço OCR.

        O EasyOCR é inicializado com os idiomas configurados.
        Para placas brasileiras, usamos inglês (caracteres alfanuméricos).
        """
        if not EASYOCR_AVAILABLE:
            raise ImportError(
                "EasyOCR não está instalado. "
                "Instale com: pip install easyocr "
                "(Nota: Python 3.14 pode ter problemas. Use Python 3.12 se possível)"
            )
        self.reader = easyocr.Reader(OCR_LANGUAGES, gpu=GPU_ENABLED, verbose=False)

    def detect_plate_color_type(self, plate_img: np.ndarray) -> str:
        """
        Identifica o tipo de placa baseado na cor.

        Args:
            plate_img: Imagem BGR da placa

        Returns:
            Tipo de placa: "branca", "amarela", "cinza" ou "desconhecida"
        """
        hsv = cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        media_v, media_h, media_s = np.mean(v), np.mean(h), np.mean(s)

        # Placa branca (Mercosul): baixa saturação, alta luminosidade
        if media_s < 40 and media_v > 130:
            return "branca"
        # Placa amarela (táxi/ônibus): matiz amarelo, alta saturação
        elif 15 < media_h < 40 and media_s > 60:
            return "amarela"
        # Placa cinza (antiga): baixa luminosidade
        elif media_v < 120:
            return "cinza"
        else:
            return "desconhecida"

    def preprocess_plate(
        self, plate_img: np.ndarray, vehicle_type: str = "carro"
    ) -> Tuple[np.ndarray, str]:
        """
        Pré-processa imagem da placa para melhorar a precisão do OCR.

        Args:
            plate_img: Imagem BGR da placa
            vehicle_type: Tipo de veículo ("carro" ou "moto")

        Returns:
            Tupla (imagem_processada, tipo_cor)
        """
        color = self.detect_plate_color_type(plate_img)
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

        # Ajustes específicos por tipo de placa
        if color in ["amarela", "cinza"]:
            # Placas antigas: equalização e realce de contraste
            gray = cv2.equalizeHist(gray)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            gray = cv2.addWeighted(
                gray, 1.5, cv2.GaussianBlur(gray, (0, 0), 3), -0.5, 0
            )
        else:
            # Placas brancas: filtro bilateral para preservar bordas
            gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # Redimensionar para melhorar OCR
        if vehicle_type == "moto":
            # Placas de moto são menores e mais estreitas
            altura = 50
            largura = 7 * 20  # Aproximadamente 7 caracteres * 20px
            gray = cv2.resize(gray, (largura, altura), interpolation=cv2.INTER_CUBIC)
        else:
            # Placas de carro: aumentar 3x para melhor resolução
            gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # Binarização adaptativa
        plate_bin = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
        )

        # Inverter se necessário (texto escuro em fundo claro)
        if np.sum(plate_bin == 0) > np.sum(plate_bin == 255):
            plate_bin = cv2.bitwise_not(plate_bin)

        return plate_bin, color

    def read_plate(self, plate_img: np.ndarray) -> Optional[str]:
        """
        Lê o texto da placa usando OCR.

        Args:
            plate_img: Imagem processada da placa (binarizada)

        Returns:
            Texto da placa normalizado ou None se não detectado
        """
        try:
            # EasyOCR retorna lista de tuplas (bbox, text, confidence)
            results = self.reader.readtext(
                plate_img, detail=0, paragraph=True, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            )

            if not results:
                return None

            # Concatenar todos os textos detectados
            text = "".join(results).replace(" ", "").upper()
            # Remover caracteres não alfanuméricos
            normalized = normalize_plate(text)

            # Validar formato brasileiro
            is_valid, validated_plate = validate_brazilian_plate(normalized)

            if is_valid:
                return validated_plate

            # Se não passou na validação mas tem 7 caracteres, retornar mesmo assim
            # (pode ser erro de OCR, mas melhor processar do que ignorar)
            if len(normalized) == 7:
                return normalized

            return None

        except Exception:
            # Em caso de erro no OCR, retornar None
            return None
