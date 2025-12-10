/*
 * FIRMWARE ARDUINO - CONTROLE DE CANCELA AUTOMATIZADA
 * * Sistema de controle de acesso veicular com máquina de estados finitos (FSM)
 * Versão simplificada sem sensor ultrassônico e buzzer
 * * Estados:
 * - S0: PRONTO/FECHADO
 * - S1: ABRINDO
 * - S2: ABERTO
 * - S3: FECHANDO
 * - S5: NEGADO/ERRO
 * * Comandos Serial:
 * - 'A': Abrir/Autorizar (transição S0 -> S1)
 * - 'N': Negar Acesso (transição S0 -> S5)
 * - 'F': Fechamento Forçado (transição S2 -> S3)
 * - 'Z': Reset/Calibração (força retorno ao S0)
 */

#include <Servo.h>

// ============================================
// DEFINIÇÕES DE HARDWARE E CONSTANTES
// ============================================

// Pinos dos componentes
#define SERVO_PIN 9
#define LED_VERDE_PIN 2
#define LED_AMARELO_PIN 3
#define LED_VERMELHO_PIN 4

// Configurações de comunicação serial
#define BAUD_RATE 9600

// Temporizadores (em milissegundos)
#define TEMPO_ESPERA_ABERTO 5000 // 5 segundos em S2
#define TEMPO_FEEDBACK_NEGADO 2000 // 2 segundos em S5

// Configurações do servo motor
#define SERVO_POS_FECHADO 0  // Posição fechada (0 graus)
#define SERVO_POS_ABERTO 90  // Posição aberta (90 graus)
#define SERVO_VELOCIDADE 2   // Graus por iteração (ajuste para velocidade desejada)

// Configurações de LEDs (piscar) - AJUSTADO PARA MELHOR VISIBILIDADE
#define LED_PISCA_INTERVALO 500    // Intervalo para piscar normal (ms)
#define LED_PISCA_RAPIDO_INTERVALO 150 // Intervalo para piscar rápido (ms)

// ============================================
// ENUMERAÇÃO DE ESTADOS (FSM)
// ============================================

enum EstadoCancela {
 S0_PRONTO_FECHADO = 0,
 S1_ABRINDO = 1,
 S2_ABERTO = 2,
 S3_FECHANDO = 3,
 S5_NEGADO_ERRO = 5
};

// ============================================
// VARIÁVEIS GLOBAIS
// ============================================

// Objeto do servo motor
Servo servo;

// Estado atual da FSM e estado anterior para detectar transição
EstadoCancela estadoAtual = S0_PRONTO_FECHADO;
EstadoCancela estadoAnterior = S0_PRONTO_FECHADO; // Adicionado

// Posição atual do servo (em graus)
int posicaoServoAtual = SERVO_POS_FECHADO;

// Temporizadores não-bloqueantes
unsigned long timerEsperaAberto = 0;
unsigned long timerFeedbackNegado = 0;

// Controle de LEDs (piscar)
unsigned long ultimoToggleLED_VERMELHO = 0;
unsigned long ultimoToggleLED_AMARELO = 0;
bool estadoLED_VERMELHO = LOW; // Alterado para LOW/HIGH para clareza
bool estadoLED_AMARELO = LOW;

// Controle de movimento do servo
unsigned long ultimoMovimentoServo = 0;
#define INTERVALO_MOVIMENTO_SERVO 50 // Intervalo entre movimentos (ms)

// ============================================
// FUNÇÕES DE CONTROLE DE LEDs
// ============================================

/**
 * Liga um LED específico
 */
void ligarLED(int pin) {
 digitalWrite(pin, HIGH);
}

/**
 * Desliga um LED específico
 */
void desligarLED(int pin) {
 digitalWrite(pin, LOW);
}

/**
 * Desliga todos os LEDs
 */
void desligarTodosLEDs() {
 desligarLED(LED_VERDE_PIN);
 desligarLED(LED_AMARELO_PIN);
 desligarLED(LED_VERMELHO_PIN);
}

/**
 * Controla o piscar de um LED (não-bloqueante)
 * @param pin: Pino do LED
 * @param intervalo: Intervalo de piscar em milissegundos
 */
void piscarLED(int pin, unsigned long intervalo) {
 unsigned long tempoAtual = millis();
 unsigned long* ultimoToggle = nullptr;
 bool* estado = nullptr;
 
 // Seleciona as variáveis corretas baseado no pino
 if (pin == LED_VERMELHO_PIN) {
  ultimoToggle = &ultimoToggleLED_VERMELHO;
  estado = &estadoLED_VERMELHO;
 } else if (pin == LED_AMARELO_PIN) {
  ultimoToggle = &ultimoToggleLED_AMARELO;
  estado = &estadoLED_AMARELO;
 } else {
  return; // Pino não suportado para piscar
 }
 
 if (tempoAtual - *ultimoToggle >= intervalo) {
  *estado = !(*estado);
  digitalWrite(pin, *estado ? HIGH : LOW);
  *ultimoToggle = tempoAtual;
 }
}

