// Two cartoon eyes on a 128x64 SSD1306. They blink, follow the neck, and
// change shape with the duck's mood.
#include "face.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "config.h"

namespace {
Adafruit_SSD1306 oled(128, 64, &Wire, -1);
bool ok = false;
Mood mood = NEUTRAL;
uint32_t moodUntil = 0, nextBlink = 0, lastDraw = 0;

void eye(int cx, int cy, float open, Mood m) {
  const int w = 34, h = 40;
  if (m == HAPPY) {  // upside-down U: ^ ^
    for (int t = 0; t < 4; t++) oled.drawCircleHelper(cx, cy + 8 + t, w / 2, 0x3, SSD1306_WHITE);
    return;
  }
  int eh = max(3, (int)(h * open * (m == SLEEPY ? 0.35f : 1.0f)));
  int ew = (m == SURPRISED) ? w + 6 : w;
  oled.fillRoundRect(cx - ew / 2, cy - eh / 2, ew, eh, min(10, eh / 2), SSD1306_WHITE);
  if (eh > 12) oled.fillCircle(cx + 6, cy - eh / 4, 4, SSD1306_BLACK);  // shine
}
}  // namespace

namespace face {

bool begin() {
  Wire.begin(PIN_SDA, PIN_SCL);
  ok = oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  if (ok) {
    oled.clearDisplay();
    oled.display();
  }
  return ok;
}

void setMood(Mood m, uint32_t forMs) {
  mood = m;
  moodUntil = millis() + forMs;
}

void update(int lookDeg) {
  uint32_t now = millis();
  if (!ok || now - lastDraw < 33) return;  // ~30 fps
  lastDraw = now;
  if (mood != NEUTRAL && now > moodUntil) mood = NEUTRAL;
  if (now > nextBlink + 150) nextBlink = now + random(2000, 5000);
  float open = 1.0f;
  if (now > nextBlink) open = 0.1f;  // mid-blink

  // eyes glance in the direction the head is turning
  int dx = constrain(-lookDeg / 3, -14, 14);
  oled.clearDisplay();
  eye(36 + dx, 32, open, mood);
  eye(92 + dx, 32, open, mood);
  oled.display();
}

}  // namespace face
