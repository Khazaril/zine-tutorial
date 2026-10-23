// Duckling v0.1 firmware.
// The duck makes its own Wi-Fi network (Duckling-XXXX). Join it from a phone
// and the control page opens automatically (captive portal), or browse to
// http://192.168.4.1
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include "config.h"
#include "motion.h"
#include "face.h"
#include "quack.h"
#include "webpage.h"

WebServer server(80);
DNSServer dns;
int touchBaseline = 0;
uint32_t lastPet = 0, lastActivity = 0;

int batteryMv() { return analogReadMilliVolts(PIN_VBAT) * 2; }

Move parseMove(const String &s) {
  for (int m = STOP; m <= CENTER; m++)
    if (s == motion::name((Move)m)) return (Move)m;
  return STOP;
}

void sendState() {
  String j = "{\"move\":\"";
  j += motion::name(motion::current());
  j += "\",\"battery_mv\":";
  j += batteryMv();
  j += ",\"joints\":[";
  for (int i = 0; i < NUM_JOINTS; i++) {
    if (i) j += ',';
    j += "{\"name\":\"";
    j += JOINT_NAME[i];
    j += "\",\"trim\":";
    j += motion::trim(i);
    j += ",\"reversed\":";
    j += motion::reversed(i) ? "true" : "false";
    j += '}';
  }
  j += "]}";
  server.send(200, "application/json", j);
}

void setupWeb() {
  server.on("/", [] { server.send_P(200, "text/html", PAGE); });
  server.on("/api/state", sendState);
  server.on("/api/move", [] {
    Move m = parseMove(server.arg("m"));
    motion::set(m);
    if (m == DANCE) face::setMood(HAPPY, 4000);
    lastActivity = millis();
    sendState();
  });
  server.on("/api/quack", [] {
    quack::play();
    face::setMood(SURPRISED, 600);
    lastActivity = millis();
    server.send(200, "text/plain", "quack");
  });
  server.on("/api/trim", [] {
    motion::set(CENTER);
    int j = server.arg("j").toInt();
    motion::setTrim(j, server.arg("v").toInt());
    if (server.hasArg("r")) motion::setReversed(j, server.arg("r") == "1");
    sendState();
  });
  server.on("/api/save", [] {
    motion::saveCalibration();
    server.send(200, "text/plain", "saved");
  });
  // captive portal: anything unknown goes to the control page
  server.onNotFound([] {
    server.sendHeader("Location", "http://192.168.4.1/", true);
    server.send(302, "text/plain", "");
  });
  server.begin();
}

void setup() {
  Serial.begin(115200);
  motion::begin();           // servos to centre first: this is the assembly position
  bool hasFace = face::begin();
  quack::begin();

  char ssid[20];
  uint64_t mac = ESP.getEfuseMac();
  snprintf(ssid, sizeof ssid, "Duckling-%04X", (uint16_t)(mac >> 32));
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, AP_PASSWORD);
  dns.start(53, "*", WiFi.softAPIP());
  setupWeb();

  touchBaseline = touchRead(PIN_TOUCH);
  Serial.printf("%s up. OLED %s. Join Wi-Fi '%s' (password %s)\n", ssid, hasFace ? "ok" : "missing", ssid, AP_PASSWORD);
  face::setMood(HAPPY, 1500);
  quack::play(1);
  lastActivity = millis();
}

void loop() {
  dns.processNextRequest();
  server.handleClient();
  motion::update();
  face::update(motion::neckAngle());

  // pet the duck: copper tape on its head (ESP32-S3 touch values rise when touched)
  if (touchBaseline > 0 && touchRead(PIN_TOUCH) > touchBaseline * 13 / 10 && millis() - lastPet > 1500) {
    lastPet = lastActivity = millis();
    face::setMood(HAPPY, 2000);
    quack::play();
  }
  // get bored after a minute of nothing and look around
  if (motion::current() == CENTER && millis() - lastActivity > 60000) {
    motion::set(LOOK_AROUND);
    face::setMood(SLEEPY, 3000);
  }
}