// Funções wrapper (piscarLEDNormal/Rapido)
void piscarLEDRapido(int pin) { piscarLED(pin, LED_PISCA_RAPIDO_INTERVALO); }
void piscarLEDNormal(int pin) { piscarLED(pin, LED_PISCA_INTERVALO); }


/**
 * CONFIGURA O ESTADO DOS LEDS NA TRANSIÇÃO DE ESTADO
 * Limpa os temporizadores de piscar e garante o estado inicial dos pinos.
 */
void configurarLEDsPorEstado(EstadoCancela estado) {
 
 // Desliga todos os LEDs primeiro para resetar
 desligarTodosLEDs();
 
 // Reseta temporizadores de piscar para o LED Vermelho
 ultimoToggleLED_VERMELHO = 0;
 estadoLED_VERMELHO = LOW;
 
 // Reseta temporizadores de piscar para o LED Amarelo
 ultimoToggleLED_AMARELO = 0;
 estadoLED_AMARELO = LOW;
 
 // Define o estado inicial do hardware para o novo estado
 switch (estado) {
  case S0_PRONTO_FECHADO:
   ligarLED(LED_VERMELHO_PIN);
   break;
   
  case S1_ABRINDO:
   ligarLED(LED_AMARELO_PIN); // Fixo durante a abertura
   break;
   
  case S2_ABERTO:
   ligarLED(LED_VERDE_PIN);
   break;
   
  case S3_FECHANDO:
   // LED Amarelo vai piscar, mas o estado inicial aqui é LOW (desligado)
   // A função piscarLED vai cuidar do estado
   break;
   
  case S5_NEGADO_ERRO:
   // LED Vermelho vai piscar
   // A função piscarLED vai cuidar do estado
   break;
   
  default:
   break;
 }
}

// ============================================
// FUNÇÕES DE CONTROLE DO SERVO MOTOR
// ... (sem alteração) ...
// ============================================

/**
 * Move o servo gradualmente em direção à posição destino (não-bloqueante)
 * @param destino: Posição destino em graus (0-90)
 * @return true se atingiu a posição destino, false caso contrário
 */
bool moverServoPara(int destino) {
 unsigned long tempoAtual = millis();
 
 // Verifica se é hora de mover o servo
 if (tempoAtual - ultimoMovimentoServo < INTERVALO_MOVIMENTO_SERVO) {
  return false;
 }
 
 ultimoMovimentoServo = tempoAtual;
 
 // Se já está na posição destino
 if (posicaoServoAtual == destino) {
  return true;
 }
 
 // Move gradualmente em direção ao destino
 if (posicaoServoAtual < destino) {
  posicaoServoAtual += SERVO_VELOCIDADE;
  if (posicaoServoAtual > destino) {
   posicaoServoAtual = destino;
  }
 } else {
  posicaoServoAtual -= SERVO_VELOCIDADE;
  if (posicaoServoAtual < destino) {
   posicaoServoAtual = destino;
  }
 }
 
 // Atualiza a posição do servo
 servo.write(posicaoServoAtual);
 
 // Retorna true se atingiu a posição destino
 return (posicaoServoAtual == destino);
}

// ============================================
// FUNÇÕES DE PROCESSAMENTO DE COMANDOS SERIAL
// ... (sem alteração) ...
// ============================================

/**
 * Processa comandos recebidos via serial (não-bloqueante)
 */
void processarComandoSerial() {
 if (Serial.available() > 0) {
  char comando = Serial.read();
  
  // Remove caracteres de nova linha e retorno de carro
  if (comando == '\n' || comando == '\r') {
   return;
  }
  
  switch (comando) {
   case 'A': // Abrir/Autorizar
    if (estadoAtual == S0_PRONTO_FECHADO) {
     estadoAtual = S1_ABRINDO;
    }
    break;
    
   case 'N': // Negar Acesso
    if (estadoAtual == S0_PRONTO_FECHADO) {
     estadoAtual = S5_NEGADO_ERRO;
     timerFeedbackNegado = millis();
    }
    break;
    
   case 'F': // Fechamento Forçado
    if (estadoAtual == S2_ABERTO) {
     estadoAtual = S3_FECHANDO;
    }
    break;
    
   case 'Z': // Reset/Calibração
    estadoAtual = S0_PRONTO_FECHADO;
    posicaoServoAtual = SERVO_POS_FECHADO;
    servo.write(SERVO_POS_FECHADO);
    desligarTodosLEDs();
    break;
    
   default:
    break;
  }
 }
}

// ============================================
// MÁQUINA DE ESTADOS FINITOS (FSM)
// ... (Lógica de LED ajustada) ...
// ============================================

/**
 * Executa a lógica do estado S0: PRONTO/FECHADO
 */
void executarEstadoS0() {
 // Hardware: Servo em 0°, LED Vermelho LIGADO (Configurado em configurarLEDsPorEstado)
 
 // Garante que o servo está na posição fechada
 if (posicaoServoAtual != SERVO_POS_FECHADO) {
  moverServoPara(SERVO_POS_FECHADO);
 }
}

