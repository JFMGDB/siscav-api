"""Cliente para comunicação com a API central."""

import io
import logging
from typing import Optional, Dict, Any

import cv2
import numpy as np
import requests

from apps.iot_device.config import ACCESS_LOGS_ENDPOINT

logger = logging.getLogger(__name__)


class APIClient:
    """Cliente HTTP para comunicação com a API central."""

    def __init__(self, timeout: int = 10):
        """
        Inicializa o cliente API.

        Args:
            timeout: Timeout em segundos para requisições HTTP
        """
        self.timeout = timeout
        self.endpoint = ACCESS_LOGS_ENDPOINT

    def send_access_log(
        self, plate_text: str, plate_image: np.ndarray
    ) -> Optional[Dict[str, Any]]:
        """
        Envia placa detectada e imagem para a API central.

        Args:
            plate_text: Texto da placa detectada
            plate_image: Imagem da placa (BGR do OpenCV)

        Returns:
            Resposta JSON da API ou None em caso de erro
        """
        try:
            # Codificar imagem para JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # Qualidade 85%
            success, img_encoded = cv2.imencode(".jpg", plate_image, encode_params)

            if not success:
                logger.error("Falha ao codificar imagem da placa")
                return None

            file_bytes = io.BytesIO(img_encoded.tobytes())

            files = {"file": ("plate.jpg", file_bytes, "image/jpeg")}
            data = {"plate": plate_text}

            logger.info(f"Enviando placa {plate_text} para API")
            response = requests.post(
                self.endpoint, files=files, data=data, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Resposta da API: {result.get('status', 'Unknown')}")
            return result

        except requests.Timeout:
            logger.error("Timeout ao enviar dados para API")
            return None
        except requests.RequestException as e:
            logger.error(f"Erro ao enviar dados para API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar dados: {e}")
            return None
