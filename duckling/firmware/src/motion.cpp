// Oscillator gaits: each joint follows  offset + amplitude * sin(2*pi*t/period + phase).
// The same technique the Otto DIY robots use, which is what makes a 4-servo
// biped walk without any balance sensing.
#include "motion.h"
#include <ESP32Servo.h>
#include <Preferences.h>

namespace {
Servo servo[NUM_JOINTS];
int trims[NUM_JOINTS];
bool rev[NUM_JOINTS];
Move mode = CENTER;
uint32_t modeStart = 0;
float lastAngle[NUM_JOINTS];

struct Gait {
  uint16_t period;            // ms
  int8_t amp[NUM_JOINTS];
  int8_t offset[NUM_JOINTS];
  int16_t phase[NUM_JOINTS];  // degrees
};

// hip L, hip R, ankle L, ankle R, neck
const Gait GAITS[] = {
    /* STOP        */ {1000, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}},
    /* FORWARD     */ {1000, {30, 30, 20, 20, 8}, {0, 0, 4, -4, 0}, {0, 0, -90, -90, 0}},
    /* BACKWARD    */ {1000, {30, 30, 20, 20, 8}, {0, 0, 4, -4, 0}, {0, 0, 90, 90, 0}},
    /* TURN_LEFT   */ {1000, {30, 0, 20, 20, 0}, {0, 0, 4, -4, 20}, {0, 0, -90, -90, 0}},
    /* TURN_RIGHT  */ {1000, {0, 30, 20, 20, 0}, {0, 0, 4, -4, -20}, {0, 0, -90, -90, 0}},
    /* WADDLE      */ {700, {0, 0, 22, 22, 15}, {0, 0, 11, -11, 0}, {0, 0, 0, 0, 90}},
    /* DANCE       */ {900, {25, 25, 15, 15, 35}, {0, 0, 0, 0, 0}, {0, 180, 90, 270, 0}},
    /* LOOK_AROUND */ {3000, {0, 0, 0, 0, 50}, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}},
    /* CENTER      */ {1000, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}},
};

void write(int j, float deg) {
  deg = constrain(deg, -JOINT_LIMIT[j], JOINT_LIMIT[j]);
  lastAngle[j] = deg;
  float out = 90 + trims[j] + (rev[j] ? -deg : deg);
  servo[j].write((int)constrain(out, 0, 180));
}
}  // namespace

namespace motion {

void begin() {
  Preferences p;
  p.begin("duckling", true);
  for (int j = 0; j < NUM_JOINTS; j++) {
    char k[8];
    snprintf(k, sizeof k, "t%d", j);
    trims[j] = p.getInt(k, 0);
    snprintf(k, sizeof k, "r%d", j);
    rev[j] = p.getBool(k, false);
  }
  p.end();
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  for (int j = 0; j < NUM_JOINTS; j++) {
    servo[j].setPeriodHertz(50);
    servo[j].attach(SERVO_PIN[j], 500, 2400);
    write(j, 0);
  }
}

void set(Move m) {
  if (m == mode) return;
  mode = m;
  modeStart = millis();
}

Move current() { return mode; }
int neckAngle() { return (int)lastAngle[NECK]; }

void update() {
  const Gait &g = GAITS[mode];
  float t = (millis() - modeStart) / (float)g.period;
  // blend from the previous pose over the first half cycle so the duck doesn't lurch
  float ramp = constrain(t * 2, 0.0f, 1.0f);
  for (int j = 0; j < NUM_JOINTS; j++) {
    float a = g.offset[j] + g.amp[j] * sinf(TWO_PI * t + radians(g.phase[j]));
    write(j, a * ramp + lastAngle[j] * (1 - ramp));
  }
}

void setTrim(int j, int t) {
  if (j < 0 || j >= NUM_JOINTS) return;
  trims[j] = constrain(t, -30, 30);
  write(j, lastAngle[j]);
}
int trim(int j) { return trims[j]; }
void setReversed(int j, bool r) {
  if (j >= 0 && j < NUM_JOINTS) rev[j] = r;
}
bool reversed(int j) { return rev[j]; }

void saveCalibration() {
  Preferences p;
  p.begin("duckling", false);
  for (int j = 0; j < NUM_JOINTS; j++) {
    char k[8];
    snprintf(k, sizeof k, "t%d", j);
    p.putInt(k, trims[j]);
    snprintf(k, sizeof k, "r%d", j);
    p.putBool(k, rev[j]);
  }
  p.end();
}

const char *name(Move m) {
  static const char *N[] = {"stop", "forward", "backward", "left", "right", "waddle", "dance", "look", "center"};
  return N[m];
}

}  // namespace motion
