"""Aplicação principal do dispositivo IoT para reconhecimento de placas."""

import logging
import sys
import time
from typing import Optional

import cv2
import numpy as np

from apps.iot_device.config import (
    ARDUINO_BAUD_RATE,
    ARDUINO_ENABLED,
    ARDUINO_PORT,
    DEMO_MODE,
    DEMO_WHITELIST,
    ENABLE_DISPLAY,
    ENABLE_SOUND,
    LOG_LEVEL,
    MAX_RUNTIME_SECONDS,
    PLATE_DETECTION_COOLDOWN,
)
from apps.iot_device.services.api_client import APIClient
from apps.iot_device.services.arduino import ArduinoService
from apps.iot_device.services.camera import CameraService
from apps.iot_device.services.ocr import OCRService
from apps.iot_device.services.plate_detector import PlateDetector
from apps.iot_device.utils.debounce import PlateDebouncer

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def play_sound(frequency: int, duration: int) -> None:
    """
    Toca um som de notificação.

    Args:
        frequency: Frequência em Hz
        duration: Duração em milissegundos
    """
    if not ENABLE_SOUND:
        return

    try:
        import winsound

        winsound.Beep(frequency, duration)
    except ImportError:
        logger.warning("winsound não disponível (sistema não Windows)")


def draw_detection(
    frame: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    plate_text: str,
    status: str,
    vehicle_type: str,
) -> None:
    """
    Desenha informações da detecção no frame.

    Args:
        frame: Frame BGR
        x, y, w, h: Coordenadas e dimensões da placa
        plate_text: Texto da placa extraído pelo OCR
        status: Status da autorização
        vehicle_type: Tipo de veículo
    """
    # Cor da caixa: verde para carro, amarelo para moto
    color_box = (0, 255, 0) if vehicle_type == "carro" else (0, 255, 255)

    # Cor do texto baseado no status
    if status == "Authorized":
        text_color = (0, 255, 0)  # Verde
        bg_color = (0, 100, 0)  # Verde escuro para fundo
    elif status == "Denied":
        text_color = (0, 0, 255)  # Vermelho
        bg_color = (0, 0, 100)  # Vermelho escuro para fundo
    else:
        text_color = (255, 255, 255)  # Branco
        bg_color = (50, 50, 50)  # Cinza escuro para fundo

    # Desenhar retângulo ao redor da placa (mais espesso para destaque)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color_box, 3)

    # Desenhar fundo para o texto (melhor legibilidade)
    label_plate = f"PLACA: {plate_text}"
    label_status = f"STATUS: {status}"
    
    # Calcular tamanho do texto para criar fundo
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    
    (text_width_plate, text_height_plate), _ = cv2.getTextSize(
        label_plate, font, font_scale, thickness
    )
    (text_width_status, text_height_status), _ = cv2.getTextSize(
        label_status, font, font_scale, thickness
    )
    
    # Desenhar fundo retangular para o texto
    padding = 5
    bg_y1 = max(0, y - text_height_plate - text_height_status - padding * 3)
    bg_y2 = y - 5
    bg_x1 = max(0, x - padding)
    bg_x2 = min(frame.shape[1], x + max(text_width_plate, text_width_status) + padding)
    
    cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_color, -1)
    
    # Desenhar texto da placa extraída (destaque principal)
    cv2.putText(
        frame,
        label_plate,
        (x, y - text_height_status - padding),
        font,
        font_scale,
        text_color,
        thickness,
    )
    
    # Desenhar status
    cv2.putText(
        frame,
        label_status,
        (x, y - padding),
        font,
        font_scale,
        text_color,
        thickness,
    )


