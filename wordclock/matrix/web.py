from __future__ import annotations

import ast
import base64
import operator
import re
from collections.abc import Callable
from logging import getLogger
from pathlib import Path
from threading import Lock, Thread

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import UnidentifiedImageError
from pydantic import BaseModel

from wordclock.led.controller import BaseLedController
from wordclock.matrix.button import ButtonHandler
from wordclock.matrix.canvas import Color, hex_to_color, strip_to_canvas
from wordclock.matrix.control import ControlledScene
from wordclock.matrix.photo import pixelate
from wordclock.matrix.runner import MatrixRunner
from wordclock.matrix.scenes import SCENE_NAMES, Scene, create_scene
from wordclock.matrix.show import Personal, ShowScene

logger = getLogger(__name__)

_WEB_DIR = Path(__file__).parent.parent / "web"
MATRIX_SCAD = Path(__file__).parent.parent / "cad" / "matrix.scad"

# Face sizes the simulator draws, read from the OpenSCAD model so the two
# never disagree.
FACE_PARAMS: tuple[str, ...] = (
    "cols",
    "rows",
    "pitch",
    "margin",
    "margin_bottom",
    "outer_t",
    "bar_w",
    "window_r",
    "rivet_d",
    "rivet_pitch",
    "cam_lens",
    "cam_rivet",
)

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _evaluate(node: ast.AST) -> float | list[float]:
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return node.value
    if isinstance(node, ast.List):
        return [_evaluate(item) for item in node.elts]
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError(f"Not a plain number: {ast.dump(node)}")


def scad_params(path: Path, names: tuple[str, ...]) -> dict[str, float | list[float]]:
    """
    Read plain numeric parameters from an OpenSCAD file.

    Args:
        path: The ``.scad`` file.
        names: The parameters to read, assigned as ``name = <number>;`` with
            plain arithmetic or a list of numbers.

    Returns:
        The value of each parameter.

    Raises:
        KeyError: If a parameter is missing.
    """
    found: dict[str, float | list[float]] = {}
    for match in re.finditer(r"^(\w+)\s*=\s*([^;]+);", path.read_text(encoding="utf-8"), re.M):
        name, expression = match.groups()
        if name in names and name not in found:
            found[name] = _evaluate(ast.parse(expression, mode="eval").body)
    missing = [name for name in names if name not in found]
    if missing:
        raise KeyError(f"Missing in {path.name}: {', '.join(missing)}")
    return found


class WebLedController(BaseLedController):
    """LEDs drawn in the browser: keeps the last frame sent to the strip."""

    def __init__(self, num_leds: int, brightness: int) -> None:
        super().__init__(num_leds=num_leds, brightness=brightness)
        self._lock = Lock()
        self._frame: list[Color] = [(0, 0, 0)] * num_leds

    def begin(self) -> None:
        pass

    def show(self) -> None:
        with self._lock:
            self._frame = list(self._pixels)

    def clear(self) -> None:
        self._pixels = [(0, 0, 0)] * self.num_leds
        self.show()

    def frame(self) -> list[Color]:
        """
        Return the colours on the strip.

        Returns:
            One colour per LED, LED 0 first.
        """
        with self._lock:
            return list(self._frame)


class SceneRequest(BaseModel):
    name: str
    text: str = "HOLA"
    color: str | None = None


class ButtonRequest(BaseModel):
    down: bool


class BrightnessRequest(BaseModel):
    brightness: int


class PhotoRequest(BaseModel):
    image: str


class Simulator:
    """State shared by the play loop and the web requests."""

    def __init__(
        self, runner: MatrixRunner, controller: WebLedController, personal: Personal
    ) -> None:
        self.runner = runner
        self.controller = controller
        self.personal = personal
        self.button = ButtonHandler()
        self.scene_name = "show"
        self.capture_id = 0
        self.last_action = "none"
        self.control = ControlledScene(
            ShowScene(personal), capture=self.request_capture, shutdown=self.shutdown
        )

    def request_capture(self) -> None:
        """Ask the browser for a webcam frame."""
        self.capture_id += 1

    def shutdown(self) -> None:
        """A real matrix would shut down here; the simulator only says so."""
        logger.info("Shutdown requested (simulated)")

    def build_scene(self, request: SceneRequest) -> Scene:
        """
        Build the scene a request asks for.

        Args:
            request: Scene name, text and colour.

        Returns:
            The new scene.

        Raises:
            ValueError: If the scene or the colour is not valid.
        """
        if request.name == "show":
            return ShowScene(self.personal)
        color = hex_to_color(request.color) if request.color else None
        return create_scene(request.name, text=request.text, color=color)


def create_matrix_app(simulator: Simulator) -> FastAPI:
    """
    Build the web simulator: a page that draws the matrix and an API that
    drives it.

    Args:
        simulator: The shared simulator state.

    Returns:
        The FastAPI app.
    """
    app = FastAPI()
    templates = Jinja2Templates(directory=_WEB_DIR / "templates")
    app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")
    runner = simulator.runner
    canvas = runner.canvas

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "matrix.html",
            {"face": scad_params(MATRIX_SCAD, FACE_PARAMS), "scenes": SCENE_NAMES},
        )

    @app.get("/api/matrix/frame")
    def frame() -> dict:
        controller = simulator.controller
        picture = strip_to_canvas(
            controller.frame(),
            canvas.width,
            canvas.height,
            runner.snake,
            runner.rotate,
            runner.mirror,
        )
        return {
            "width": canvas.width,
            "height": canvas.height,
            "cells": picture.rows(),
            "brightness": controller.brightness,
            "lights": simulator.control.lights_on,
            "scene": simulator.scene_name,
            "capture": simulator.capture_id,
            "action": simulator.last_action,
        }

    @app.post("/api/matrix/scene")
    def scene(request: SceneRequest) -> dict:
        try:
            simulator.control.set_base(simulator.build_scene(request))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        simulator.scene_name = request.name
        return {"scene": request.name}

    @app.post("/api/matrix/button")
    def button(request: ButtonRequest) -> dict:
        if request.down:
            simulator.button.press()
            return {"action": "none"}
        action = simulator.button.release()
        simulator.control.handle(action)
        simulator.last_action = action.value
        return {"action": action.value}

    @app.post("/api/matrix/brightness")
    def brightness(request: BrightnessRequest) -> dict:
        if not 0 <= request.brightness <= 255:
            raise HTTPException(status_code=400, detail="brightness must be 0-255")
        simulator.controller.brightness = request.brightness
        return {"brightness": request.brightness}

    @app.post("/api/matrix/photo")
    def photo(request: PhotoRequest) -> dict:
        data = request.image.split(",", 1)[-1]
        try:
            pixels = pixelate(base64.b64decode(data), canvas.width, canvas.height)
        except (ValueError, UnidentifiedImageError) as exc:
            raise HTTPException(status_code=400, detail="image must be a JPEG or PNG") from exc
        simulator.control.show_photo(pixels, canvas.width)
        return {"cells": len(pixels)}

    return app


def serve(simulator: Simulator, host: str, port: int, play: Callable[[], None]) -> None:
    """
    Play the matrix in the background and serve the simulator page.

    Args:
        simulator: The shared simulator state.
        host: Address to listen on.
        port: Port to listen on.
        play: The play loop, run in a background thread.
    """
    Thread(target=play, name="matrix-play", daemon=True).start()
    logger.info("Simulator at http://%s:%d", host, port)
    uvicorn.run(
        create_matrix_app(simulator), host=host, port=port, log_level="warning", log_config=None
    )
