"""Serviço de comunicação com Arduino para controle da cancela."""

import logging
import time
from typing import Optional

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

logger = logging.getLogger(__name__)


class ArduinoService:
    """Serviço para comunicação serial com Arduino."""

    # Comandos disponíveis
    CMD_ABRIR = 'A'      # Abrir/Autorizar cancela
    CMD_NEGAR = 'N'      # Negar acesso
    CMD_FECHAR = 'F'     # Fechamento forçado
    CMD_RESET = 'Z'      # Reset/Calibração

    def __init__(
        self,
        port: Optional[str] = None,
        baud_rate: int = 9600,
        timeout: float = 1.0,
        auto_connect: bool = True
    ):
        """
        Inicializa o serviço Arduino.

        Args:
            port: Porta serial (ex: COM3, /dev/ttyUSB0). Se None, tenta detectar automaticamente.
            baud_rate: Taxa de transmissão (padrão: 9600)
            timeout: Timeout de leitura em segundos
            auto_connect: Se True, conecta automaticamente na inicialização
        """
        if not SERIAL_AVAILABLE:
            raise ImportError(
                "Biblioteca pyserial não instalada. "
                "Execute: pip install pyserial"
            )

        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._connected = False

        if auto_connect:
            self.connect()

    @property
    def is_connected(self) -> bool:
        """Verifica se está conectado ao Arduino."""
        return self._connected and self._serial is not None and self._serial.is_open

    def _detect_arduino_port(self) -> Optional[str]:
        """
        Detecta automaticamente a porta do Arduino.

        Returns:
            Porta detectada ou None se não encontrada
        """
        logger.info("Procurando Arduino nas portas seriais...")
        
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Procurar por Arduino na descrição
            description = port.description.lower()
            if any(keyword in description for keyword in ['arduino', 'ch340', 'usb serial', 'usb-serial']):
                logger.info(f"Arduino detectado na porta: {port.device}")
                return port.device
        
        # Se não encontrou por descrição, listar portas disponíveis
        available_ports = [p.device for p in ports]
        if available_ports:
            logger.warning(f"Arduino não detectado automaticamente. Portas disponíveis: {available_ports}")
        else:
            logger.warning("Nenhuma porta serial encontrada")
        
        return None

    def connect(self) -> bool:
        """
        Estabelece conexão com o Arduino.

        Returns:
            True se conectado com sucesso, False caso contrário
        """
        if self.is_connected:
            logger.debug("Já conectado ao Arduino")
            return True

        try:
            # Se porta não especificada, tentar detectar
            port = self.port or self._detect_arduino_port()
            
            if not port:
                logger.error("Porta do Arduino não especificada e não detectada automaticamente")
                return False

            logger.info(f"Conectando ao Arduino na porta {port} ({self.baud_rate} baud)...")
            
            self._serial = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            
            # Aguardar Arduino reiniciar após conexão serial
            time.sleep(2)
            
            # Limpar buffer
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
            
            self._connected = True
            self.port = port  # Salvar porta detectada
            
            logger.info(f"Conectado ao Arduino na porta {port}")
            return True

        except serial.SerialException as e:
            logger.error(f"Erro ao conectar ao Arduino: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao conectar: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Desconecta do Arduino."""
        if self._serial and self._serial.is_open:
            try:
                self._serial.close()
                logger.info("Desconectado do Arduino")
            except Exception as e:
                logger.error(f"Erro ao desconectar: {e}")
        
        self._connected = False
        self._serial = None

    def send_command(self, command: str) -> bool:
        """
        Envia um comando para o Arduino.

        Args:
            command: Comando a enviar ('A', 'N', 'F', 'Z')

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.is_connected:
            logger.warning("Arduino não conectado. Tentando reconectar...")
            if not self.connect():
                logger.error("Falha ao reconectar ao Arduino")
                return False

        try:
            # Validar comando
            valid_commands = [self.CMD_ABRIR, self.CMD_NEGAR, self.CMD_FECHAR, self.CMD_RESET]
            if command not in valid_commands:
                logger.warning(f"Comando inválido: {command}. Comandos válidos: {valid_commands}")
                return False

            # Enviar comando
            self._serial.write(command.encode('utf-8'))
            self._serial.flush()
            
            logger.info(f"Comando '{command}' enviado ao Arduino")
            return True

        except serial.SerialException as e:
            logger.error(f"Erro de comunicação serial: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar comando: {e}")
            return False

    def abrir_cancela(self) -> bool:
        """
        Envia comando para abrir a cancela (autorização concedida).

        Returns:
            True se enviado com sucesso
        """
        logger.info("Enviando comando de ABERTURA ao Arduino")
        return self.send_command(self.CMD_ABRIR)

    def negar_acesso(self) -> bool:
        """
        Envia comando de negação de acesso.

        Returns:
            True se enviado com sucesso
        """
        logger.info("Enviando comando de NEGAÇÃO ao Arduino")
        return self.send_command(self.CMD_NEGAR)

    def fechar_cancela(self) -> bool:
        """
        Envia comando para fechar a cancela imediatamente.

        Returns:
            True se enviado com sucesso
        """
        logger.info("Enviando comando de FECHAMENTO ao Arduino")
        return self.send_command(self.CMD_FECHAR)

    def reset(self) -> bool:
        """
        Envia comando de reset/calibração.

        Returns:
            True se enviado com sucesso
        """
        logger.info("Enviando comando de RESET ao Arduino")
        return self.send_command(self.CMD_RESET)

    def __enter__(self):
        """Context manager entry."""
        if not self.is_connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def list_available_ports() -> list:
    """
    Lista todas as portas seriais disponíveis.

    Returns:
        Lista de dicionários com informações das portas
    """
    if not SERIAL_AVAILABLE:
        return []

    ports = serial.tools.list_ports.comports()
    return [
        {
            'device': p.device,
            'description': p.description,
            'hwid': p.hwid
        }
        for p in ports
    ]


