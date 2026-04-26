"""
Spanish layout 16x16 (256 LEDs, snake wiring).

Raw grid is defined in data/spanish.json.
GRID_RAW is the final display matrix produced once at import time.

Time sentences use the Spanish Y/MENOS system:
  X:00  → ES/SON LA/LAS <HOUR> EN PUNTO
  X:15  → ES/SON LA/LAS <HOUR> Y CUARTO
  X:30  → ES/SON LA/LAS <HOUR> Y MEDIA
  X:35  → ES/SON LA/LAS <HOUR+1> MENOS VEINTICINCO
  X:45  → ES/SON LA/LAS <HOUR+1> MENOS CUARTO
"""

from __future__ import annotations

import wordclock.layouts.base as base
from wordclock.layouts.base import LedResult
from wordclock.layouts.registry import Language
from wordclock.layouts.utils import load_grid

GRID_RAW: list[str] = load_grid(Language.spanish)

NUM_ROWS: int = len(GRID_RAW)
NUM_COLS: int = len(GRID_RAW[0])

# "VEINTICINCO" does not fit in a single row; split before searching
_NORMALIZE: dict[str, str] = {"VEINTICINCO": "VEINTE CINCO"}

HOUR_WORDS: list[str] = [
    "DOCE",
    "UNA",
    "DOS",
    "TRES",
    "CUATRO",
    "CINCO",
    "SEIS",
    "SIETE",
    "OCHO",
    "NUEVE",
    "DIEZ",
    "ONCE",
]

_MINUS_MINUTES: frozenset[int] = frozenset({35, 40, 45, 50, 55})

_MINUTE_PHRASES: dict[int, str] = {
    5: "Y CINCO",
    10: "Y DIEZ",
    15: "Y CUARTO",
    20: "Y VEINTE",
    25: "Y VEINTICINCO",
    30: "Y MEDIA",
    35: "MENOS VEINTICINCO",
    40: "MENOS VEINTE",
    45: "MENOS CUARTO",
    50: "MENOS DIEZ",
    55: "MENOS CINCO",
}


def time_to_sentence(hours: int, minutes: int) -> str:
    """
    Convert hours (0-23) and minutes (0-59) to a Spanish word clock sentence.

    Args:
        hours: Hour value 0-23.
        minutes: Minute value 0-59.

    Returns:
        Sentence in ALL CAPS, e.g. ``"SON LAS DIEZ Y MEDIA"``.
    """
    h = hours % 12
    m = (minutes // 5) * 5

    if m in _MINUS_MINUTES:
        h = (h + 1) % 12

    verb = "ES" if h == 1 else "SON"
    art = "LA" if h == 1 else "LAS"
    h_word = HOUR_WORDS[h]

    if m == 0:
        return f"{verb} {art} {h_word} EN PUNTO"
    return f"{verb} {art} {h_word} {_MINUTE_PHRASES[m]}"


def sentence_to_coords(sentence: str, grid: list[str] | None = None) -> list[tuple[int, int]]:
    """
    Find each word of *sentence* in *grid* and return ``(row, col)`` pairs.

    Args:
        sentence: ALL-CAPS sentence from :func:`time_to_sentence`.
        grid: Grid to search; defaults to :data:`GRID_RAW`.

    Returns:
        List of ``(row, col)`` pairs for every lit letter.
    """
    return base.sentence_to_coords(
        sentence,
        GRID_RAW if grid is None else grid,
        NUM_ROWS,
        normalize=_NORMALIZE,
    )


def get_leds_for_time(
    hours: int,
    minutes: int,
    grid: list[str] | None = None,
    snake: bool = True,
) -> LedResult:
    """
    Return everything needed to update the display for a given time.

    Args:
        hours: Hour value 0-23.
        minutes: Minute value 0-59.
        grid: Grid to search; defaults to :data:`GRID_RAW`.
        snake: Apply snake wiring. Default ``True``.

    Returns:
        :class:`~wordclock.layouts.base.LedResult` dict.
    """
    return base.build_leds_for_time(
        hours,
        minutes,
        grid=grid if grid is not None else GRID_RAW,
        num_rows=NUM_ROWS,
        num_cols=NUM_COLS,
        time_to_sentence_fn=time_to_sentence,
        normalize=_NORMALIZE,
        snake=snake,
    )
