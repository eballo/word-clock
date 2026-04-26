"""Clock loop and combined serve logic."""

from __future__ import annotations

from datetime import datetime
from logging import getLogger
from time import sleep

logger = getLogger(__name__)


def run_clock(
    lang: str = "english",
    mock: bool = False,
    brightness: int = 128,
    interval: int = 30,
    color: tuple[int, int, int] = (255, 200, 50),
    ctrl=None,
) -> None:
    from wordclock.layouts.english import GRID_RAW, get_leds_for_time
    from wordclock.led.controller import create_controller

    grid = GRID_RAW
    if ctrl is None:
        ctrl = create_controller(mock=mock, brightness=brightness, grid=grid if mock else None)

    logger.info("Wordclock starting (lang=%s, mode=%s)", lang, "mock" if mock else "real")

    last_sentence = ""
    try:
        while True:
            now = datetime.now()
            result = get_leds_for_time(now.hour, now.minute, grid=grid)

            if result["sentence"] != last_sentence:
                logger.info("%02d:%02d → %s", now.hour, now.minute, result["sentence"])
                ctrl.display_leds(result["led_indices"], color=color)
                last_sentence = result["sentence"]

            sleep(interval)

    except KeyboardInterrupt:
        logger.info("Stopping...")
        ctrl.clear()


def serve(
    lang: str = "english",
    mock: bool = False,
    brightness: int = 128,
    interval: int = 30,
    color: tuple[int, int, int] = (255, 200, 50),
    host: str = "0.0.0.0",
    port: int = 5000,
    debug: bool = False,
) -> None:
    import threading

    from wordclock.api.app import _run_app, create_app
    from wordclock.layouts.english import GRID_RAW
    from wordclock.led.controller import create_controller

    grid = GRID_RAW
    ctrl = create_controller(mock=mock, brightness=brightness, grid=grid if mock else None)

    clock_thread = threading.Thread(
        target=run_clock,
        kwargs=dict(lang=lang, interval=interval, color=color, ctrl=ctrl),
        daemon=True,
    )
    clock_thread.start()

    logger.info("Wordclock API → http://%s:%d", host, port)
    app = create_app(led_controller=ctrl)
    _run_app(app, host=host, port=port, debug=debug)
