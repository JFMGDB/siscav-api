import cv2
import time
from apps.iot_device.config import CAMERA_ID, FRAME_HEIGHT, FRAME_WIDTH, FPS_LIMIT

class CameraService:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_ID)
        # Configurar propriedades da câmera para melhor performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        # Desabilitar buffer para reduzir latência
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # Configurar FPS se suportado
        if FPS_LIMIT > 0:
            self.cap.set(cv2.CAP_PROP_FPS, FPS_LIMIT)
        
        self.last_frame_time = 0
        self.min_frame_interval = 1.0 / FPS_LIMIT if FPS_LIMIT > 0 else 0

    def read_frame(self):
        # Controlar FPS manualmente se necessário
        if self.min_frame_interval > 0:
            current_time = time.time()
            elapsed = current_time - self.last_frame_time
            if elapsed < self.min_frame_interval:
                time.sleep(self.min_frame_interval - elapsed)
            self.last_frame_time = time.time()
        
        # Descartar frames antigos do buffer
        for _ in range(2):
            ret, _ = self.cap.read()
            if not ret:
                break
        
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read from camera")
        return frame

    def release(self):
        self.cap.release()
