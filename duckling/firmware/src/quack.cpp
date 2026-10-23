// Synthesised quack: a buzzy pulse wave with falling pitch pushed through a
// resonant "nasal" filter. No sound files needed. Plays on its own task so
// walking never stutters.
#include "quack.h"
#include <Arduino.h>
#include <driver/i2s.h>
#include "config.h"

namespace {
const int RATE = 16000;
volatile int pending = -1;

void render(int variant) {
  float base = 520 + 90 * variant;       // starting pitch
  float len = 0.22f + 0.04f * variant;   // seconds
  int n = (int)(RATE * len);
  float phase = 0, y1 = 0, y2 = 0;
  // two-pole resonator around 1.1 kHz gives the nasal "aah"
  const float f0 = 1100, r = 0.96f;
  const float c1 = 2 * r * cosf(TWO_PI * f0 / RATE), c2 = -r * r;
  int16_t buf[256];
  for (int i = 0; i < n;) {
    int k = 0;
    for (; k < 256 && i < n; k++, i++) {
      float t = (float)i / n;
      float f = base * (1.0f - 0.35f * t);
      phase += f / RATE;
      if (phase >= 1) phase -= 1;
      float src = phase < 0.3f ? 1.0f : -0.43f;   // narrow pulse
      float y = src + c1 * y1 + c2 * y2;
      y2 = y1;
      y1 = y;
      float env = min(1.0f, t * 25) * (1 - t * t);   // fast attack, soft release
      buf[k] = (int16_t)constrain(y * env * 1400, -32000, 32000);
    }
    size_t written;
    i2s_write(I2S_NUM_0, buf, k * sizeof(int16_t), &written, portMAX_DELAY);
  }
  i2s_zero_dma_buffer(I2S_NUM_0);
}

void task(void *) {
  for (;;) {
    if (pending >= 0) {
      int v = pending;
      pending = -1;
      render(v);
    }
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}
}  // namespace

namespace quack {

void begin() {
  i2s_config_t cfg = {};
  cfg.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX);
  cfg.sample_rate = RATE;
  cfg.bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT;
  cfg.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
  cfg.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  cfg.dma_buf_count = 4;
  cfg.dma_buf_len = 256;
  i2s_pin_config_t pins = {};
  pins.mck_io_num = I2S_PIN_NO_CHANGE;
  pins.bck_io_num = PIN_I2S_BCLK;
  pins.ws_io_num = PIN_I2S_LRC;
  pins.data_out_num = PIN_I2S_DOUT;
  pins.data_in_num = I2S_PIN_NO_CHANGE;
  i2s_driver_install(I2S_NUM_0, &cfg, 0, nullptr);
  i2s_set_pin(I2S_NUM_0, &pins);
  xTaskCreatePinnedToCore(task, "quack", 4096, nullptr, 1, nullptr, 0);
}

void play(int variant) { pending = variant > 0 ? variant - 1 : random(0, 3); }

}  // namespace quack
