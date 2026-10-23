#pragma once
#include <stdint.h>

enum Mood { NEUTRAL, HAPPY, SLEEPY, SURPRISED };

namespace face {
bool begin();          // false if no OLED found (the duck still works)
void update(int lookDeg);
void setMood(Mood m, uint32_t forMs = 2000);
}
