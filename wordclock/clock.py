from __future__ import annotations

import asyncio
from datetime import datetime
from logging import getLogger

from wordclock.api.app import create_app, run_app
from wordclock.config import (
    API_HOST,
    API_PORT,
    CLOCK_INTERVAL,
    CLOCK_LANG,
    LED_BRIGHTNESS,
    LED_COLOR,
)
from wordclock.layouts.registry import get_layout
from wordclock.led.controller import create_controller

logger = getLogger(__name__)


class WordClock:
    def __init__(
        self,
        lang: str = CLOCK_LANG,
        mock: bool = False,
        display: bool = False,
        brightness: int = LED_BRIGHTNESS,
        interval: int = CLOCK_INTERVAL,
        color: tuple[int, int, int] = LED_COLOR,
    ) -> None:
        self._interval = interval
        self._color = color
        self._last_sentence = ""

        layout = get_layout(lang)
        self._grid = layout.GRID_RAW
        self._get_leds_for_time = layout.get_leds_for_time
        self._ctrl = create_controller(
            mock=mock, brightness=brightness, grid=self._grid if display else None
        )

        logger.info("Wordclock starting (lang=%s, mode=%s)", lang, "mock" if mock else "real")

    async def _loop(self) -> None:
        try:
            while True:
                now = datetime.now()
                result = self._get_leds_for_time(now.hour, now.minute, grid=self._grid)
                if result["sentence"] != self._last_sentence:
                    logger.info("%02d:%02d → %s", now.hour, now.minute, result["sentence"])
                    self._ctrl.display_leds(result["led_indices"], color=self._color)
                    self._last_sentence = result["sentence"]
                await asyncio.sleep(self._interval)
        except asyncio.CancelledError:
            logger.info("Stopping...")
            self._ctrl.clear()
            raise

    def run(self) -> None:
        try:
            asyncio.run(self._loop())
        except KeyboardInterrupt:
            pass

    def serve(self, host: str = API_HOST, port: int = API_PORT, debug: bool = False) -> None:
        logger.info("Wordclock API → http://%s:%d", host, port)
        app = create_app(led_controller=self._ctrl, clock_loop=self._loop)
        run_app(app, host=host, port=port, debug=debug)
