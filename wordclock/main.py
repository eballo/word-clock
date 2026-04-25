from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime
from logging import DEBUG, INFO, basicConfig, getLogger
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
    from wordclock.layouts.english import build_display_grid, get_leds_for_time
    from wordclock.led.controller import create_controller

    grid = build_display_grid()
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

    from wordclock.api.app import create_app
    from wordclock.layouts.english import build_display_grid
    from wordclock.led.controller import create_controller

    grid = build_display_grid()
    ctrl = create_controller(mock=mock, brightness=brightness, grid=grid if mock else None)

    clock_thread = threading.Thread(
        target=run_clock,
        kwargs=dict(lang=lang, interval=interval, color=color, ctrl=ctrl),
        daemon=True,
    )
    clock_thread.start()

    logger.info("Wordclock API → http://%s:%d", host, port)
    app = create_app(led_controller=ctrl)
    from wordclock.api.app import _run_app
    _run_app(app, host=host, port=port, debug=debug)


def main() -> None:
    parser = ArgumentParser(description="Wordclock — LED word clock")
    parser.add_argument("--lang", default="english", choices=["english"])
    parser.add_argument("--mock", action="store_true", help="Simulated LEDs")
    parser.add_argument("--brightness", type=int, default=128)
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    basicConfig(
        level=DEBUG if args.debug else INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )
    run_clock(lang=args.lang, mock=args.mock, brightness=args.brightness, interval=args.interval)


def main_serve() -> None:
    parser = ArgumentParser(description="Wordclock — clock loop + API server")
    parser.add_argument("--lang", default="english", choices=["english"])
    parser.add_argument("--mock", action="store_true", help="Simulated LEDs")
    parser.add_argument("--brightness", type=int, default=128)
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", "-p", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    basicConfig(
        level=DEBUG if args.debug else INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )
    serve(
        lang=args.lang,
        mock=args.mock,
        brightness=args.brightness,
        interval=args.interval,
        host=args.host,
        port=args.port,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