def process_plate_detection(
    frame: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    ocr_service: Optional[OCRService],
    api_client: APIClient,
    debouncer: PlateDebouncer,
    arduino_service: Optional[ArduinoService] = None,
) -> Optional[str]:
    """
    Processa uma detecção de placa: OCR, validação, envio para API e controle do Arduino.

    Args:
        frame: Frame completo
        x, y, w, h: Coordenadas da placa
        ocr_service: Serviço OCR
        api_client: Cliente da API
        debouncer: Sistema de debounce
        arduino_service: Serviço de comunicação com Arduino (opcional)

    Returns:
        Status da autorização ou None se não processado
    """
    # Extrair região da placa
    plate_region = frame[y : y + h, x : x + w]

    # Determinar tipo de veículo pela proporção
    vehicle_type = "carro" if w > h else "moto"

    # Pré-processar e ler placa (se OCR disponível)
    if ocr_service is None:
        # Sem OCR, apenas mostrar detecção visual
        plate_text = None
        color = "desconhecida"
        logger.info(f"Região de placa detectada (sem OCR): {x}, {y}, {w}, {h}")
    else:
        plate_processed, color = ocr_service.preprocess_plate(plate_region, vehicle_type)
        plate_text = ocr_service.read_plate(plate_processed)

    if not plate_text:
        # Se não há texto detectado, ainda mostrar a detecção visual
        if ENABLE_DISPLAY:
            draw_detection(frame, x, y, w, h, "DETECTADO", "Aguardando OCR", vehicle_type)
        return None

    # Verificar debounce
    if not debouncer.should_process(plate_text):
        logger.debug(f"Placa {plate_text} em cooldown, ignorando")
        return None

    # Log detalhado do conteúdo extraído
    logger.info("=" * 60)
    logger.info("EXTRACAO DE PLACA CONCLUIDA")
    logger.info(f"  Conteudo extraido: {plate_text}")
    logger.info(f"  Tipo de placa: {color}")
    logger.info(f"  Tipo de veiculo: {vehicle_type}")
    logger.info(f"  Coordenadas: x={x}, y={y}, w={w}, h={h}")
    logger.info("=" * 60)

    # Normalizar placa para comparação (remover hífens, espaços, converter para maiúsculas)
    normalized_plate = "".join(c for c in plate_text if c.isalnum()).upper()
    
    # Verificar autorização
    status = "Unknown"
    
    if DEMO_MODE:
        # Modo demonstração: verificar whitelist local
        logger.info("[DEMO MODE] Verificando whitelist local...")
        if normalized_plate in DEMO_WHITELIST:
            status = "Authorized"
            logger.info(f"[DEMO MODE] Placa {normalized_plate} AUTORIZADA (whitelist local)")
        else:
            status = "Denied"
            logger.info(f"[DEMO MODE] Placa {normalized_plate} NEGADA (não está na whitelist)")
    else:
        # Modo normal: enviar para API
        response = api_client.send_access_log(plate_text, plate_region)
        if response:
            status = response.get("status", "Unknown")
    
    logger.info("=" * 60)
    logger.info("RESULTADO DA VALIDACAO")
    logger.info(f"  Placa extraida: {plate_text}")
    logger.info(f"  Placa normalizada: {normalized_plate}")
    logger.info(f"  Status: {status}")
    if DEMO_MODE:
        logger.info(f"  Modo: DEMONSTRACAO (whitelist local)")
        logger.info(f"  Placas autorizadas: {DEMO_WHITELIST}")
    logger.info("=" * 60)

    # Tocar som baseado no status
    if status == "Authorized":
        play_sound(1000, 200)  # Som de sucesso
        # Enviar comando de abertura para o Arduino
        if arduino_service and arduino_service.is_connected:
            logger.info(">>> ENVIANDO COMANDO DE ABERTURA AO ARDUINO <<<")
            arduino_service.abrir_cancela()
    elif status == "Denied":
        play_sound(500, 500)  # Som de negação
        # Enviar comando de negação para o Arduino
        if arduino_service and arduino_service.is_connected:
            logger.info(">>> ENVIANDO COMANDO DE NEGAÇÃO AO ARDUINO <<<")
            arduino_service.negar_acesso()

    # Desenhar no frame
    if ENABLE_DISPLAY:
        draw_detection(frame, x, y, w, h, plate_text, status, vehicle_type)

    return status


