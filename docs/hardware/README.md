# Hardware — referência histórica

## Estado atual do repositório

A documentação de hardware e o firmware Arduino foram organizados anteriormente junto ao cliente IoT em **`apps/iot-device/docs/hardware/`**. Esse aplicativo e o sketch em **`arduino/cancela_control/`** **podem não existir mais** no tree atual deste repositório.

Para recuperar guias ou `.ino`, use o **histórico Git** (`git log --all --full-history -- "**/cancela_control.ino"` ou caminhos antigos sob `apps/iot-device/`).

## Papel na arquitetura SISCAV

- **API (este repo):** decisão de acesso, persistência, JWT, ingestão `POST /api/v1/access_logs/`, acionamento opcional de atuador via **`GATE_ACTUATOR_URL`** (HTTP POST JSON), configurado no servidor.
- **Borda / campo:** câmera, ALPR e hardware de portão ficam **fora** do escopo obrigatório deste repositório; integre pela API documentada em [`docs/iot/README.md`](../iot/README.md).

## Especificações (referência de projeto legado)

Quando o firmware existia no repositório, o material citava:

- Plataforma Arduino Uno R3  
- Serial UART 9600 baud  
- Componentes: servo, LEDs, resistores  

Trate como **referência**, não como caminho de arquivo válido no checkout atual.

## Documentação relacionada

- [`docs/iot/README.md`](../iot/README.md) — contrato com a API  
- [`docs/installation.md`](../installation.md) — só API e banco  
