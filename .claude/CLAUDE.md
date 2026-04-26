# Word Clock — Project Skill

Read this file before writing any documentation, API code, or Python
for this project. It captures all conventions agreed during development.

---

## Project overview

A 16×16 LED word clock (256 WS2812B LEDs, 30 LEDs/metre) built on a
Raspberry Pi. Frame: 65×65 cm, LED matrix: 53.3×53.3 cm, cell: 3.33 cm.
Front panel: 3D-printed, opaque black, interchangeable per language.
Supported languages: English, Catalan, Spanish.

**Stack:**
- Python 3.13+, managed by `uv`
- FastAPI + uvicorn (API + web simulator)
- Typer (CLI — `wordclock` and `wordclock-generate` entry points)
- jinja2 + aiofiles (templates + static files)
- rpi-ws281x (Raspberry Pi only, optional extra)
- pytest + pytest-cov + ruff + pre-commit (dev)

---

## Repository structure

```
word-clock/
├── prototype/              # Original JS simulator — do not modify
├── wordclock/              # Python package
│   ├── api/
│   │   ├── app.py          # create_app() factory — middleware, state, router
│   │   └── routes.py       # All FastAPI route handlers
│   ├── layouts/
│   │   ├── base.py         # LedResult, LayoutModule protocol, shared functions
│   │   ├── registry.py     # SUPPORTED_LANGUAGES, get_layout()
│   │   ├── english.py      # English layout
│   │   ├── catalan.py      # Catalan layout
│   │   ├── spanish.py      # Spanish layout
│   │   ├── data/           # JSON files: raw + static grid per language
│   │   └── utils/          # Layout utility package
│   │       ├── __init__.py # Re-exports: Layout, create_layout, load_grid, …
│   │       ├── grid.py     # create_layout() — pure filler replacement
│   │       ├── layout.py   # Layout class, load_grid(), generate_static()
│   │       └── cli.py      # wordclock-generate CLI entry point
│   ├── led/
│   │   └── controller.py   # BaseLedController, RealLedController, MockLedController
│   ├── web/                # Templates + static (CSS, JS)
│   │   ├── templates/index.html
│   │   └── static/{css,js}/wordclock.*
│   ├── clock.py            # run_clock() and serve() logic
│   └── main.py             # Thin CLI entry points only
├── tests/
│   ├── unit/
│   │   └── layouts/        # One file per layout + base + registry
│   └── integration/
│       └── api/            # FastAPI TestClient tests
├── docs/                   # Numbered markdown docs (see below)
├── .claude/
│   └── CLAUDE.md           # This file
├── .pre-commit-config.yaml
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## Documentation conventions

### Language
Always write documentation in **English**.

### File naming
Numbered with two digits: `01-introduction.md`, `02-hardware.md`, etc.

### Structure of each doc
```markdown
# NN — Title

## Overview
One short paragraph summarising what this doc covers.

---

## 1. Section
...

