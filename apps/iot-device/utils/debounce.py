"""Sistema de debounce para evitar detecções duplicadas da mesma placa."""

import time
from typing import Dict, Optional


class PlateDebouncer:
    """Gerencia debounce de detecções de placas para evitar processamento duplicado."""

    def __init__(self, cooldown_seconds: float = 3.0):
        """
        Inicializa o debouncer.

        Args:
            cooldown_seconds: Tempo em segundos antes de permitir nova detecção da mesma placa
        """
        self.cooldown_seconds = cooldown_seconds
        self.last_detections: Dict[str, float] = {}

    def should_process(self, plate: str) -> bool:
        """
        Verifica se uma placa deve ser processada (não está em cooldown).

        Args:
            plate: Placa normalizada

        Returns:
            True se a placa deve ser processada, False caso contrário
        """
        current_time = time.time()
        last_time = self.last_detections.get(plate, 0)

        if current_time - last_time >= self.cooldown_seconds:
            self.last_detections[plate] = current_time
            # Limpar entradas antigas (mais de 1 minuto)
            self._cleanup_old_entries(current_time)
            return True

        return False

    def _cleanup_old_entries(self, current_time: float) -> None:
        """Remove entradas com mais de 1 minuto do histórico."""
        cutoff_time = current_time - 60.0
        self.last_detections = {
            plate: timestamp
            for plate, timestamp in self.last_detections.items()
            if timestamp > cutoff_time
        }

    def reset(self) -> None:
        """Reseta o histórico de detecções."""
        self.last_detections.clear()













