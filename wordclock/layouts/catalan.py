"""
Catalan layout 16x16 (256 LEDs, snake wiring).

Raw grid is defined in data/catalan.json.
GRID_RAW is the final display matrix produced once at import time.

Time sentences use the Catalan quarters system (references the NEXT hour):
  X:00  → ÉS/SÓN LA/LES <HOUR> EN PUNT
  X:05  → ÉS/SÓN VORA LA/LES <HOUR>
  X:15  → ÉS UN QUART DE/D' <HOUR+1>
  X:25  → SÓN DOS QUARTS DE/D' <HOUR+1> MENYS CINC
  X:30  → SÓN DOS QUARTS DE/D' <HOUR+1>
  X:45  → SÓN TRES QUARTS DE/D' <HOUR+1>
  X:55  → SÓN VORA LA/LES <HOUR+1>
"""

from __future__ import annotations

import wordclock.layouts.base as base
from wordclock.layouts.base import LedResult
from wordclock.layouts.utils import load_grid

GRID_RAW: list[str] = load_grid("catalan")

NUM_ROWS: int = len(GRID_RAW)
NUM_COLS: int = len(GRID_RAW[0])

# "D'" must be split so the apostrophe token can be found in the grid
_NORMALIZE: dict[str, str] = {"D'": "D' "}

HOUR_WORDS: list[str] = [
    "DOTZE",
    "UNA",
    "DUES",
    "TRES",
    "QUATRE",
    "CINC",
    "SIS",
    "SET",
    "VUIT",
    "NOU",
    "DEU",
    "ONZE",
]


def time_to_sentence(hours: int, minutes: int) -> str:
    """
    Convert hours (0-23) and minutes (0-59) to a Catalan word clock sentence.

    Args:
        hours: Hour value 0-23.
        minutes: Minute value 0-59.

    Returns:
        Sentence in ALL CAPS, e.g. ``"SÓN DOS QUARTS DE DEU"``.
    """
    h = hours % 12
    m = (minutes // 5) * 5

    ph = (h + 1) % 12
    ph_word = HOUR_WORDS[ph]
    prep = "D'" if ph_word in ("UNA", "ONZE") else "DE"

    if m == 0:
        verb = "ÉS" if h == 1 else "SÓN"
        art = "LA" if h == 1 else "LES"
        return f"{verb} {art} {HOUR_WORDS[h]} EN PUNT"

    if m in (5, 10):
        verb = "ÉS" if h == 1 else "SÓN"
        art = "LA" if h == 1 else "LES"
        return f"{verb} VORA {art} {HOUR_WORDS[h]}"

    if m == 15:
        return f"ÉS UN QUART {prep} {ph_word}"
    if m == 20:
        return f"ÉS UN QUART I CINC {prep} {ph_word}"
    if m == 25:
        return f"SÓN DOS QUARTS {prep} {ph_word} MENYS CINC"
    if m == 30:
        return f"SÓN DOS QUARTS {prep} {ph_word}"
    if m == 35:
        return f"SÓN DOS QUARTS I CINC {prep} {ph_word}"
    if m == 40:
        return f"SÓN TRES QUARTS {prep} {ph_word} MENYS CINC"
    if m == 45:
        return f"SÓN TRES QUARTS {prep} {ph_word}"
    if m == 50:
        return f"SÓN TRES QUARTS I CINC {prep} {ph_word}"
    if m == 55:
        art = "LA" if ph == 1 else "LES"
        return f"SÓN VORA {art} {ph_word}"

    raise ValueError(f"Unhandled minute value: {minutes}")


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


def coords_to_led_indices(coords: list[tuple[int, int]], snake: bool = True) -> list[int]:
    """
    Convert ``(row, col)`` pairs to absolute LED indices.

    Args:
        coords: List of ``(row, col)`` pairs.
        snake: Apply snake wiring. Default ``True``.

    Returns:
        List of integer LED indices.
    """
    return base.coords_to_led_indices(coords, NUM_COLS, snake=snake)


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
    sentence = time_to_sentence(hours, minutes)
    coords = sentence_to_coords(sentence, grid)
    led_indices = coords_to_led_indices(coords, snake=snake)
    return LedResult(
        sentence=sentence,
        coords=coords,
        led_indices=led_indices,
        hours=hours,
        minutes=minutes,
    )


if __name__ == "__main__":
    cases = [
        (1, 0),
        (2, 5),
        (10, 15),
        (12, 30),
        (4, 45),
        (11, 55),
    ]
    print("=" * 55)
    print("  Catalan word clock — layout test")
    print("=" * 55)
    print(f"\n{'TIME':<8} | {'SENTENCE'}")
    print("-" * 40)
    for h, m in cases:
        res = get_leds_for_time(h, m)
        print(f"{h:02d}:{m:02d}    | {res['sentence']}")
