"""FastAPI application factory."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from wordclock.api.routes import router
from wordclock.layouts.registry import SUPPORTED_LANGUAGES, get_layout

logger = getLogger(__name__)

_WEB_DIR = Path(__file__).parent.parent / "web"


def create_app(led_controller=None) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    app.state.led_controller = led_controller
    app.state.grids = {lang: get_layout(lang).GRID_RAW for lang in SUPPORTED_LANGUAGES}
    app.state.templates = Jinja2Templates(directory=_WEB_DIR / "templates")
    app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")
    app.include_router(router)
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