def main() -> None:
    """Função principal da aplicação."""
    logger.info("Iniciando dispositivo IoT SISCAV")
    
    # Log do modo de operação
    if DEMO_MODE:
        logger.info("=" * 60)
        logger.info(">>> MODO DEMONSTRACAO ATIVO <<<")
        logger.info("Usando whitelist local (não requer API/banco de dados)")
        logger.info(f"Placas autorizadas: {DEMO_WHITELIST}")
        logger.info("=" * 60)

    # Inicializar serviços
    arduino_service = None
    try:
        camera = CameraService()
        plate_detector = PlateDetector()
        api_client = APIClient()
        debouncer = PlateDebouncer(cooldown_seconds=PLATE_DETECTION_COOLDOWN)
        
        # Tentar inicializar OCR, mas continuar sem ele se não estiver disponível
        try:
            ocr_service = OCRService()
            ocr_available = True
            logger.info("OCR (EasyOCR) inicializado com sucesso")
        except ImportError as e:
            ocr_service = None
            ocr_available = False
            logger.warning(f"OCR não disponível: {e}")
            logger.warning("Sistema funcionará apenas com detecção visual (sem reconhecimento de texto)")
        
        # Tentar inicializar Arduino, mas continuar sem ele se não estiver disponível
        if ARDUINO_ENABLED:
            try:
                arduino_service = ArduinoService(
                    port=ARDUINO_PORT,
                    baud_rate=ARDUINO_BAUD_RATE,
                    auto_connect=True
                )
                if arduino_service.is_connected:
                    logger.info("=" * 60)
                    logger.info("ARDUINO CONECTADO COM SUCESSO")
                    logger.info(f"  Porta: {arduino_service.port}")
                    logger.info(f"  Baud Rate: {ARDUINO_BAUD_RATE}")
                    logger.info("=" * 60)
                else:
                    logger.warning("Arduino habilitado mas não conectado")
                    arduino_service = None
            except ImportError as e:
                logger.warning(f"pyserial não instalado: {e}")
                logger.warning("Execute: pip install pyserial")
                arduino_service = None
            except Exception as e:
                logger.warning(f"Erro ao conectar Arduino: {e}")
                logger.warning("Sistema funcionará sem controle de cancela")
                arduino_service = None
        else:
            logger.info("Arduino desabilitado nas configurações (ARDUINO_ENABLED=false)")
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {e}")
        sys.exit(1)

    logger.info("Serviços inicializados com sucesso")
    start_time = time.time()

    try:
        frame_skip = 2  # Processar apenas 1 a cada 3 frames para melhor performance
        frame_count = 0
        
        while True:
            # Ler frame da câmera
            try:
                frame = camera.read_frame()
            except RuntimeError as e:
                logger.error(f"Erro ao ler frame: {e}")
                break

            frame_count += 1
            
            # Processar apenas alguns frames para melhor performance
            if frame_count % (frame_skip + 1) == 0:
                # Detectar placas no frame
                plate_candidates = plate_detector.detect_plates(frame)

                # Processar cada candidato
                for x, y, w, h in plate_candidates:
                    process_plate_detection(
                        frame, x, y, w, h, ocr_service, api_client, debouncer, arduino_service
                    )

            # Exibir frame se habilitado (sempre mostrar para feedback visual)
            if ENABLE_DISPLAY:
                cv2.imshow("SISCAV IoT Device - Reconhecimento de Placas", frame)

                # Verificar tecla ESC para sair (timeout menor para melhor responsividade)
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    logger.info("Tecla ESC pressionada, encerrando")
                    break

            # Verificar tempo máximo de execução
            if MAX_RUNTIME_SECONDS > 0 and time.time() - start_time > MAX_RUNTIME_SECONDS:
                logger.info("Tempo máximo de execução atingido")
                break

    except KeyboardInterrupt:
        logger.info("Interrupção pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante execução: {e}", exc_info=True)
    finally:
        # Limpar recursos
        camera.release()
        if ENABLE_DISPLAY:
            cv2.destroyAllWindows()
        # Desconectar Arduino
        if arduino_service:
            arduino_service.disconnect()
            logger.info("Arduino desconectado")
        logger.info("Aplicação finalizada")


if __name__ == "__main__":
    main()
