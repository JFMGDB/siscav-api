#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

WebServer server(80);
Servo gateServo;

constexpr int SERVO_PIN = 18;
constexpr int LED_PIN = 2;
constexpr int GATE_CLOSED_ANGLE = 0;
constexpr int GATE_OPEN_ANGLE = 90;

void openGate() {
  gateServo.write(GATE_OPEN_ANGLE);
  digitalWrite(LED_PIN, HIGH);
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

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  gateServo.setPeriodHertz(50);
  gateServo.attach(SERVO_PIN);
  gateServo.write(GATE_CLOSED_ANGLE);

  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST", "", 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
  }
  Serial.println("WiFi connected");

  server.on("/open", HTTP_POST, handleOpen);
  server.begin();
  Serial.println("HTTP server listening on port 80 (POST /open)");
}

void loop() {
  server.handleClient();
}
