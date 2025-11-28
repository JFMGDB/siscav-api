# Documentação do Dispositivo IoT

Esta pasta contém a documentação relacionada ao dispositivo IoT que realiza o reconhecimento automático de placas.

## Índice

1. [Refatoração do Dispositivo IoT](./01-refatoracao-dispositivo-iot.md)
   - Problemas identificados e corrigidos
   - Melhorias implementadas
   - Arquitetura refatorada
   - Princípios SOLID, DRY e Componentização aplicados
   - Decisões de design

2. [Resumo Executivo - Dispositivo IoT](./02-resumo-dispositivo-iot.md)
   - Visão geral das melhorias
   - Métricas de melhoria
   - Estrutura de arquivos
   - Fluxo de processamento
   - Configuração para demonstração

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

