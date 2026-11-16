from __future__ import annotations

import subprocess
from enum import StrEnum
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path
from signal import SIGTERM, signal
from types import FrameType
from typing import Annotated

import typer

from wordclock.config import MATRIX_BRIGHTNESS, MATRIX_HEIGHT, MATRIX_MAX_MA, MATRIX_WIDTH
from wordclock.led.controller import create_controller
from wordclock.matrix.canvas import Canvas, Color, hex_to_color
from wordclock.matrix.catalog import ALL_SCENES, Catalog
from wordclock.matrix.runner import MatrixRunner
from wordclock.matrix.show import load_personal
from wordclock.matrix.web import MatrixService, WebLedController, serve

SceneName = StrEnum("SceneName", {name: name for name in ALL_SCENES})

app = typer.Typer()
logger = getLogger(__name__)


def parse_color(value: str) -> Color:
    """
    Parse a hex colour such as ``ff8800`` or ``#ff8800``.

    Args:
        value: Six hex digits, with or without ``#``.

    Returns:
        The RGB colour.

    Raises:
        typer.BadParameter: If the value is not a hex colour.
    """
    try:
        return hex_to_color(value)
    except ValueError as exc:
        raise typer.BadParameter(f"Expected a hex colour like ff8800, got {value!r}") from exc


def power_off() -> None:
    """Shut the Raspberry Pi down, after a long press of the button."""
    logger.warning("Shutting down")
    subprocess.run(["systemctl", "poweroff"], check=False)


def stop_on_sigterm(signum: int, frame: FrameType | None) -> None:
    """
    Stop like Ctrl+C when systemd stops the service, so the LEDs go dark.

    Args:
        signum: The signal number.
        frame: The interrupted stack frame.

    Raises:
        KeyboardInterrupt: Always, to end the scene.
    """
    raise KeyboardInterrupt


@app.command()
def main(
    scene: Annotated[SceneName, typer.Argument(help="Scene to play")] = SceneName.show,
    text: Annotated[str, typer.Option(help="Text for the text scene")] = "HOLA",
    color: Annotated[str | None, typer.Option(help="Hex colour, e.g. ff8800")] = None,
    width: int = MATRIX_WIDTH,
    height: int = MATRIX_HEIGHT,
    brightness: Annotated[int, typer.Option(min=0, max=255)] = MATRIX_BRIGHTNESS,
    max_ma: Annotated[int, typer.Option(help="Software current limit in mA")] = MATRIX_MAX_MA,
    snake: Annotated[bool, typer.Option(help="Odd rows run right to left")] = True,
    rotate: Annotated[bool, typer.Option(help="Turn the picture 180°, matrix upside down")] = False,
    mirror: Annotated[bool, typer.Option(help="Flip the picture left to right")] = False,
    seconds: Annotated[float | None, typer.Option(help="Stop after this many seconds")] = None,
    mock: Annotated[bool, typer.Option(help="No LEDs: draw the matrix in the terminal")] = False,
    preview: Annotated[bool | None, typer.Option(help="Draw the matrix in the terminal")] = None,
    config: Annotated[Path, typer.Option(help="Personal texts and accounts, a TOML file")] = Path(
        "matrix.toml"
    ),
    web: Annotated[
        bool,
        typer.Option(help="No LEDs: simulate the matrix in a web page, with button and webcam"),
    ] = False,
    api: Annotated[
        bool, typer.Option(help="Light the LEDs and serve the same page and API to control them")
    ] = False,
    host: Annotated[
        str, typer.Option(help="Page and API address; 0.0.0.0 for the whole network")
    ] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Page and API port")] = 8001,
    debug: bool = False,
) -> None:
    """Play a scene on the mini LED matrix."""
    basicConfig(level=DEBUG if debug else INFO, format="%(asctime)s %(levelname)-8s %(message)s")
    signal(SIGTERM, stop_on_sigterm)
    rgb = parse_color(color) if color else None
    if web:
        ctrl = WebLedController(num_leds=width * height, brightness=brightness)
    else:
        ctrl = create_controller(mock=mock, num_leds=width * height, brightness=brightness)
    runner = MatrixRunner(
        Canvas(width, height),
        ctrl,
        max_ma=max_ma,
        snake=snake,
        preview=(mock if preview is None else preview) and not (web or api),
        rotate=rotate,
        mirror=mirror,
    )
    catalog = Catalog(load_personal(config))
    try:
        player = catalog.build(scene.value, text=text, color=rgb)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if web or api:
        service = MatrixService(runner, ctrl, catalog, shutdown=None if web else power_off)
        service.control.set_base(player)
        service.scene_name = scene.value
        serve(service, host, port, play=lambda: runner.play(service.control, seconds=seconds))
        return
    runner.play(player, seconds=seconds)
