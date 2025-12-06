## DEFINIÇÃO DE PROJETO TÓPICOS AVANÇADOS EM DESENVOLVIMENTO WEB

## (WEB 3.0): SUBSISTEMA DE CONTROLE DE CANCELA AUTOMATIZADA

**1. Resumo do Projeto**
    Como parte da avaliação da disciplina de Web 3.0 do professor e orientador
Daniel Bezerra, este documento tem a finalidade de especificar o projeto que será
desenvolvido: a materialização de um sistema de controle de acesso veicular, em que o
software munido de visão computacional será responsável por identificar e autorizar a
entrada de veículos, através de controle remoto que enviará comando de abertura e
fechamento para o microcomputador Arduino.
    A função primária é traduzir a decisão de software do mestre (Autorizado ou
Negado) em movimentos mecânicos precisos do servomotor e em _feedback_ claro para
o usuário através de dispositivos visuais e sonoros.
    Destaca-se o caráter de dispositivo escravo de controle de I/O que terá como
função primária traduzir a decisão do software mestre, que poderá ser autorizado ou
negado, em movimentos mecânicos do servomotor e em feedback claro para o usuário
através de leds.
    Como protocolo de integração, adota-se a comunicação serial UART por sua
simplicidade e menor complexidade para troca de dados entre o microcontrolador e o
servidor central.
**1.1 Objetivos**
    1. O sistema deve inicializar e manter uma comunicação serial estável com o
       computador central e ser capaz de receber e decodificar comandos de abertura e
       fechamento sem perda de dados.^
    2. Deve-se controlar o servomotor para realizar a movimentação angular da cancela:
       0º para a posição Fechada e 90º para a posição Aberta.
    3. Identificar a aproximação de veículos via sensor ultrassônico para iniciar a


```
verificação da placa e acionamento dos portões.
```
4. O _firmware_ deve gerenciar de maneira não-bloqueante o estado operacional do
    sistema (Pronto, Abrindo, Aberto, Fechando, Obstrução), fornecendo _feedback_
    instantâneo e inequívoco através dos LEDs de semáforo e do Buzzer.
**2. Escopo e Definição
Incluído Excluído**
Implementação do Protocolo de Comunicação
Serial (UART)
Processamento de Imagem ou OCR (easyOCR)
Controle de Posição e Velocidade do
Servomotor
Conexão de Rede (Wi-Fi, Ethernet ou IoT)
Gerenciamento da Lógica de Máquina de
Estados Finitos para Estados da Cancela
Servir como Unidade Mestre de Decisão
Leitura e Processamento do Sensor
Ultrassônico de Segurança
Controle de Múltiplas Cancelas (limitado pelo
Uno)^
**2.2 Diagrama de Blocos do Sistema Integrado**
Abaixo o fluxo de dados e controle:
1. **easyOCR:** ponto de decisão, onde a imagem é processada, a placa é identificada
e a autorização é verificada.
2. **PySerial:** utiliza-se a biblioteca PySerial para enviar o comando de caractere único
através do cabo USB, que emulará a comunicação UART.^
3. **Arduino Uno:** Recebe e lê o Comando Serial que é o gatilho que altera o Estado
da FSM. A lógica interna então comanda os atuadores e monitora o sensor.
4. **Servo Motor:** movimenta o braço da cancela.
5. **Sensor Ultrassônico:** mede continuamente a distância, fornecendo o _feedback_ de
segurança necessário ao _firmware_.
6. **LEDs (Semáforo):** comunicam o estado atual do sistema ao usuário.


**2.3 Dispositivos de Feedback**
Para fornecer informações claras sobre o estado do sistema aos usuários, será
implementado um sistema de semáforo simplificado e sinalização sonora.
● **LED Vermelho:** Fechado (S0) ou uma condição de erro/negação de acesso (S5).
● **LED Verde:** Aberto (S2) e passagem autorizada.
● **LED Amarelo:** transição (S1 - Abrindo e S3 - Fechando), sistema está em
movimento.^
O _feedback_ não deve comprometer a reatividade do sistema. O controle de LEDs será
gerenciado por lógica não bloqueante (utilizando _millis()_ ) para evitar paralisação do
loop() e interferência na leitura do sensor ultrassônico.


