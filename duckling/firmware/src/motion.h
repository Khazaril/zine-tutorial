#pragma once
#include <Arduino.h>
#include "config.h"

enum Move { STOP, FORWARD, BACKWARD, TURN_LEFT, TURN_RIGHT, WADDLE, DANCE, LOOK_AROUND, CENTER };

namespace motion {
void begin();
void update();                 // call every loop
void set(Move m);
Move current();
int neckAngle();               // degrees from centre, for the eyes to follow
void setTrim(int joint, int trim);
int trim(int joint);
void setReversed(int joint, bool rev);
bool reversed(int joint);
void saveCalibration();
const char *name(Move m);
}
