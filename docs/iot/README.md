# Documentação do Dispositivo IoT

**Nota**: A documentação do dispositivo IoT foi reorganizada e movida para `apps/iot-device/docs/`.

Consulte a documentação atualizada em:
- [Documentação do Dispositivo IoT](../../apps/iot-device/docs/README.md)

## Documentos Movidos

A documentação foi reorganizada para ficar próxima ao código-fonte:

- Documentação principal: `apps/iot-device/docs/`
- Hardware/Arduino: `apps/iot-device/docs/hardware/`
- Documentos arquivados: `apps/iot-device/docs/archive/`

## Descrição

O dispositivo IoT é responsável por:

- Captura de imagens de veículos via câmera
- Detecção de regiões candidatas a placas
- Extração de texto via OCR (EasyOCR)
- Validação de formato de placas brasileiras
- Comunicação com a API central
- Sistema de debounce para evitar processamento duplicado

## Componentes Principais

- **CameraService**: Gerenciamento de captura de vídeo
- **PlateDetector**: Detecção de regiões candidatas
- **OCRService**: Processamento OCR
- **APIClient**: Comunicação com API
- **PlateDebouncer**: Prevenção de duplicatas
- **PlateValidator**: Validação de formatos brasileiros

## Tecnologias

- Python 3.10+
- OpenCV para processamento de imagem
- EasyOCR para reconhecimento de texto
- Requests para comunicação HTTP













