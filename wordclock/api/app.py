from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from contextlib import asynccontextmanager, suppress
from logging import getLogger
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from wordclock.api.routes import router
from wordclock.layouts.registry import SUPPORTED_LANGUAGES, get_layout

logger = getLogger(__name__)

_WEB_DIR = Path(__file__).parent.parent / "web"
_ClockLoop = Callable[[], Coroutine[Any, Any, None]]


def create_app(led_controller: Any = None, clock_loop: _ClockLoop | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if clock_loop:
            task = asyncio.create_task(clock_loop())
            try:
                yield
            finally:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
        else:
            yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    _layouts = {lang: get_layout(lang) for lang in SUPPORTED_LANGUAGES}
    app.state.led_controller = led_controller
    app.state.grids = {lang: _layouts[lang].GRID_RAW for lang in SUPPORTED_LANGUAGES}
    app.state.dims = {
        lang: (_layouts[lang].NUM_ROWS, _layouts[lang].NUM_COLS) for lang in SUPPORTED_LANGUAGES
    }
    app.state.templates = Jinja2Templates(directory=_WEB_DIR / "templates")
    app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")
    app.include_router(router)
    return app


def run_app(app: FastAPI, host: str, port: int, debug: bool) -> None:
    uvicorn.run(app, host=host, port=port, log_level="debug" if debug else "info", log_config=None)
