from __future__ import annotations

from enum import StrEnum
from logging import DEBUG, INFO, basicConfig
from pathlib import Path
from signal import SIGTERM, signal
from types import FrameType
from typing import Annotated

import typer

from wordclock.config import MATRIX_BRIGHTNESS, MATRIX_HEIGHT, MATRIX_MAX_MA, MATRIX_WIDTH
from wordclock.led.controller import create_controller
from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.runner import MatrixRunner
from wordclock.matrix.scenes import SCENE_NAMES, create_scene
from wordclock.matrix.show import ShowScene, load_personal

SceneName = StrEnum("SceneName", {name: name for name in SCENE_NAMES})

app = typer.Typer()


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
    digits = value.removeprefix("#")
    try:
        if len(digits) != 6:
            raise ValueError(value)
        return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16))
    except ValueError as exc:
        raise typer.BadParameter(f"Expected a hex colour like ff8800, got {value!r}") from exc


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
    config: Annotated[Path, typer.Option(help="Personal texts for the show, a TOML file")] = Path(
        "matrix.toml"
    ),
    debug: bool = False,
) -> None:
    """Play a scene on the mini LED matrix."""
    basicConfig(level=DEBUG if debug else INFO, format="%(asctime)s %(levelname)-8s %(message)s")
    signal(SIGTERM, stop_on_sigterm)
    rgb = parse_color(color) if color else None
    ctrl = create_controller(mock=mock, num_leds=width * height, brightness=brightness)
    runner = MatrixRunner(
        Canvas(width, height),
        ctrl,
        max_ma=max_ma,
        snake=snake,
        preview=mock if preview is None else preview,
        rotate=rotate,
        mirror=mirror,
    )
    if scene == SceneName.show:
        player = ShowScene(load_personal(config))
    else:
        player = create_scene(scene.value, text=text, color=rgb)
    runner.play(player, seconds=seconds)
