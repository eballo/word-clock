from __future__ import annotations

from logging import DEBUG, INFO, basicConfig
from typing import Annotated

import typer

from wordclock.config import API_HOST, API_PORT, CLOCK_INTERVAL, LED_BRIGHTNESS
from wordclock.layouts.registry import Language

_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(message)s"


app = typer.Typer()


@app.command(no_args_is_help=True)
def main(
    lang: Language = Language.catalan,
    mock: Annotated[bool, typer.Option(help="Use mock LED controller")] = False,
    display: Annotated[bool, typer.Option(help="Print grid to console (mock only)")] = False,
    brightness: int = LED_BRIGHTNESS,
    interval: int = CLOCK_INTERVAL,
    host: str = API_HOST,
    port: Annotated[int, typer.Option("--port", "-p")] = API_PORT,
    debug: bool = False,
) -> None:
    basicConfig(level=DEBUG if debug else INFO, format=_LOG_FORMAT)

    from wordclock.clock import WordClock

    WordClock(
        lang=lang.value,
        mock=mock,
        display=display,
        brightness=brightness,
        interval=interval,
    ).serve(host=host, port=port, debug=debug)
