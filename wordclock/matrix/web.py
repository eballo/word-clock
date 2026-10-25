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
from wordclock.matrix.button import ButtonAction, ButtonHandler
from wordclock.matrix.canvas import Color, hex_to_color, strip_to_canvas
from wordclock.matrix.catalog import Catalog
from wordclock.matrix.control import ControlledScene
from wordclock.matrix.photo import pixelate
from wordclock.matrix.runner import MatrixRunner

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

    def get_state(self) -> list[Color]:
        with self._lock:
            return list(self._frame)


class SceneRequest(BaseModel):
    name: str
    text: str = "HOLA"
    color: str | None = None


class ButtonRequest(BaseModel):
    down: bool


class PressRequest(BaseModel):
    action: ButtonAction = ButtonAction.TOGGLE


class BrightnessRequest(BaseModel):
    brightness: int


class PhotoRequest(BaseModel):
    image: str


class MatrixService:
    """
    State shared by the play loop and the web requests: the simulator on
    the Mac, and the remote control on the Raspberry Pi.
    """

    def __init__(
        self,
        runner: MatrixRunner,
        controller: BaseLedController,
        catalog: Catalog,
        shutdown: Callable[[], None] | None = None,
    ) -> None:
        self.runner = runner
        self.controller = controller
        self.catalog = catalog
        self.button = ButtonHandler()
        self.scene_name = "show"
        self.capture_id = 0
        self.last_action = "none"
        self.control = ControlledScene(
            catalog.build("show"),
            capture=self.request_capture,
            shutdown=shutdown or self.simulated_shutdown,
        )

    def request_capture(self) -> None:
        """Ask the browser for a webcam frame."""
        self.capture_id += 1

    def simulated_shutdown(self) -> None:
        """Without a real shutdown, only say so."""
        logger.info("Shutdown requested (simulated)")

    def play(self, request: SceneRequest) -> None:
        """
        Switch to the scene a request asks for.

        Args:
            request: Scene name, text and colour.

        Raises:
            ValueError: If the scene or the colour is not valid.
        """
        color = hex_to_color(request.color) if request.color else None
        self.control.set_base(self.catalog.build(request.name, text=request.text, color=color))
        self.scene_name = request.name

    def press(self, action: ButtonAction) -> None:
        """
        Do what a button press asks for.

        Args:
            action: The action of the press.
        """
        self.control.handle(action)
        self.last_action = action.value


def create_matrix_app(service: MatrixService) -> FastAPI:
    """
    Build the web page that draws the matrix and the API that drives it.

    Args:
        service: The shared matrix state.

    Returns:
        The FastAPI app.
    """
    app = FastAPI()
    templates = Jinja2Templates(directory=_WEB_DIR / "templates")
    app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")
    runner = service.runner
    canvas = runner.canvas

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "matrix.html",
            {
                "face": scad_params(MATRIX_SCAD, FACE_PARAMS),
                "scenes": service.catalog.available(),
            },
        )

    @app.get("/api/matrix/frame")
    def frame() -> dict:
        picture = strip_to_canvas(
            service.controller.get_state(),
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
            "brightness": service.controller.brightness,
            "lights": service.control.lights_on,
            "scene": service.scene_name,
            "capture": service.capture_id,
            "action": service.last_action,
        }

    @app.get("/api/matrix/scenes")
    def scenes() -> dict:
        return {"scenes": list(service.catalog.available()), "scene": service.scene_name}

    @app.post("/api/matrix/scene")
    def scene(request: SceneRequest) -> dict:
        try:
            service.play(request)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"scene": request.name}

    @app.post("/api/matrix/button")
    def button(request: ButtonRequest) -> dict:
        if request.down:
            service.button.press()
            return {"action": "none"}
        action = service.button.release()
        service.press(action)
        return {"action": action.value}

    @app.post("/api/matrix/press")
    def press(request: PressRequest) -> dict:
        service.press(request.action)
        return {"action": request.action.value}

    @app.post("/api/matrix/brightness")
    def brightness(request: BrightnessRequest) -> dict:
        if not 0 <= request.brightness <= 255:
            raise HTTPException(status_code=400, detail="brightness must be 0-255")
        service.controller.brightness = request.brightness
        return {"brightness": request.brightness}

    @app.post("/api/matrix/photo")
    def photo(request: PhotoRequest) -> dict:
        data = request.image.split(",", 1)[-1]
        try:
            pixels = pixelate(base64.b64decode(data), canvas.width, canvas.height)
        except (ValueError, UnidentifiedImageError) as exc:
            raise HTTPException(status_code=400, detail="image must be a JPEG or PNG") from exc
        service.control.show_photo(pixels, canvas.width)
        return {"cells": len(pixels)}

    return app


def serve(service: MatrixService, host: str, port: int, play: Callable[[], None]) -> None:
    """
    Play the matrix in the background and serve the page and the API.

    Args:
        service: The shared matrix state.
        host: Address to listen on.
        port: Port to listen on.
        play: The play loop, run in a background thread.
    """
    Thread(target=play, name="matrix-play", daemon=True).start()
    logger.info("Matrix page and API at http://%s:%d", host, port)
    uvicorn.run(
        create_matrix_app(service), host=host, port=port, log_level="warning", log_config=None
    )
