# Guia de Montagem e Demonstração - Arduino Cancela Automatizada

Este guia fornece instruções detalhadas para montar o hardware do Arduino e realizar a demonstração do sistema de controle de cancela automatizada.

## Índice

1. [Lista de Materiais](#lista-de-materiais)
2. [Esquema de Conexões](#esquema-de-conexões)
3. [Montagem do Hardware](#montagem-do-hardware)
4. [Instalação do Software](#instalação-do-software)
5. [Carregamento do Firmware](#carregamento-do-firmware)
6. [Teste e Demonstração](#teste-e-demonstração)
7. [Troubleshooting](#troubleshooting)
8. [Checklist de Verificação](#checklist-de-verificação)

---

## Lista de Materiais

### Componentes Eletrônicos

| Componente | Quantidade | Especificações | Observações |
|------------|------------|----------------|-------------|
| Arduino Uno R3 | 1 | Microcontrolador | USB Tipo A/B para comunicação |
| Servo Motor | 1 | SG90 ou similar | Movimento 0° a 180° (usaremos 0°-90°) |
| LED Verde | 1 | 5mm | Com resistor de 220Ω |
| LED Amarelo | 1 | 5mm | Com resistor de 220Ω |
| LED Vermelho | 1 | 5mm | Com resistor de 220Ω |
| Resistores 220Ω | 3 | 1/4W | Para proteção dos LEDs |
| Protoboard | 1 | 400 pontos | Para conexões |
| Jumpers (fios) | ~15 | Macho-Macho | Para conexões |
| Fonte Externa | 1 | 5V, mínimo 2A | Para alimentar o servo (opcional, mas recomendado) |
| Cabo USB | 1 | Tipo A/B | Para comunicação e alimentação do Arduino |

### Ferramentas

- Computador com Arduino IDE instalado
- Multímetro (opcional, para verificação)
- Alicate de corte (para ajustar jumpers)

---

## Esquema de Conexões

### Diagrama de Pinagem

```
                    ARDUINO UNO
                    ┌─────────┐
                    │         │
    LED Verde ──────┤ 2 (DIG) │
    LED Amarelo ────┤ 3 (DIG) │
    LED Vermelho ───┤ 4 (DIG) │
                    │         │
                    │         │
                    │         │
    Servo (Sinal) ──┤ 9 (PWM) │
                    │         │
                    │   5V    │─── Servo (VCC) [se usar fonte externa, não conectar]
                    │   GND    │─── Servo (GND) ── GND Fonte Externa
                    │         │
                    │   USB    │─── Cabo USB para PC
                    └─────────┘
```

### Tabela de Conexões Detalhada

| Componente | Pino/Conector | Arduino | Tipo | Observações |
|------------|---------------|---------|------|-------------|
| **LED Verde** | Anodo (+) | Digital 2 | Saída | Via resistor 220Ω |
| **LED Verde** | Catodo (-) | GND | - | - |
| **LED Amarelo** | Anodo (+) | Digital 3 | Saída | Via resistor 220Ω |
| **LED Amarelo** | Catodo (-) | GND | - | - |
| **LED Vermelho** | Anodo (+) | Digital 4 | Saída | Via resistor 220Ω |
| **LED Vermelho** | Catodo (-) | GND | - | - |
| **Servo Motor** | Sinal (Laranja/Amarelo) | Digital 9 | PWM | Controle de posição |
| **Servo Motor** | VCC (Vermelho) | 5V ou Fonte Externa | Alimentação | Ver seção de alimentação |
| **Servo Motor** | GND (Marrom/Preto) | GND | Terra | GND comum com Arduino |

### Alimentação do Servo Motor

**IMPORTANTE**: O servo motor pode consumir muita corrente. Recomenda-se usar fonte externa:

- **Opção 1 (Recomendada)**: Fonte externa 5V, mínimo 2A
  - Conecte o VCC do servo na fonte externa
  - Conecte o GND do servo no GND da fonte externa
  - **CRUCIAL**: Conecte o GND da fonte externa no GND do Arduino (GND comum)
  - Deixe o VCC do servo desconectado do 5V do Arduino

- **Opção 2 (Teste apenas)**: Alimentar pelo 5V do Arduino
  - Apenas para testes rápidos
  - Pode causar instabilidade se o servo exigir muita corrente
  - Não recomendado para uso contínuo

---

## Montagem do Hardware

### Passo 1: Preparar os LEDs

1. Para cada LED (Verde, Amarelo, Vermelho):
   - Identifique o anodo (perna positiva, mais longa) e catodo (perna negativa, mais curta)
   - Conecte um resistor de 220Ω no anodo do LED
   - A outra perna do resistor será conectada ao pino digital do Arduino

### Passo 2: Montar na Protoboard

1. **LED Verde**:
   - Resistor → Pino Digital 2 do Arduino
   - Catodo do LED → GND do Arduino

2. **LED Amarelo**:
   - Resistor → Pino Digital 3 do Arduino
   - Catodo do LED → GND do Arduino

3. **LED Vermelho**:
   - Resistor → Pino Digital 4 do Arduino
   - Catodo do LED → GND do Arduino

4. **Servo Motor**:
   - Fio de sinal (geralmente laranja/amarelo) → Pino Digital 9 do Arduino
   - Fio VCC (geralmente vermelho) → 5V do Arduino OU fonte externa (recomendado)
   - Fio GND (geralmente marrom/preto) → GND do Arduino (e GND da fonte externa se usar)

### Passo 3: Verificação Visual

Antes de conectar a alimentação, verifique:

- [ ] Todos os LEDs têm resistores de 220Ω
- [ ] Catodos dos LEDs estão conectados ao GND
- [ ] Servo conectado corretamente (sinal no pino 9)
- [ ] GND comum entre Arduino e fonte externa (se usar)
- [ ] Nenhum curto-circuito visível
- [ ] Conexões firmes e bem feitas

---

## Instalação do Software

### Passo 1: Instalar Arduino IDE

1. Baixe o Arduino IDE da [página oficial](https://www.arduino.cc/en/software)
2. Instale o software no seu computador
3. Abra o Arduino IDE

### Passo 2: Instalar Biblioteca do Servo

A biblioteca `Servo.h` já vem incluída no Arduino IDE por padrão. Não é necessário instalar nada adicional.

### Passo 3: Configurar Arduino IDE

1. No menu: **Ferramentas → Placa → Arduino Uno**
2. No menu: **Ferramentas → Porta → Selecione a porta COM do seu Arduino**
   - No Windows: geralmente `COM3`, `COM4`, etc.
   - No Linux/Mac: geralmente `/dev/ttyUSB0` ou `/dev/ttyACM0`
   - Se não aparecer, verifique se o cabo USB está conectado e se os drivers estão instalados

---

## Carregamento do Firmware

### Passo 1: Abrir o Código

**IMPORTANTE**: O Arduino IDE requer que o arquivo `.ino` esteja em uma pasta com o mesmo nome do arquivo.

1. No Arduino IDE, abra o arquivo: `arduino/cancela_control/cancela_control.ino`
   - **Nota**: O arquivo está em `arduino/cancela_control/` (pasta com mesmo nome)
2. O código completo será exibido
3. **Alternativa**: Se preferir, você pode criar uma nova pasta no Arduino IDE:
   - **Arquivo → Novo** (isso cria uma pasta automaticamente)
   - Copie e cole o código do arquivo `.ino` na nova aba
   - Salve o sketch com o nome `cancela_control`

### Passo 2: Verificar Configuração da Placa

**ANTES de verificar o código**, certifique-se de que:

1. **Placa selecionada**: **Ferramentas → Placa → Arduino Uno**
   - Se não aparecer "Arduino Uno", instale os pacotes de placas:
     - **Ferramentas → Placa → Gerenciador de Placas**
     - Procure por "Arduino AVR Boards" e instale
   
2. **Porta selecionada**: **Ferramentas → Porta → [Sua porta COM]**
   - No Windows: `COM3`, `COM4`, etc.
   - No Linux/Mac: `/dev/ttyUSB0` ou `/dev/ttyACM0`
   - Se não aparecer nenhuma porta, verifique a conexão USB

### Passo 3: Verificar o Código

1. Clique no botão **Verificar** (ícone de check ✓) ou pressione `Ctrl+R` (Windows/Linux) ou `Cmd+R` (Mac)
2. Aguarde a compilação
3. **Se aparecer erro "Missing FQBN"**:
   - Verifique se a placa está selecionada (Passo 2 acima)
   - Feche e reabra o Arduino IDE
   - Tente criar um novo sketch e copiar o código
   - Verifique se o arquivo está em uma pasta com o mesmo nome

### Passo 4: Carregar no Arduino

1. **IMPORTANTE**: Certifique-se de que o hardware está montado corretamente antes de carregar
2. Clique no botão **Carregar** (ícone de seta →) ou pressione `Ctrl+U` (Windows/Linux) ou `Cmd+U` (Mac)
3. Aguarde o upload completar
4. Você verá a mensagem "Carregamento concluído" quando terminar

### Passo 4: Verificar Inicialização

Após o carregamento:

- O LED vermelho deve acender (indicando estado S0 - PRONTO/FECHADO)
- O servo deve estar na posição 0° (fechado)
- O monitor serial está pronto para receber comandos

---

## Teste e Demonstração

### Passo 1: Abrir Monitor Serial

1. No Arduino IDE: **Ferramentas → Monitor Serial** ou pressione `Ctrl+Shift+M` (Windows/Linux) ou `Cmd+Shift+M` (Mac)
2. Configure para:
   - **Velocidade**: 9600 baud (canto inferior direito do monitor serial)
   - **Terminação**: Nenhuma (ou Nova Linha)
   - **Importante**: Certifique-se de que o Arduino está conectado e a porta está selecionada

### Passo 2: Teste dos Estados da FSM

#### Teste 1: Abrir Cancela (Comando 'A')

1. No monitor serial, digite: `A` e pressione Enter
2. **Comportamento esperado**:
   - LED amarelo acende (S1 - ABRINDO)
   - Servo move gradualmente de 0° para 90°
   - Quando servo atinge 90°: LED verde acende (S2 - ABERTO)
   - Após 5 segundos: LED amarelo pisca e servo fecha (S3 - FECHANDO)
   - Quando servo atinge 0°: LED vermelho acende (S0 - PRONTO/FECHADO)

#### Teste 2: Negar Acesso (Comando 'N')

1. Certifique-se de que está no estado S0 (LED vermelho ligado)
2. No monitor serial, digite: `N` e pressione Enter
3. **Comportamento esperado**:
   - LED vermelho pisca rapidamente (S5 - NEGADO/ERRO)
   - Servo permanece em 0°
   - Após 2 segundos: retorna ao S0 (LED vermelho ligado)

#### Teste 3: Fechamento Forçado (Comando 'F')

1. Envie comando 'A' para abrir a cancela
2. Aguarde o estado S2 (LED verde ligado, cancela aberta)
3. Antes dos 5 segundos, digite: `F` e pressione Enter
4. **Comportamento esperado**:
   - Imediatamente: LED amarelo pisca e servo começa a fechar (S3 - FECHANDO)
   - Quando servo atinge 0°: LED vermelho acende (S0 - PRONTO/FECHADO)

#### Teste 4: Reset/Calibração (Comando 'Z')

1. Envie qualquer comando para alterar o estado
2. Digite: `Z` e pressione Enter
3. **Comportamento esperado**:
   - Imediatamente: sistema retorna ao S0
   - LED vermelho ligado
   - Servo move para 0° (se não estiver)

### Passo 3: Demonstração Completa

Para uma demonstração completa, execute na seguinte ordem:

1. **Inicialização**: Sistema inicia em S0 (LED vermelho ligado)
2. **Autorização**: Envie 'A' → Cancela abre (LED amarelo → verde)
3. **Espera**: Aguarde 5 segundos → Cancela fecha automaticamente
4. **Negação**: Envie 'N' → Feedback de erro (LED vermelho piscando rápido)
5. **Reset**: Envie 'Z' → Sistema retorna ao estado inicial

### Passo 4: Integração com Sistema de Reconhecimento de Placas (SISCAV)

O sistema SISCAV já está integrado com o Arduino. Quando uma placa é detectada pela webcam e autorizada pela API, o Arduino recebe automaticamente o comando de abertura.

#### Configuração da Integração

1. **Instalar dependências do dispositivo IoT**:

```powershell
# Navegar para o diretório do dispositivo IoT
cd C:\src\personal\siscav-api\apps\iot-device

# Ativar o ambiente virtual do dispositivo IoT
.\venv\Scripts\Activate.ps1

# Instalar dependências necessárias
pip install pyserial                    # Comunicação com Arduino
pip uninstall opencv-python-headless -y # Remover versão sem GUI
pip install opencv-python               # Instalar versão com GUI (para webcam)
```

2. **Configurar variáveis de ambiente** (opcional):

```powershell
# Porta do Arduino (se não especificada, detecta automaticamente)
$env:ARDUINO_PORT="COM3"

# Habilitar/desabilitar Arduino (padrão: true)
$env:ARDUINO_ENABLED="true"

# URL da API (padrão: localhost:8000)
$env:API_BASE_URL="http://localhost:8000/api/v1"
```

3. **Executar o sistema integrado**:

```powershell
# Certifique-se de que o Arduino está conectado e com o firmware carregado
cd C:\src\personal\siscav-api\apps\iot-device
.\venv\Scripts\Activate.ps1
python run.py
```

#### Fluxo de Operação Integrado

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Webcam    │───▶│    OCR      │───▶│    API      │───▶│   Arduino   │
│ (Detecção)  │    │ (Leitura)   │    │(Autorização)│    │  (Cancela)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │ Authorized? │
                                     └──────┬──────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │                 │                 │
                          ▼                 ▼                 ▼
                    ┌──────────┐     ┌──────────┐     ┌──────────┐
                    │  Sim: A  │     │  Não: N  │     │ Erro: -  │
                    │ (Abre)   │     │ (Nega)   │     │(Ignora)  │
                    └──────────┘     └──────────┘     └──────────┘
```

1. **Webcam** captura frames continuamente
2. **Detecção de placa** identifica regiões de placa no frame
3. **OCR (EasyOCR)** extrai o texto da placa
4. **API** verifica se a placa está autorizada no sistema
5. **Arduino** recebe comando baseado na resposta:
   - `'A'` (Authorized): Abre a cancela
   - `'N'` (Denied): Feedback de negação

#### Teste Manual com Python

Para testar a comunicação diretamente com o Arduino:

```python
import serial
import time

# Conectar ao Arduino (ajuste a porta COM)
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Aguardar inicialização

# Enviar comando de abertura
arduino.write(b'A')
print("Comando de abertura enviado")

# Aguardar operação
time.sleep(10)

# Fechar conexão
arduino.close()
```

#### Demonstração Completa do Sistema

Para uma demonstração completa:

1. **Inicie a API** (Terminal 1):
   ```powershell
   cd C:\src\personal\siscav-api
   .\venv\Scripts\Activate.ps1
   uvicorn apps.api.src.main:app --reload
   ```
   Aguarde a mensagem: `Uvicorn running on http://127.0.0.1:8000`

2. **Conecte o Arduino** via USB e carregue o firmware (`arduino/cancela_control/cancela_control.ino`)

3. **Execute o dispositivo IoT** (Terminal 2):
   ```powershell
   cd C:\src\personal\siscav-api\apps\iot-device
   .\venv\Scripts\Activate.ps1
   python run.py
   ```
   Aguarde a mensagem: `ARDUINO CONECTADO COM SUCESSO`

4. **Mostre uma placa para a webcam**:
   - Se a placa estiver cadastrada e autorizada → cancela abre (LED verde)
   - Se a placa não estiver autorizada → feedback de erro (LED vermelho piscando)

**Nota**: Se o OCR (EasyOCR) não estiver disponível, o sistema funcionará apenas com detecção visual. Para testar o Arduino manualmente, use o Monitor Serial do Arduino IDE e envie os comandos 'A', 'N', 'F', 'Z'.

---

## Troubleshooting

### Problema: Arduino não aparece na porta COM

**Soluções**:
- Verifique se o cabo USB está conectado corretamente
- Tente outra porta USB do computador
- Instale os drivers USB do Arduino (geralmente automático no Windows 10+)
- No Linux, pode ser necessário adicionar usuário ao grupo `dialout`: `sudo usermod -a -G dialout $USER`

### Problema: Erro "Missing FQBN" (Fully Qualified Board Name)

**Este é um erro comum que ocorre quando a placa não está selecionada corretamente.**

**Soluções**:
1. **Selecione a placa explicitamente**:
   - **Ferramentas → Placa → Arduino Uno**
   - Se "Arduino Uno" não aparecer na lista:
     - **Ferramentas → Placa → Gerenciador de Placas**
     - Procure por "Arduino AVR Boards"
     - Clique em "Instalar"
     - Aguarde a instalação completar
     - Feche e reabra o Arduino IDE

2. **Verifique a estrutura do arquivo**:
   - O arquivo `.ino` deve estar em uma pasta com o mesmo nome
   - Exemplo: `cancela_control/cancela_control.ino` ✓
   - Não: `cancela_control.ino` (sem pasta) ✗

3. **Tente criar um novo sketch**:
   - **Arquivo → Novo**
   - Copie todo o código do arquivo `.ino`
   - Cole na nova aba
   - Salve como `cancela_control` (o IDE criará a pasta automaticamente)

4. **Reinicie o Arduino IDE** após fazer as alterações acima

### Problema: Erro ao carregar o código

**Soluções**:
- Verifique se a placa selecionada é "Arduino Uno" (veja solução acima)
- Verifique se a porta COM está correta
- Tente desconectar e reconectar o cabo USB
- Feche outros programas que possam estar usando a porta serial
- Certifique-se de que o arquivo está em uma pasta com o mesmo nome

### Problema: LEDs não acendem

**Soluções**:
- Verifique se os LEDs estão conectados corretamente (anodo/catodo)
- Verifique se os resistores de 220Ω estão conectados
- Teste os LEDs individualmente conectando diretamente no 5V e GND (com resistor)
- Verifique se os pinos estão corretos (2, 3, 4)

### Problema: Servo não se move

**Soluções**:
- Verifique se o fio de sinal está no pino 9
- Verifique a alimentação do servo (5V ou fonte externa)
- Verifique se o GND está conectado corretamente
- Teste o servo diretamente com um código simples
- Se usar fonte externa, certifique-se de que o GND está comum com o Arduino

### Problema: Servo treme ou não mantém posição

**Soluções**:
- Use fonte externa dedicada (5V, mínimo 2A)
- Verifique se o GND da fonte externa está conectado ao GND do Arduino
- Verifique se a fonte externa fornece corrente suficiente

### Problema: Comandos serial não funcionam

**Soluções**:
- Verifique se o baud rate está configurado para 9600
- Verifique se está enviando apenas um caractere por vez ('A', 'N', 'F', 'Z')
- Certifique-se de que não há caracteres extras (espaços, quebras de linha)
- Feche e reabra o monitor serial
- Verifique se o Arduino está recebendo energia (LED onboard deve piscar)

### Problema: Estados não transicionam corretamente

**Soluções**:
- Verifique se o código foi carregado corretamente
- Recarregue o firmware no Arduino
- Verifique se os temporizadores estão funcionando (5s para S2, 2s para S5)
- Envie comando 'Z' para resetar o sistema

### Problema: Arduino não detectado pelo sistema Python

**Soluções**:
- Verifique se o Arduino está conectado via USB
- Verifique se o firmware foi carregado corretamente
- Feche o Monitor Serial do Arduino IDE (ele bloqueia a porta)
- Especifique a porta manualmente: `$env:ARDUINO_PORT="COM3"`
- Verifique portas disponíveis no Gerenciador de Dispositivos do Windows

### Problema: OpenCV não exibe janela da webcam

**Soluções**:
- Instale a versão correta do OpenCV:
  ```powershell
  pip uninstall opencv-python-headless -y
  pip install opencv-python
  ```
- Verifique se a webcam está funcionando em outros aplicativos

### Problema: Erro "No module named 'apps.iot_device'"

**Soluções**:
- Use o script `run.py` em vez de executar diretamente:
  ```powershell
  cd C:\src\personal\siscav-api\apps\iot-device
  .\venv\Scripts\Activate.ps1
  python run.py
  ```

### Problema: Erro "uvicorn não reconhecido"

**Soluções**:
- Ative o ambiente virtual antes de executar:
  ```powershell
  cd C:\src\personal\siscav-api
  .\venv\Scripts\Activate.ps1
  uvicorn apps.api.src.main:app --reload
  ```

---

## Checklist de Verificação

### Antes da Montagem

- [ ] Todos os componentes estão disponíveis
- [ ] Arduino IDE instalado
- [ ] Protoboard e jumpers disponíveis
- [ ] Ferramentas necessárias (alicate, multímetro)

### Após a Montagem

- [ ] LEDs conectados com resistores de 220Ω
- [ ] Servo conectado no pino 9
- [ ] GND comum entre todos os componentes
- [ ] Alimentação do servo verificada (5V ou fonte externa)
- [ ] Nenhum curto-circuito visível
- [ ] Conexões firmes e bem feitas

### Após o Carregamento do Firmware

- [ ] Código compilado sem erros
- [ ] Firmware carregado com sucesso
- [ ] LED vermelho acende na inicialização (S0)
- [ ] Servo na posição 0° (fechado)

### Testes Funcionais

- [ ] Comando 'A' abre a cancela corretamente
- [ ] LED amarelo acende durante abertura (S1)
- [ ] LED verde acende quando aberto (S2)
- [ ] Cancela fecha automaticamente após 5 segundos
- [ ] LED amarelo pisca durante fechamento (S3)
- [ ] Comando 'N' ativa estado de erro (S5)
- [ ] LED vermelho pisca rapidamente no estado de erro
- [ ] Comando 'F' fecha a cancela imediatamente
- [ ] Comando 'Z' reseta o sistema corretamente
- [ ] Monitor serial funciona corretamente

### Para Demonstração

- [ ] Hardware montado e funcionando
- [ ] Todos os testes passaram
- [ ] Código de exemplo Python pronto (se aplicável)
- [ ] Documentação de referência disponível
- [ ] Backup do código fonte salvo

---

## Informações Adicionais

### Especificações Técnicas

- **Baud Rate**: 9600 bps
- **Formato Serial**: 8N1 (8 bits, sem paridade, 1 bit de parada)
- **Velocidade do Servo**: 2 graus por iteração (ajustável no código)
- **Temporizador S2**: 5000ms (5 segundos)
- **Temporizador S5**: 2000ms (2 segundos)
- **Intervalo de piscar normal**: 500ms
- **Intervalo de piscar rápido**: 200ms

### Estados da FSM

| Estado | Nome | LED | Servo | Duração |
|--------|------|-----|-------|---------|
| S0 | PRONTO/FECHADO | Vermelho Ligado | 0° | Indefinido |
| S1 | ABRINDO | Amarelo Ligado | 0° → 90° | ~2-3 segundos |
| S2 | ABERTO | Verde Ligado | 90° | 5 segundos |
| S3 | FECHANDO | Amarelo Piscando | 90° → 0° | ~2-3 segundos |
| S5 | NEGADO/ERRO | Vermelho Piscando Rápido | 0° | 2 segundos |

### Comandos Serial

| Comando | ASCII | Ação | Estado Válido |
|---------|-------|------|---------------|
| 'A' | 65 | Abrir/Autorizar | S0 → S1 |
| 'N' | 78 | Negar Acesso | S0 → S5 |
| 'F' | 70 | Fechamento Forçado | S2 → S3 |
| 'Z' | 90 | Reset/Calibração | Qualquer → S0 |

---

## Suporte e Referências

- **Documentação do Projeto**: `docs/hardware/arduino-project-definition.md`
- **Código Fonte Arduino**: `arduino/cancela_control/cancela_control.ino`
- **Serviço Arduino (Python)**: `apps/iot-device/services/arduino.py`
- **Script de Execução IoT**: `apps/iot-device/run.py`
- **Arduino IDE**: https://www.arduino.cc/en/software
- **Biblioteca Servo**: https://www.arduino.cc/reference/en/libraries/servo/
- **PySerial**: https://pyserial.readthedocs.io/

---

**Última atualização**: Versão simplificada sem sensor ultrassônico e buzzer, com integração webcam/Arduino

