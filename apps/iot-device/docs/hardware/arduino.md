# Firmware Arduino - Controle de Cancela Automatizada

Este diretório contém o firmware do Arduino Uno para o sistema de controle de cancela automatizada do projeto SISCAV.

## Arquivos

- **`cancela_control.ino`**: Código principal do firmware
- **`README.md`**: Este arquivo

## Documentação

Para instruções completas de montagem, instalação e demonstração, consulte:

- **[Guia de Montagem e Demonstração](../docs/arduino/01-guia-montagem-demonstracao.md)**: Instruções detalhadas passo a passo

## Especificações

- **Plataforma**: Arduino Uno R3
- **Comunicação**: Serial UART (9600 baud)
- **Estados FSM**: 5 estados (S0, S1, S2, S3, S5)
- **Componentes**: Servo Motor, 3 LEDs (Verde, Amarelo, Vermelho)

## Quick Start

1. Abra `cancela_control/cancela_control.ino` no Arduino IDE
   - **Importante**: O arquivo deve estar em uma pasta com o mesmo nome
2. Selecione a placa: **Ferramentas → Placa → Arduino Uno**
   - Se não aparecer, instale "Arduino AVR Boards" pelo Gerenciador de Placas
3. Selecione a porta: **Ferramentas → Porta → [Sua porta COM]**
4. Clique em **Verificar** (✓) para compilar
5. Clique em **Carregar** (→) para enviar ao Arduino
6. Abra o Monitor Serial (9600 baud) e envie comandos: 'A', 'N', 'F', 'Z'

**Nota**: Se aparecer erro "Missing FQBN", verifique se a placa está selecionada corretamente.

## Comandos Serial

- **'A'**: Abrir/Autorizar (S0 → S1)
- **'N'**: Negar Acesso (S0 → S5)
- **'F'**: Fechamento Forçado (S2 → S3)
- **'Z'**: Reset/Calibração (Qualquer → S0)

## Requisitos

- Arduino IDE 1.8.x ou superior
- Biblioteca Servo (incluída por padrão no Arduino IDE)
- Hardware: Arduino Uno, Servo Motor, 3 LEDs, 3 resistores 220Ω

## Versão

Versão simplificada sem sensor ultrassônico e buzzer.

