from __future__ import annotations

from datetime import datetime
from importlib.metadata import version
from logging import getLogger

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from wordclock.api.schemas import BrightnessResponse, GridResponse, HealthResponse, TimeResponse
from wordclock.layouts.registry import Language, get_layout

logger = getLogger(__name__)

router = APIRouter(prefix="/api")


class BrightnessRequest(BaseModel):
    brightness: int


def _resolve_lang(lang: str) -> Language:
    try:
        return Language(lang)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown language: {lang}")


def _push_leds(request: Request, indices: list[int]) -> None:
    ctrl = request.app.state.led_controller
    if ctrl:
        ctrl.display_leds(indices)


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(request, "index.html")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=version("wordclock"))


@router.get("/grid", response_model=GridResponse)
def get_grid(request: Request, lang: str = "english") -> GridResponse:
    lang_enum = _resolve_lang(lang)
    logger.debug("Fetching grid for language: %s", lang_enum.value)
    grid = request.app.state.grids[lang_enum.value]
    rows, cols = request.app.state.dims[lang_enum.value]
    return GridResponse(
        language=lang_enum.value,
        rows=rows,
        cols=cols,
        grid=[list(row) for row in grid],
    )


@router.get("/time", response_model=TimeResponse)
def get_time(
    request: Request,
    lang: str = "english",
    h: int | None = None,
    m: int | None = None,
) -> TimeResponse:
    lang_enum = _resolve_lang(lang)
    logger.debug("Fetching time for language: %s, h: %s, m: %s", lang_enum.value, h, m)
    now = datetime.now()
    h = h if h is not None else now.hour
    m = m if m is not None else now.minute
    if not (0 <= h <= 23):
        raise HTTPException(status_code=400, detail="h must be 0-23")
    if not (0 <= m <= 59):
        raise HTTPException(status_code=400, detail="m must be 0-59")
    layout = get_layout(lang_enum)
    grid = request.app.state.grids[lang_enum.value]
    result = layout.get_leds_for_time(h, m, grid=grid)
    _push_leds(request, result["led_indices"])
    return TimeResponse(
        language=lang_enum.value,
        hours=result["hours"],
        minutes=result["minutes"],
        sentence=result["sentence"],
        coords=result["coords"],
        led_indices=result["led_indices"],
    )


@router.post("/brightness", response_model=BrightnessResponse)
def set_brightness(request: Request, body: BrightnessRequest) -> BrightnessResponse:
    if not (0 <= body.brightness <= 255):
        raise HTTPException(status_code=400, detail="brightness must be an integer 0-255")
    ctrl = request.app.state.led_controller
    if ctrl:
        ctrl.brightness = body.brightness
    return BrightnessResponse(brightness=body.brightness)