**2.4 Lista de Materiais e Especificações de Hardware
Componente Modelo Sugerido Função Principal Requisito
Elétrico/Nota**
Microcontrolador Arduino Uno R3 Processamento
central, I/O
USB
Atuador da Cancela Servo Motor Movimento angular
0º/90º
Requer fonte externa
dedicada (4.8V –
7.2V) para torque
adequado.^
Sensor de Segurança Ultrassônico Medição de distância
e segurança anti
obstrução
Alimentado pelo 5V
do Arduino.
Feedback Visual 3x LEDs (Verde,
Amarelo, Vermelho)
Status do semáforo e
FSM
Resistores de 220Ω
Ohms^
Alimentação Externa Fonte DC 5V, mínimo
2A
Energia dedicada ao
Servo
GND comum com o
Arduino.
Interface Cabo USB Tipo A/B Comunicação Serial
Mestre-Escravo
Conexão para
programação e
comunicação de
dados.
**2.5 Detalhamento do Protocolo UART**
A comunicação será implementada utilizando a biblioteca Serial nativa do Arduino, que
se baseia no protocolo UART (Universal Asynchronous Receiver/Transmitter).^1
**Padrões de Comunicação:**
● **Inicialização:** Serial.begin(9600); na função setup() para inicializar o hardware
serial e definir a taxa de transmissão.^
● **Baud Rate (velocidade):** 9600 bps (bits por segundo).^
● **Formato de Transmissão:** 8N1 (8 bits de dados, Sem Paridade, 1 Bit de Parada).^
**2.6 Mapeamento de Comandos Seriais**
Os seguintes caracteres ASCII são definidos como os comandos operacionais da


interface Mestre-Escravo:
**Comando Recebido
(PC → Arduino)
Valor ASCII
(Decimal)
Ação na FSM Descrição**
'A' (Abrir/Autorizar) 65 Transição para S1 Autorização de
acesso concedida.
Inicia abertura da
cancela.
'N' (Negar Acesso) 78 Transição para S5 Autorização negada
(placa não
reconhecida/não
autorizada).
'F' (Fechamento
Manual/Forçado)
70 Transição para S3 Comando de
fechamento imediato
(ignora o
temporizador de
espera em S2).
'Z' (Reset/Calibração) 90 Força retorno ao S0 Usado para resetar o
sistema ou recalibrar
a posição inicial do
servo.


**2.7 Definição dos Estados Operacionais (FSM)
Estado Nome do
Estado
Ação de
Hardware (I/O)
Condição de
Transição
(Evento)
Próximo
Estado
S0** PRONTO/FECH
ADO
Servo em 0º.
LED Vermelho
LIGADO.

1. Comando
Serial 'A'
recebido.
    S1: ABRINDO
2. Comando
Serial 'N'
recebido.
S5:
NEGADO/ERRO
**S1** ABRINDO Servo move
gradualmente 0º
$\to$ 90º. LED
Amarelo
LIGADO.
1. Servo atinge a
posição de 90º.
S2: ABERTO
**S2** ABERTO
(Espera)
Servo em 90º.
LED Verde
LIGADO.
1. Temporizador
interno
(T_Espera = 5s)
decorrido.^5
S3: FECHANDO
2. Comando
Serial 'F'
recebido.
S3: FECHANDO
**S3** FECHANDO Servo move
gradualmente
90º $\to$ 0º.
LED Amarelo
PISCA.
1. Servo atinge a
posição de 0º.
S0:
PRONTO/FECH
ADO
2. Distância
Ultrassônica
$\leq
D_{crítica}$
(Obstrução).
S4:
OBSTRUÇÃO
**S4** OBSTRUÇÃO
(Segurança)
Servo PÁRA.
LED Vermelho
PISCA. Buzzer
ATIVO.
1. Distância
Ultrassônica $>
D_{crítica}$
(Objeto
removido).
S3: FECHANDO
(Retoma)
**S5** NEGADO/ERRO Servo em 0º.
LED Vermelho
PISCA Rápido.
Buzzer 1x.
1. Temporizador
(T_Feedback =
2s) decorrido.
S0:
PRONTO/FECH
ADO


**2.8 Pinagem e Conexões do Arduino UNO
Componente/Sinal Pino Arduino Tipo de Conexão Observações**
Servomotor MG
(Sinal PWM)
Pino Digital 9 Saída PWM Recomendado,
compatível com a
biblioteca Servo.h.
Sensor Ultrassônico
(Trig)
Pino Digital 8 Saída Digital Envio do pulso
sônico.
Sensor Ultrassônico
(Echo)
Pino Digital 7 Entrada Digital Recebimento do eco.
LED Vermelho
(Fechado/Negado)
Pino Digital 4 Saída Digital Requer resistor de
220$\Omega$.
LED Amarelo
(Transição)
Pino Digital 3 Saída Digital Requer resistor de
220$\Omega$.
LED Verde (Aberto) Pino Digital 2 Saída Digital Requer resistor de
220$\Omega$.
Buzzer Pino Digital 10 Saída Digital Usado para alertas de
segurança (S4 e S5).
GND GND Referência de Tensão Conexão crucial com
o GND da fonte
externa do servo.
**2.7 Definição da Equipe**

1. Anderson Marinho
2. José Felipe
3. José Guerra
4. Jamilli Maria
5. Enio Bezerra
6. Débora Laís