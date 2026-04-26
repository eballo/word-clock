"""CLI entry points for the wordclock package."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig, getLogger

logger = getLogger(__name__)


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

    from wordclock.clock import run_clock

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

    from wordclock.clock import serve

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
