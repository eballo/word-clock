"""FastAPI route handlers."""

from __future__ import annotations

from datetime import datetime
from logging import getLogger

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from wordclock.layouts.registry import SUPPORTED_LANGUAGES, get_layout

logger = getLogger(__name__)

router = APIRouter()


class BrightnessRequest(BaseModel):
    brightness: int


def _push_leds(request: Request, indices: list[int]) -> None:
    ctrl = request.app.state.led_controller
    if ctrl:
        ctrl.display_leds(indices)


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(request, "index.html")


@router.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}


@router.get("/api/grid")
def get_grid(request: Request, lang: str = "english") -> dict:
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unknown language: {lang}")
    logger.debug("Fetching grid for language: %s", lang)
    layout = get_layout(lang)
    grid = request.app.state.grids[lang]
    return {
        "language": lang,
        "rows": layout.NUM_ROWS,
        "cols": layout.NUM_COLS,
        "grid": [list(row) for row in grid],
    }


@router.get("/api/time")
def get_time(
    request: Request,
    lang: str = "english",
    h: int | None = None,
    m: int | None = None,
) -> dict:
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unknown language: {lang}")
    logger.debug("Fetching time for language: %s, h: %s, m: %s", lang, h, m)
    now = datetime.now()
    h = h if h is not None else now.hour
    m = m if m is not None else now.minute
    if not (0 <= h <= 23):
        raise HTTPException(status_code=400, detail="h must be 0-23")
    if not (0 <= m <= 59):
        raise HTTPException(status_code=400, detail="m must be 0-59")
    layout = get_layout(lang)
    grid = request.app.state.grids[lang]
    result = layout.get_leds_for_time(h, m, grid=grid)
    _push_leds(request, result["led_indices"])
    return {
        "language": lang,
        "hours": result["hours"],
        "minutes": result["minutes"],
        "sentence": result["sentence"],
        "coords": result["coords"],
        "led_indices": result["led_indices"],
    }


@router.post("/api/brightness")
def set_brightness(request: Request, body: BrightnessRequest) -> dict:
    if not (0 <= body.brightness <= 255):
        raise HTTPException(status_code=400, detail="brightness must be an integer 0-255")
    ctrl = request.app.state.led_controller
    if ctrl:
        ctrl.brightness = body.brightness
    return {"brightness": body.brightness}
