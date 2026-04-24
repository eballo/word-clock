"""
LED strip controller — WS2812B.

Two interchangeable implementations:
  RealLedController  → rpi-ws281x (Raspberry Pi only)
  MockLedController  → no hardware, logs to console

Usage:
    from wordclock.led.controller import create_controller
    ctrl = create_controller(mock=True)
    ctrl.display_leds([0, 1, 42], color=(255, 200, 50))
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger

logger = getLogger(__name__)

DEFAULT_LED_COUNT  = 256
DEFAULT_LED_PIN    = 18
DEFAULT_BRIGHTNESS = 128
DEFAULT_FREQ_HZ    = 800_000
DEFAULT_DMA        = 10


_DEFAULT_COLOR = (255, 200, 50)
_ANSI_BOLD  = "\033[1m"
_ANSI_DIM   = "\033[2m"
_ANSI_RESET = "\033[0m"


class BaseLedController(ABC):

    def __init__(self, num_leds: int = DEFAULT_LED_COUNT, brightness: int = DEFAULT_BRIGHTNESS, grid: list[str] | None = None):
        self.num_leds   = num_leds
        self.brightness = brightness
        self._grid = grid
        self._pixels: list[tuple[int, int, int]] = [(0, 0, 0)] * num_leds

    @abstractmethod
    def begin(self) -> None: ...

    @abstractmethod
    def show(self) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...

    def set_pixel(self, index: int, r: int, g: int, b: int) -> None:
        if 0 <= index < self.num_leds:
            self._pixels[index] = (r, g, b)

    def set_pixels(self, indices: list[int], r: int, g: int, b: int) -> None:
        for idx in indices:
            self.set_pixel(idx, r, g, b)

    def display_leds(
        self,
        active_indices: list[int],
        color: tuple[int, int, int] = (255, 200, 50),
    ) -> None:
        self.clear()
        self.set_pixels(active_indices, *color)
        self.show()

    def get_state(self) -> list[tuple[int, int, int]]:
        return list(self._pixels)


class RealLedController(BaseLedController):

    def __init__(self, num_leds=DEFAULT_LED_COUNT, brightness=DEFAULT_BRIGHTNESS,
                 pin=DEFAULT_LED_PIN, freq_hz=DEFAULT_FREQ_HZ, dma=DEFAULT_DMA):
        super().__init__(num_leds, brightness)
        self._pin, self._freq_hz, self._dma = pin, freq_hz, dma
        self._strip = None

    def begin(self) -> None:
        try:
            from rpi_ws281x import PixelStrip  # type: ignore[import]
            self._strip = PixelStrip(
                self.num_leds, self._pin, self._freq_hz,
                self._dma, False, self.brightness, 0,
            )
            self._strip.begin()
            logger.info("RealLedController ready (%d LEDs, GPIO%d)", self.num_leds, self._pin)
        except ImportError as e:
            raise RuntimeError("rpi-ws281x not installed. Run: uv pip install 'wordclock[rpi]'") from e

    def show(self) -> None:
        if not self._strip:
            return
        from rpi_ws281x import Color  # type: ignore[import]
        for i, (r, g, b) in enumerate(self._pixels):
            self._strip.setPixelColor(i, Color(r, g, b))
        self._strip.show()

    def clear(self) -> None:
        self._pixels = [(0, 0, 0)] * self.num_leds
        self.show()


class MockLedController(BaseLedController):

    def begin(self) -> None:
        logger.info("MockLedController ready (%d LEDs)", self.num_leds)

    def show(self) -> None:
        active = [i for i, px in enumerate(self._pixels) if any(px)]
        logger.debug("show() → %d LEDs active", len(active))

    def clear(self) -> None:
        self._pixels = [(0, 0, 0)] * self.num_leds

    def display_leds(
        self,
        indices: list[int],
        color: tuple[int, int, int] = _DEFAULT_COLOR,
    ) -> None:
        logger.info("LEDs on: %s  color=%s", indices, color)
        if self._grid is not None:
            self._print_grid(indices)

    def _print_grid(self, active_indices: list[int]) -> None:
        active = set(active_indices)
        grid = self._grid
        rows = len(grid)
        cols = len(grid[0])

        print()
        for row in range(rows):
            line: list[str] = []
            for col in range(cols):
                # Reverse snake-wiring to recover the LED index for this cell.
                idx = row * cols + (cols - 1 - col if row % 2 == 1 else col)
                ch = grid[row][col]
                if idx in active:
                    line.append(f"{_ANSI_BOLD}{ch}{_ANSI_RESET}")
                else:
                    line.append(f"{_ANSI_DIM}{ch}{_ANSI_RESET}")
            print("".join(line))
        print()

    def clear(self) -> None:
        logger.info("LEDs cleared")


def create_controller(mock: bool = False, **kwargs) -> BaseLedController:
    safe = {k: v for k, v in kwargs.items() if k in ("num_leds", "brightness", "grid")}
    if mock:
        ctrl: BaseLedController = MockLedController(**safe)
    else:
        try:
            ctrl = RealLedController(**kwargs)
        except RuntimeError:
            logger.warning("LED hardware unavailable — falling back to mock mode.")
            ctrl = MockLedController(**safe)
    ctrl.begin()
    return ctrl