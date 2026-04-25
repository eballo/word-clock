from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

logger = getLogger(__name__)

SUPPORTED_LANGUAGES = ("english",)

_WEB_DIR = Path(__file__).parent.parent / "web"


def _get_layout(lang: str):
    if lang == "english":
        from wordclock.layouts.english import (
            NUM_COLS,
            NUM_ROWS,
            build_display_grid,
            get_leds_for_time,
        )
        return build_display_grid, get_leds_for_time, NUM_ROWS, NUM_COLS
    raise ValueError(f"Unsupported language: {lang}")


class BrightnessRequest(BaseModel):
    brightness: int


def create_app(led_controller=None) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    app.state.led_controller = led_controller
    app.state.grids = {"english": _get_layout("english")[0]()}

    templates = Jinja2Templates(directory=_WEB_DIR / "templates")
    app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")

    def _push_leds(indices: list[int]) -> None:
        ctrl = app.state.led_controller
        if ctrl:
            ctrl.display_leds(indices)

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse(request, "index.html")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/api/grid")
    def get_grid(lang: str = "english"):
        if lang not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unknown language: {lang}")
        _, _, num_rows, num_cols = _get_layout(lang)
        grid = app.state.grids[lang]
        return {
            "language": lang,
            "rows": num_rows,
            "cols": num_cols,
            "grid": [list(row) for row in grid],
        }

    @app.get("/api/time")
    def get_time(lang: str = "english", h: int | None = None, m: int | None = None):
        if lang not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unknown language: {lang}")
        now = datetime.now()
        h = h if h is not None else now.hour
        m = m if m is not None else now.minute
        if not (0 <= h <= 23):
            raise HTTPException(status_code=400, detail="h must be 0-23")
        if not (0 <= m <= 59):
            raise HTTPException(status_code=400, detail="m must be 0-59")
        _, get_leds, _, _ = _get_layout(lang)
        grid = app.state.grids[lang]
        result = get_leds(h, m, grid=grid)
        _push_leds(result["led_indices"])
        return {
            "language": lang,
            "hours": result["hours"],
            "minutes": result["minutes"],
            "sentence": result["sentence"],
            "coords": result["coords"],
            "led_indices": result["led_indices"],
        }

    @app.post("/api/brightness")
    def set_brightness(body: BrightnessRequest):
        if not (0 <= body.brightness <= 255):
            raise HTTPException(status_code=400, detail="brightness must be an integer 0-255")
        ctrl = app.state.led_controller
        if ctrl:
            ctrl.brightness = body.brightness
        return {"brightness": body.brightness}

    return app


def _run_app(app: FastAPI, host: str, port: int, debug: bool) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="debug" if debug else "info")


def main() -> None:
    parser = ArgumentParser(description="Wordclock API server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", "-p", default=5000, type=int)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    basicConfig(
        level=DEBUG if args.debug else INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )

    from wordclock.led.controller import create_controller

    ctrl = create_controller(mock=args.mock)
    app = create_app(led_controller=ctrl)
    logger.info("Wordclock API → http://%s:%d", args.host, args.port)
    _run_app(app, host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
