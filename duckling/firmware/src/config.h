#pragma once
// Duckling v0.1 pin map (ESP32-S3 SuperMini). Matches docs/wiring.md.

enum Joint { HIP_L, HIP_R, ANKLE_L, ANKLE_R, NECK, NUM_JOINTS };

static const int SERVO_PIN[NUM_JOINTS] = {1, 2, 3, 4, 5};
static const char *JOINT_NAME[NUM_JOINTS] = {"Left hip", "Right hip", "Left ankle", "Right ankle", "Neck"};

// Mechanical limits around centre (degrees). Keeps feet from hitting each other.
static const int JOINT_LIMIT[NUM_JOINTS] = {35, 35, 35, 35, 60};

static const int PIN_SDA = 8;
static const int PIN_SCL = 9;
static const int PIN_I2S_BCLK = 10;
static const int PIN_I2S_LRC = 11;
static const int PIN_I2S_DOUT = 12;
static const int PIN_TOUCH = 7;      // optional copper-tape pad on the head
static const int PIN_VBAT = 6;       // optional 100k/100k divider from the cell

static const char *AP_PASSWORD = "quackquack";  // min 8 chars; SSID is Duckling-XXXX
