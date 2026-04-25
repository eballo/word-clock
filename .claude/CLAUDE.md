# Word Clock — Project Skill

Read this file before writing any documentation, API code, or Python
for this project. It captures all conventions agreed during development.

---

## Project overview

A 16×16 LED word clock (256 WS2812B LEDs, 30 LEDs/metre) built on a
Raspberry Pi. Frame: 65×65 cm, LED matrix: 53.3×53.3 cm, cell: 3.33 cm.
Front panel: 3D-printed, opaque black, interchangeable per language.
Primary language: English. Catalan planned next.

**Stack:**
- Python 3.11+, managed by `uv`
- FastAPI + uvicorn (API + web simulator)
- jinja2 + aiofiles (templates + static files)
- rpi-ws281x (Raspberry Pi only, optional extra)
- pytest + pytest-cov + ruff + pre-commit (dev)

---

## Repository structure

```
word-clock/
├── prototype/          # Original JS simulator — do not modify
├── wordclock/          # Python package
│   ├── layouts/        # One file per language (english.py, catalan.py…)
│   ├── led/            # LED controller (real + mock)
│   ├── api/            # FastAPI app (app.py)
│   ├── web/            # Templates + static (CSS, JS)
│   │   ├── templates/index.html
│   │   └── static/{css,js}/wordclock.*
│   ├── __init__.py
│   └── main.py         # Clock loop + serve entry points
├── tests/
│   ├── layouts/        # test_english_layout.py, test_catalan_layout.py…
│   └── api/            # test_api.py
├── docs/               # Numbered markdown docs (see below)
├── .claude/
│   └── CLAUDE.md       # This file
├── .pre-commit-config.yaml
├── pyproject.toml
├── .python-version     # 3.11
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

## API conventions (wordclock/api/app.py)

### App factory
Always use `create_app(led_controller=None)` factory pattern.
Never create the app at module level.

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
Languages are validated against `SUPPORTED_LANGUAGES = ("english",)`.
To add a new language: add to the tuple and add a branch in `_get_layout()`.

### CORS
Always enable with `CORSMiddleware` — needed for the web simulator.

---

## Layout conventions (wordclock/layouts/)

### Grid design rules
- **Filler character is `x` (lowercase)** — never use a letter that appears in a
  real word as filler, to avoid `build_display_grid()` corrupting words.
  Exception: uppercase `X` is a real letter (e.g. in SIX) and must be preserved.
- All rows must be exactly `NUM_COLS` characters (16).
- Words must be findable left-to-right within a single row.
- Comment each row with the words it contains.

### build_display_grid()
Replaces lowercase `x` with random uppercase letters. Accepts an optional `seed`
for deterministic output in tests.

### time_to_sentence()
Returns a sentence in ALL CAPS, e.g. `"IT IS A QUARTER PAST TEN"`.
Words separated by single spaces. No punctuation.

### sentence_to_coords()
Sequential search (same logic as the original JS `highlightWordFrom()`).
Returns `list[tuple[int, int]]` — (row, col) for each lit letter.

### get_leds_for_time()
Main entry point. Returns:
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

### main.py
Always pass the grid when creating the controller in mock mode:
```python
grid = build_display_grid()
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
- `logger = getLogger(__name__)` in every module.
- No bare `except` — always catch specific exceptions.
- Constants in `UPPER_SNAKE_CASE`, including `frozenset`.
- Docstrings on all public functions with `Args:` and `Returns:` sections.

---

## Test conventions

### Layout tests (tests/layouts/)
- One file per layout: `test_english_layout.py`, `test_catalan_layout.py`.
- Group tests in classes: `TestTimeToSentence`, `TestSentenceToCoords`,
  `TestGetLedsForTime`.
- Always include a parametrized test that covers all 24×12 time combinations.

### API tests (tests/api/test_api.py)
- Use `create_app(led_controller=None)` with FastAPI `TestClient`.
- Test all endpoints: health, grid, time (valid + invalid), brightness.
- Assert both status code and response body.
- Use `r.json()` (not `r.get_json()`).

### Running tests
```bash
uv run pytest                    # all tests with coverage
uv run pytest tests/layouts/     # layout tests only
uv run pytest -k "test_six"      # filter by name
```

---

## Common commands

```bash
uv sync --extra dev              # install all dev dependencies
uv run wordclock --mock --debug  # run clock loop with grid display
uv run wordclock-api --mock      # run FastAPI + web simulator
uv run wordclock-serve --mock    # run clock loop + API together
uv run pytest                    # run tests
uv run ruff check .              # lint
uv run ruff format .             # format
uv run pre-commit run --all-files  # run all pre-commit hooks manually
```