/**
 * Executa a lógica do estado S1: ABRINDO
 */
void executarEstadoS1() {
 // Hardware: Servo move gradualmente 0° -> 90°, LED Amarelo LIGADO (Configurado em configurarLEDsPorEstado)
 
 // Move o servo para a posição aberta
 bool servoAtingiuDestino = moverServoPara(SERVO_POS_ABERTO);
 
 // Transição: Servo atinge 90° -> S2
 if (servoAtingiuDestino) {
  estadoAtual = S2_ABERTO;
  timerEsperaAberto = millis();
 }
}

/**
 * Executa a lógica do estado S2: ABERTO
 */
void executarEstadoS2() {
 // Hardware: Servo em 90°, LED Verde LIGADO (Configurado em configurarLEDsPorEstado)
 
 // Garante que o servo está na posição aberta
 if (posicaoServoAtual != SERVO_POS_ABERTO) {
  moverServoPara(SERVO_POS_ABERTO);
 }
 
 // Verifica temporizador de espera
 unsigned long tempoAtual = millis();
 
 // Transições:
 // - Temporizador de 5s decorrido -> S3
 if (tempoAtual - timerEsperaAberto >= TEMPO_ESPERA_ABERTO) {
  estadoAtual = S3_FECHANDO;
 }
}

/**
 * Executa a lógica do estado S3: FECHANDO
 */
void executarEstadoS3() {
 // Hardware: Servo move gradualmente 90° -> 0°, LED Amarelo PISCA
 piscarLEDNormal(LED_AMARELO_PIN); // APENAS CHAMA A FUNÇÃO PISCAR
 
 // Move o servo para a posição fechada
 bool servoAtingiuDestino = moverServoPara(SERVO_POS_FECHADO);
 
 // Transição: Servo atinge 0° -> S0
 if (servoAtingiuDestino) {
  estadoAtual = S0_PRONTO_FECHADO;
 }
}

/**
 * Executa a lógica do estado S5: NEGADO/ERRO
 */
void executarEstadoS5() {
 // Hardware: Servo em 0°, LED Vermelho PISCA RÁPIDO
 piscarLEDRapido(LED_VERMELHO_PIN); // APENAS CHAMA A FUNÇÃO PISCAR
 
 // Garante que o servo está na posição fechada
 if (posicaoServoAtual != SERVO_POS_FECHADO) {
  moverServoPara(SERVO_POS_FECHADO);
 }
 
 // Verifica temporizador de feedback
 unsigned long tempoAtual = millis();
 
 // Transição: Temporizador de 2s decorrido -> S0
 if (tempoAtual - timerFeedbackNegado >= TEMPO_FEEDBACK_NEGADO) {
  estadoAtual = S0_PRONTO_FECHADO;
 }
}

/**
 * Executa a máquina de estados finitos
 */
void executarFSM() {
 // Detecta mudança de estado e configura o hardware (LEDs)
 if (estadoAtual != estadoAnterior) {
  configurarLEDsPorEstado(estadoAtual); // Chama a nova função
  Serial.print("Transição para estado: ");
  Serial.println(estadoAtual);
 }
 
 // Executa a lógica específica do estado
 switch (estadoAtual) {
  case S0_PRONTO_FECHADO:
   executarEstadoS0();
   break;
   
  case S1_ABRINDO:
   executarEstadoS1();
   break;
   
  case S2_ABERTO:
   executarEstadoS2();
   break;
   
  case S3_FECHANDO:
   executarEstadoS3();
   break;
   
  case S5_NEGADO_ERRO:
   executarEstadoS5();
   break;
   
  default:
   estadoAtual = S0_PRONTO_FECHADO;
   break;
 }
 
 // Atualiza o estado anterior para a próxima iteração
 estadoAnterior = estadoAtual;
}

// ============================================
// FUNÇÕES DE INICIALIZAÇÃO
// ============================================

/**
 * Configuração inicial do Arduino
 */
void setup() {
 Serial.begin(BAUD_RATE);
 
 pinMode(LED_VERDE_PIN, OUTPUT);
 pinMode(LED_AMARELO_PIN, OUTPUT);
 pinMode(LED_VERMELHO_PIN, OUTPUT);
 
 servo.attach(SERVO_PIN);
 servo.write(SERVO_POS_FECHADO);
 posicaoServoAtual = SERVO_POS_FECHADO;
 
 // Inicializa o estado e configura os LEDs para S0
 estadoAtual = S0_PRONTO_FECHADO;
 estadoAnterior = S5_NEGADO_ERRO; // Força a primeira execução de configurarLEDsPorEstado em loop()
 
 delay(500);
}

// ============================================
// LOOP PRINCIPAL
// ============================================

/**
 * Loop principal do Arduino (executa continuamente)
 */
void loop() {
 processarComandoSerial();
 executarFSM();
 delay(10);
}