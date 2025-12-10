# Hardware Documentation

**Nota**: A documentação de hardware foi reorganizada e movida para `apps/iot-device/docs/hardware/`.

Consulte a documentação atualizada em:
- [Documentação de Hardware](../../apps/iot-device/docs/hardware/)

## Documentos Movidos

A documentação de hardware foi movida para ficar próxima ao código do dispositivo IoT:

- Hardware/Arduino: `apps/iot-device/docs/hardware/`
  - `arduino.md` - Documentação do firmware Arduino
  - `project-definition.md` - Definição do projeto Arduino
  - `assembly-guide.md` - Guia de montagem e demonstração

## Especificações Técnicas

- **Plataforma**: Arduino Uno R3
- **Comunicação**: Serial UART 9600 baud
- **Estados FSM**: 5 estados (S0, S1, S2, S3, S5)
- **Componentes**: Servo Motor, 3 LEDs, 3 resistores 220Ω
- **Versão**: Simplificada (sem sensor ultrassônico e buzzer)

## Referências

- [Código Fonte](../../arduino/cancela_control/cancela_control.ino): Firmware implementado
- [Documentação de Operação](../operations/README.md): Guias operacionais
