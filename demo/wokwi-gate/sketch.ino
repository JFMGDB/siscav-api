#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

WebServer server(80);
Servo gateServo;

constexpr int SERVO_PIN = 18;
constexpr int LED_PIN = 2;
// Wokwi servo: 0° = braço para cima (cancela levantada), 90° = horizontal (barreira fechada).
constexpr int GATE_OPEN_ANGLE = 0;
constexpr int GATE_CLOSED_ANGLE = 90;
constexpr unsigned long AUTO_CLOSE_MS = 10000;

unsigned long gateCloseAt = 0;

void closeGate() {
  gateServo.write(GATE_CLOSED_ANGLE);
  digitalWrite(LED_PIN, LOW);
  gateCloseAt = 0;
  Serial.println("GATE CLOSE");
}

void openGate() {
  gateServo.write(GATE_OPEN_ANGLE);
  digitalWrite(LED_PIN, HIGH);
  gateCloseAt = millis() + AUTO_CLOSE_MS;
  Serial.println("GATE OPEN");
}

void handleOpen() {
  if (server.method() != HTTP_POST) {
    server.send(405, "application/json", "{\"ok\":false}");
    return;
  }

  openGate();
  server.send(200, "application/json", "{\"ok\":true}");
}

void handleClose() {
  if (server.method() != HTTP_POST) {
    server.send(405, "application/json", "{\"ok\":false}");
    return;
  }

  closeGate();
  server.send(200, "application/json", "{\"ok\":true}");
}

void setup() {
  Serial.begin(115200);
  Serial.println("Siscav gate boot...");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  gateServo.setPeriodHertz(50);
  gateServo.attach(SERVO_PIN);
  gateServo.write(GATE_CLOSED_ANGLE);

  WiFi.mode(WIFI_STA);
  Serial.print("Connecting WiFi");
  WiFi.begin("Wokwi-GUEST", "", 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println(" connected");

  server.on("/open", HTTP_POST, handleOpen);
  server.on("/close", HTTP_POST, handleClose);
  server.begin();
  Serial.println("HTTP server listening on port 80 (POST /open, POST /close)");
}

void loop() {
  server.handleClient();
  if (gateCloseAt != 0 && millis() >= gateCloseAt) {
    closeGate();
  }
}
