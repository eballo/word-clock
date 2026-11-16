from __future__ import annotations

# LED hardware (WS2812B strip on Raspberry Pi)
LED_COUNT: int = 256
LED_PIN: int = 18
LED_BRIGHTNESS: int = 128
LED_FREQ_HZ: int = 800_000
LED_DMA: int = 10
LED_COLOR: tuple[int, int, int] = (255, 200, 50)

# Clock loop
CLOCK_INTERVAL: int = 30
CLOCK_LANG: str = "catalan"

# API server
API_HOST: str = "0.0.0.0"
API_PORT: int = 5000

# Mini matrix (Tremex WS2812B strip, 30 LEDs/metre, 60 LEDs in a 10 x 6 snake)
MATRIX_WIDTH: int = 10
MATRIX_HEIGHT: int = 6
# Brightness that follows the time of day, 0-255: strong in daylight,
# softer after sunset and dim from 23:00 until morning
MATRIX_BRIGHTNESS_DAY: int = 96
MATRIX_BRIGHTNESS_EVENING: int = 32
MATRIX_BRIGHTNESS_NIGHT: int = 8
# Software current limit: a breadboard rail carries 1-2 A at most
MATRIX_MAX_MA: int = 1500
