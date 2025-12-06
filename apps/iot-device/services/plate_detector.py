"""Serviço de detecção de placas veiculares usando processamento de imagem."""

import cv2
import numpy as np
from typing import Optional, Tuple


class PlateDetector:
    """Detecta placas veiculares em frames de vídeo usando processamento de imagem."""

    def __init__(
        self,
        min_width: int = 100,
        min_height: int = 30,
        max_width: int = 500,
        max_height: int = 200,
        min_aspect_ratio: float = 2.0,
        max_aspect_ratio: float = 6.0,
    ):
        """
        Inicializa o detector de placas.

        Args:
            min_width: Largura mínima da placa em pixels
            min_height: Altura mínima da placa em pixels
            max_width: Largura máxima da placa em pixels
            max_height: Altura máxima da placa em pixels
            min_aspect_ratio: Razão de aspecto mínima (largura/altura)
            max_aspect_ratio: Razão de aspecto máxima (largura/altura)
        """
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio

    def detect_plates(self, frame: np.ndarray) -> list[Tuple[int, int, int, int]]:
        """
        Detecta possíveis placas no frame.

        Args:
            frame: Frame BGR do OpenCV

        Returns:
            Lista de tuplas (x, y, width, height) representando regiões candidatas
        """
        # Converter para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Equalização de histograma para melhorar contraste
        gray_eq = cv2.equalizeHist(gray)

        # Aplicar filtro bilateral para reduzir ruído mantendo bordas
        gray_filtered = cv2.bilateralFilter(gray_eq, 9, 75, 75)

        # Detecção de bordas usando Canny
        edges = cv2.Canny(gray_filtered, 50, 150, apertureSize=3)

        # Operações morfológicas para conectar bordas próximas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrar contornos por características de placas
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Filtrar por tamanho
            if not (self.min_width <= w <= self.max_width and self.min_height <= h <= self.max_height):
                continue

            # Filtrar por razão de aspecto (placas são retangulares horizontais)
            aspect_ratio = w / h
            if not (self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio):
                continue

            # Filtrar por área mínima do contorno
            area = cv2.contourArea(contour)
            if area < (w * h * 0.5):  # Contorno deve ocupar pelo menos 50% da bounding box
                continue

            candidates.append((x, y, w, h))

        # Ordenar por área (maior primeiro)
        candidates.sort(key=lambda c: c[2] * c[3], reverse=True)

        # Remover sobreposições (manter apenas a maior)
        filtered_candidates = []
        for candidate in candidates:
            x, y, w, h = candidate
            overlap = False
            for existing in filtered_candidates:
                ex, ey, ew, eh = existing
                # Calcular interseção
                inter_x = max(x, ex)
                inter_y = max(y, ey)
                inter_w = min(x + w, ex + ew) - inter_x
                inter_h = min(y + h, ey + eh) - inter_y
                if inter_w > 0 and inter_h > 0:
                    inter_area = inter_w * inter_h
                    candidate_area = w * h
                    if inter_area > candidate_area * 0.5:  # Mais de 50% de sobreposição
                        overlap = True
                        break
            if not overlap:
                filtered_candidates.append(candidate)

        return filtered_candidates

    def extract_plate_region(
        self, frame: np.ndarray, x: int, y: int, w: int, h: int
    ) -> np.ndarray:
        """
        Extrai a região da placa do frame.

        Args:
            frame: Frame BGR completo
            x, y, w, h: Coordenadas e dimensões da placa

        Returns:
            Imagem da região da placa
        """
        # Adicionar margem pequena para capturar bordas
        margin = 5
        x_start = max(0, x - margin)
        y_start = max(0, y - margin)
        x_end = min(frame.shape[1], x + w + margin)
        y_end = min(frame.shape[0], y + h + margin)

        return frame[y_start:y_end, x_start:x_end]













