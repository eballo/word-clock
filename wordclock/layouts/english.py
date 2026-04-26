"""
English layout 16x16 (256 LEDs, snake wiring).

Raw grid is defined in data/english.json.
GRID_RAW is the final display matrix produced once at import time.

Time sentences:
  X:00  → IT IS <HOUR> OCLOCK
  X:05  → IT IS FIVE PAST <HOUR>
  X:10  → IT IS TEN PAST <HOUR>
  X:15  → IT IS A QUARTER PAST <HOUR>
  X:20  → IT IS TWENTY PAST <HOUR>
  X:25  → IT IS TWENTY FIVE PAST <HOUR>
  X:30  → IT IS HALF PAST <HOUR>
  X:35  → IT IS TWENTY FIVE TO <HOUR+1>
  X:40  → IT IS TWENTY TO <HOUR+1>
  X:45  → IT IS A QUARTER TO <HOUR+1>
  X:50  → IT IS TEN TO <HOUR+1>
  X:55  → IT IS FIVE TO <HOUR+1>
"""

from __future__ import annotations

import wordclock.layouts.base as base
from wordclock.layouts.base import LedResult
from wordclock.layouts.utils import load_grid

GRID_RAW: list[str] = load_grid("english")

NUM_ROWS: int = len(GRID_RAW)
NUM_COLS: int = len(GRID_RAW[0])

HOUR_WORDS: list[str] = [
    "TWELVE",
    "ONE",
    "TWO",
    "THREE",
    "FOUR",
    "FIVE",
    "SIX",
    "SEVEN",
    "EIGHT",
    "NINE",
    "TEN",
    "ELEVEN",
]

MINUTE_WORDS: list[str] = [
    "OCLOCK",
    "FIVE PAST",
    "TEN PAST",
    "A QUARTER PAST",
    "TWENTY PAST",
    "TWENTY FIVE PAST",
    "HALF PAST",
    "TWENTY FIVE TO",
    "TWENTY TO",
    "A QUARTER TO",
    "TEN TO",
    "FIVE TO",
]

_NEXT_HOUR: frozenset[int] = frozenset(range(7, 12))  # :35 → :55


def time_to_sentence(hours: int, minutes: int) -> str:
    """
    Convert hours (0-23) and minutes (0-59) to an English word clock sentence.

    Args:
        hours: Hour value 0-23.
        minutes: Minute value 0-59.

    Returns:
        Sentence in ALL CAPS, e.g. ``"IT IS A QUARTER PAST TEN"``.
    """
    minute_index = minutes // 5
    h = hours % 12
    if minute_index in _NEXT_HOUR:
        h = (h + 1) % 12

    hour_word = HOUR_WORDS[h]
    minute_phrase = MINUTE_WORDS[minute_index]

    if minute_index == 0:
        return f"IT IS {hour_word} {minute_phrase}"
    return f"IT IS {minute_phrase} {hour_word}"


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
        (12, 0),
        (1, 0),
        (3, 5),
        (6, 10),
        (10, 15),
        (8, 20),
        (4, 25),
        (7, 30),
        (11, 35),
        (2, 40),
        (9, 45),
        (5, 50),
        (3, 55),
    ]
    print("=" * 55)
    print("  English word clock — layout test")
    print("=" * 55)
    print(f"\n{'TIME':<8} | {'SENTENCE'}")
    print("-" * 40)
    for h, m in cases:
        res = get_leds_for_time(h, m)
        print(f"{h:02d}:{m:02d}    | {res['sentence']}")