## 2. Section
...
```

### Style rules
- Use **tables** for specs, dimensions, and component lists.
- Use **ASCII diagrams** for physical layouts, wiring, and layer stacks.
- Use **code blocks** with the correct language tag for all commands and code.
- Measurements always include units: `53.3 cm`, `3.33 cm`, `30 LEDs/metre`.
- Hardware references use the exact model: `WS2812B`, `GPIO 18`, `74AHCT125`.
- End each doc with a checklist (`- [ ]`) when it describes a build process.
- Never use the word "straightforward" or "simple".

### Decisions already made (do not re-discuss)
| Topic | Decision |
|-------|----------|
| Frame size | 65 × 65 cm |
| LED matrix | 53.3 × 53.3 cm |
| Cell size | 3.33 × 3.33 cm (30 LEDs/metre) |
| LED count | 256 (16 × 16) |
| Front panel | 3D-printed, opaque black PLA/PETG |
| Wiring | Snake (even rows L→R, odd rows R→L) |
| Power | 5V 10A PSU, inject at row 0 and row 8 |
| GPIO | GPIO 18 (PWM), level shifter 74AHCT125 |
| OS | Raspberry Pi OS Lite 64-bit |
| Auto-start | systemd service |
| Hostname | wordclock.local |

---

## API conventions

### App factory
Always use `create_app(led_controller=None)` factory in `api/app.py`.
Never create the app at module level.
Route handlers live in `api/routes.py` and are registered via `app.include_router(router)`.
Shared state (grids, templates, led_controller) is stored in `app.state` and accessed
inside handlers via `request.app.state`.

### Endpoint structure
```
GET  /api/health
GET  /api/grid?lang=english
GET  /api/time?lang=english&h=10&m=30
POST /api/brightness   {"brightness": 128}
GET  /                 → web simulator (index.html)
```

### Response format
All responses return JSON. Success:
```json
{
  "language":    "english",
  "hours":       10,
  "minutes":     30,
  "sentence":    "IT IS HALF PAST TEN",
  "coords":      [[2, 0], [2, 1], ...],
  "led_indices": [32, 33, ...]
}
```

Error (FastAPI `HTTPException`):
```json
{"detail": "h must be 0-23"}
```

### HTTP status codes
- `200` success
- `400` bad input (wrong parameter type or out of range)
- Never use `404` for wrong language — use `400` with a clear message

### Language support
Languages are defined in `layouts/registry.py`:
```python
SUPPORTED_LANGUAGES: tuple[str, ...] = ("english", "catalan", "spanish")
```
To add a new language: add to the tuple, create `layouts/<lang>.py` and `layouts/data/<lang>.json`.
Use `get_layout(lang)` from the registry — never import layouts directly in `app.py`.

### CORS
Always enable with `CORSMiddleware` — needed for the web simulator.

---

## Layout conventions (wordclock/layouts/)

### Shared contract
Every layout module must satisfy the `LayoutModule` protocol defined in `layouts/base.py`:
- `GRID_RAW: list[str]` — final display matrix (loaded via `load_grid()` at import time)
- `NUM_ROWS: int`, `NUM_COLS: int`
- `HOUR_WORDS: list[str]`
- `time_to_sentence(hours, minutes) -> str` — always named exactly this
- `get_leds_for_time(hours, minutes, grid, snake) -> LedResult`

### Grid design rules
- Raw grids live in `layouts/data/<lang>.json` under the `"raw"` key.
- **Filler character is `x` (lowercase)** — never use a letter that appears in a
  real word as filler.
  Exception: uppercase `X` is a real letter (e.g. in SIX) and must be preserved.
- All rows must be exactly `NUM_COLS` characters (16).
- Words must be findable left-to-right within a single row.
- Run `uv run wordclock-generate --lang <name>` to generate and persist the
  static version into the JSON file's `"static"` key.

### load_grid() / GRID_RAW
`GRID_RAW` in each layout is the final display matrix, computed once at import:
```python
GRID_RAW: list[str] = load_grid("english")
```
`load_grid()` returns the `"static"` field from the JSON if present, otherwise
computes it from `"raw"` via `create_layout()`. Run `wordclock-generate` to
populate `"static"` before deploying.

### time_to_sentence()
Returns a sentence in ALL CAPS, e.g. `"IT IS A QUARTER PAST TEN"`.
Words separated by single spaces. No punctuation.
Function must be named `time_to_sentence` in every layout module.

### sentence_to_coords()
Thin wrapper over `base.sentence_to_coords()`. Pass a `normalize` dict for
language-specific substitutions before word splitting:
- Catalan: `{"D'": "D' "}` (splits the preposition token)
- Spanish: `{"VEINTICINCO": "VEINTE CINCO"}` (word does not fit one row)

### get_leds_for_time()
Main entry point. Returns `LedResult` (TypedDict from `layouts/base.py`):
```python
{
    "sentence":    str,
    "coords":      list[tuple[int, int]],
    "led_indices": list[int],
    "hours":       int,
    "minutes":     int,
}
```

---

## LED controller conventions

### MockLedController
- Accepts `grid: list[str]` passed via `create_controller(grid=grid)`.
- `display_leds()` logs the active indices and prints the grid with ANSI
  bold (active letters) and ANSI dim (inactive letters).
- Use `logger.info` for the LED count, `print()` for the grid itself.

### clock.py
Clock loop logic lives in `wordclock/clock.py`. Always pass the grid when
creating the controller in mock mode:
```python
grid = GRID_RAW
ctrl = create_controller(mock=mock, brightness=brightness, grid=grid if mock else None)
```

### create_controller()
- `mock=True` → always returns `MockLedController`
- `mock=False` → tries `RealLedController`, falls back to mock on failure

---

## Python conventions

- `from __future__ import annotations` at the top of every module.
- Type hints everywhere (return types, parameters).
- Specific imports: `from logging import getLogger` not `import logging`.
- `logger = getLogger(__name__)` in every module that logs.
- No bare `except` — always catch specific exceptions.
- Constants in `UPPER_SNAKE_CASE`, including `frozenset`.
- `Callable` imported from `collections.abc`, not `typing`.
- Docstrings on all public functions with `Args:` and `Returns:` sections.

---

## Test conventions

### Structure
```
tests/
├── unit/
│   └── layouts/    # test_english_layout.py, test_catalan_layout.py,
│                   # test_spanish_layout.py, test_base.py, test_registry.py
└── integration/
    └── api/        # conftest.py (client fixture), test_api.py, test_languages.py
```

### Style
- All test methods annotated with `-> None`.
- Given / When / Then inline comments in every test body.
- Group tests in classes: `TestTimeToSentence`, `TestSentenceToCoords`, `TestGetLedsForTime`.
- Always include a parametrized test that covers all 24×12 time combinations.

### Layout tests (tests/unit/layouts/)
- One file per layout module.
- Tests import directly from `wordclock.layouts.<lang>`.

### API tests (tests/integration/api/)
- Shared `client` fixture in `conftest.py` using `create_app(led_controller=None)`.
- Test all endpoints: health, grid, time (valid + invalid), brightness.
- Assert both status code and response body.
- Use `r.json()` (not `r.get_json()`).

### Running tests
```bash
uv run pytest                          # all tests with coverage
uv run pytest tests/unit/              # unit tests only
uv run pytest tests/integration/       # integration tests only
uv run pytest tests/unit/layouts/      # layout tests only
uv run pytest -k "test_quarter"        # filter by name
```

---

## Common commands

```bash
uv sync --extra dev                    # install all dev dependencies
uv run wordclock --mock --debug        # run clock loop with grid display
uv run wordclock-api --mock            # run FastAPI + web simulator
uv run wordclock-serve --mock          # run clock loop + API together
uv run wordclock-generate --lang ca    # generate static grid for a language
uv run pytest                          # run tests
uv run ruff check .                    # lint
uv run ruff format .                   # format
uv run pre-commit run --all-files      # run all pre-commit hooks manually
```
