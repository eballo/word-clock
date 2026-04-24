from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime
from logging import basicConfig, getLogger, DEBUG, INFO

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

logger = getLogger(__name__)

SUPPORTED_LANGUAGES = ("english",)


def _get_layout(lang: str):
    if lang == "english":
        from wordclock.layouts.english import (
            build_display_grid, get_leds_for_time, NUM_ROWS, NUM_COLS
        )
        return build_display_grid, get_leds_for_time, NUM_ROWS, NUM_COLS
    raise ValueError(f"Unsupported language: {lang}")


def create_app(led_controller=None) -> Flask:
    app = Flask(
        __name__,
        template_folder="../web/templates",
        static_folder="../web/static",
    )
    CORS(app)
    app.config["LED_CONTROLLER"] = led_controller
    # Pre-build one grid per language
    app.config["GRIDS"] = {
        "english": _get_layout("english")[0](),
    }

    def _push_leds(indices: list[int]) -> None:
        ctrl = app.config.get("LED_CONTROLLER")
        if ctrl:
            ctrl.display_leds(indices)

    # ── Web ────────────────────────────────────────────────────────────
    @app.get("/")
    def index():
        return render_template("index.html")

    # ── API ────────────────────────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "0.1.0"})

    @app.get("/api/grid")
    def get_grid():
        lang = request.args.get("lang", "english")
        if lang not in SUPPORTED_LANGUAGES:
            return jsonify({"error": f"Unknown language: {lang}"}), 400

        _, _, num_rows, num_cols = _get_layout(lang)
        grid = app.config["GRIDS"][lang]
        return jsonify({
            "language": lang,
            "rows": num_rows,
            "cols": num_cols,
            "grid": [list(row) for row in grid],
        })

    @app.get("/api/time")
    def get_time():
        lang = request.args.get("lang", "english")
        if lang not in SUPPORTED_LANGUAGES:
            return jsonify({"error": f"Unknown language: {lang}"}), 400

        try:
            now = datetime.now()
            h = int(request.args.get("h", now.hour))
            m = int(request.args.get("m", now.minute))
        except (ValueError, TypeError):
            return jsonify({"error": "h and m must be integers"}), 400

        if not (0 <= h <= 23):
            return jsonify({"error": "h must be 0-23"}), 400
        if not (0 <= m <= 59):
            return jsonify({"error": "m must be 0-59"}), 400

        _, get_leds, _, _ = _get_layout(lang)
        grid = app.config["GRIDS"][lang]
        result = get_leds(h, m, grid=grid)
        _push_leds(result["led_indices"])

        return jsonify({
            "language":    lang,
            "hours":       result["hours"],
            "minutes":     result["minutes"],
            "sentence":    result["sentence"],
            "coords":      result["coords"],
            "led_indices": result["led_indices"],
        })

    @app.post("/api/brightness")
    def set_brightness():
        data = request.get_json(silent=True) or {}
        brightness = data.get("brightness")
        if not isinstance(brightness, int) or not (0 <= brightness <= 255):
            return jsonify({"error": "brightness must be an integer 0-255"}), 400
        ctrl = app.config.get("LED_CONTROLLER")
        if ctrl:
            ctrl.brightness = brightness
        return jsonify({"brightness": brightness})

    return app


def main() -> None:
    parser = ArgumentParser(description="Wordclock Flask API")
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
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)


if __name__ == "__main__":
    main()
