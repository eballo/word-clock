from __future__ import annotations

import ast
import base64
import operator
import re
from collections.abc import Callable
from datetime import time as day_time
from importlib.metadata import PackageNotFoundError, version
from logging import getLogger
from pathlib import Path
from threading import Lock, Thread

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import UnidentifiedImageError
from pydantic import BaseModel, Field

from wordclock.led.controller import BaseLedController
from wordclock.matrix.button import ButtonAction, ButtonHandler
from wordclock.matrix.canvas import Color, hex_to_color, strip_to_canvas
from wordclock.matrix.catalog import Catalog
from wordclock.matrix.control import ControlledScene
from wordclock.matrix.languages import MatrixLanguage
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


API_DESCRIPTION = """
Drive the 10 x 6 LED matrix: switch scenes, press the button, change the
brightness and the language, and read the frame on the strip.

The same API runs in the web simulator (`wordclock-matrix --web`) and on
the Raspberry Pi (`wordclock-matrix --api`). There is no password: keep it
on the home network.
"""

OPENAPI_TAGS: list[dict[str, str]] = [
    {"name": "matrix", "description": "What the matrix shows and how."},
    {"name": "button", "description": "The button on the face: lights, photo and shutdown."},
    {"name": "simulator", "description": "Helpers to test the matrix: time of day and photo."},
    {"name": "page", "description": "The web page that draws the matrix."},
]


def package_version() -> str:
    """
    Read the installed version of the project.

    Returns:
        The version, or ``0.0.0`` when the package is not installed.
    """
    try:
        return version("wordclock")
    except PackageNotFoundError:
        return "0.0.0"


class SceneRequest(BaseModel):
    name: str = Field(description="A scene of GET /api/matrix/scenes", examples=["pomodoro"])
    text: str = Field("HOLA", description="Text for the text scene")
    color: str | None = Field(None, description="Hex colour, e.g. ff8800", examples=["ff8800"])


class ButtonRequest(BaseModel):
    down: bool = Field(description="True when the button goes down, False when it is released")


class PressRequest(BaseModel):
    action: ButtonAction = Field(ButtonAction.TOGGLE, description="What the press does")


class BrightnessRequest(BaseModel):
    brightness: int = Field(description="Strip brightness, 0-255", examples=[80])


class TimeRequest(BaseModel):
    time: str | None = Field(
        None, description="Time of day as HH:MM, or null for the real time", examples=["23:30"]
    )


class LanguageRequest(BaseModel):
    language: str = Field(description="english, catalan or spanish", examples=["english"])


class PhotoRequest(BaseModel):
    image: str = Field(description="A JPEG or PNG, as a data URL or plain base64")


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
    app = FastAPI(
        title="Mini Matrix API",
        version=package_version(),
        description=API_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
    )
    templates = Jinja2Templates(directory=_WEB_DIR / "templates")
    app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")
    runner = service.runner
    canvas = runner.canvas

    @app.get("/", response_class=HTMLResponse, tags=["page"], summary="Matrix page")
    def index(request: Request) -> HTMLResponse:
        """The page that draws the matrix as printed, with its controls."""
        return templates.TemplateResponse(
            request,
            "matrix.html",
            {
                "face": scad_params(MATRIX_SCAD, FACE_PARAMS),
                "scenes": service.catalog.available(),
                "languages": [language.value for language in MatrixLanguage],
            },
        )

    def day_state() -> dict:
        dimmer = runner.dimmer
        if dimmer is None:
            return {"time": None, "simulated_time": False, "phase": None, "sun": None}
        sun = dimmer.sun_times()
        return {
            "time": dimmer.now().strftime("%H:%M"),
            "simulated_time": dimmer.simulated,
            "phase": dimmer.phase().value,
            "sun": {
                "sunrise": sun.sunrise.strftime("%H:%M"),
                "sunset": sun.sunset.strftime("%H:%M"),
            },
        }

    @app.get("/api/matrix/frame", tags=["matrix"], summary="Read the frame and state")
    def frame() -> dict:
        """The colours on the matrix now, seen from the front, and its state."""
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
            "auto_brightness": runner.dimmer is not None and not runner.dimmer.manual,
            "language": service.catalog.locale.language.value,
            **day_state(),
            "lights": service.control.lights_on,
            "scene": service.scene_name,
            "capture": service.capture_id,
            "action": service.last_action,
        }

    @app.get("/api/matrix/scenes", tags=["matrix"], summary="List the scenes")
    def scenes() -> dict:
        """The scenes that can play with these settings, and the current one."""
        return {"scenes": list(service.catalog.available()), "scene": service.scene_name}

    @app.post("/api/matrix/scene", tags=["matrix"], summary="Play a scene")
    def scene(request: SceneRequest) -> dict:
        """Play a scene, with a text and a colour for the scenes that use them."""
        try:
            service.play(request)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"scene": request.name}

    @app.post("/api/matrix/button", tags=["button"], summary="Press or release the button")
    def button(request: ButtonRequest) -> dict:
        """Press or release the button; the release does what the hold time says."""
        if request.down:
            service.button.press()
            return {"action": "none"}
        action = service.button.release()
        service.press(action)
        return {"action": action.value}

    @app.post("/api/matrix/press", tags=["button"], summary="Press the button once")
    def press(request: PressRequest) -> dict:
        """A whole press of the button: lights on or off, photo or shutdown."""
        service.press(request.action)
        return {"action": request.action.value}

    @app.post("/api/matrix/brightness", tags=["matrix"], summary="Set the brightness")
    def brightness(request: BrightnessRequest) -> dict:
        """Set the brightness; the automatic one takes over at the next phase."""
        if not 0 <= request.brightness <= 255:
            raise HTTPException(status_code=400, detail="brightness must be 0-255")
        if runner.dimmer:
            runner.dimmer.set_manual(request.brightness)
        service.controller.brightness = request.brightness
        return {"brightness": request.brightness}

    @app.get("/api/matrix/language", tags=["matrix"], summary="Read the language")
    def get_language() -> dict:
        """The language of the texts, and the languages there are."""
        return {
            "language": service.catalog.locale.language.value,
            "languages": [language.value for language in MatrixLanguage],
        }

    @app.post("/api/matrix/language", tags=["matrix"], summary="Switch the language")
    def set_language(request: LanguageRequest) -> dict:
        """Switch the language live; the next text of every scene uses it."""
        try:
            language = MatrixLanguage(request.language)
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail=f"Unknown language: {request.language}"
            ) from exc
        service.catalog.locale.set(language)
        return get_language()

    @app.post("/api/matrix/time", tags=["simulator"], summary="Simulate a time of day")
    def simulated_time(request: TimeRequest) -> dict:
        """Preview the automatic brightness at another time of day."""
        if runner.dimmer is None:
            raise HTTPException(
                status_code=400, detail="The brightness is fixed: start without --brightness"
            )
        try:
            moment = day_time.fromisoformat(request.time) if request.time else None
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="time must be HH:MM") from exc
        runner.dimmer.simulate(moment)
        runner.controller.brightness = runner.dimmer.brightness()
        return day_state()

    @app.post("/api/matrix/photo", tags=["simulator"], summary="Show a photo")
    def photo(request: PhotoRequest) -> dict:
        """Show a picture on the matrix, pixelated to 10 x 6, like the camera photo."""
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
