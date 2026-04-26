from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypedDict


class LedResult(TypedDict):
    """Return type of every layout's ``get_leds_for_time``."""

    sentence: str
    coords: list[tuple[int, int]]
    led_indices: list[int]
    hours: int
    minutes: int


class LayoutModule(Protocol):
    """Structural interface every layout module must satisfy."""

    GRID_RAW: list[str]
    NUM_ROWS: int
    NUM_COLS: int
    HOUR_WORDS: list[str]
    time_to_sentence: Callable[[int, int], str]
    get_leds_for_time: Callable[..., LedResult]


def sentence_to_coords(
    sentence: str,
    grid: list[str],
    num_rows: int,
    normalize: dict[str, str] | None = None,
) -> list[tuple[int, int]]:
    """
    Find each word of *sentence* in *grid* (left-to-right, top-to-bottom)
    and return the ``(row, col)`` coordinates of every lit letter.

    Args:
        sentence: ALL-CAPS sentence to locate.
        grid: Display grid to search.
        num_rows: Number of rows in the grid.
        normalize: Optional substitutions applied to *sentence* before splitting
                   (e.g. ``{"D'": "D' "}`` for Catalan).

    Returns:
        List of ``(row, col)`` pairs for every lit letter.
    """
    if normalize:
        for old, new in normalize.items():
            sentence = sentence.replace(old, new)

    words = sentence.split()
    coords: list[tuple[int, int]] = []
    current_row = 0
    current_col = 0

    for word in words:
        found = False
        for r in range(current_row, num_rows):
            start_c = current_col if r == current_row else 0
            idx = grid[r].find(word, start_c)
            if idx != -1:
                for i in range(len(word)):
                    coords.append((r, idx + i))
                current_row = r
                current_col = idx + len(word)
                found = True
                break

        if not found:
            for r in range(num_rows):
                idx = grid[r].find(word)
                if idx != -1:
                    for i in range(len(word)):
                        coords.append((r, idx + i))
                    current_row = r
                    current_col = idx + len(word)
                    break

    return coords


def build_leds_for_time(
    hours: int,
    minutes: int,
    *,
    grid: list[str],
    num_rows: int,
    num_cols: int,
    time_to_sentence_fn: Callable[[int, int], str],
    normalize: dict[str, str] | None = None,
    snake: bool = True,
) -> LedResult:
    """
    Build a :class:`LedResult` for a given time using the provided layout parameters.

    Args:
        hours: Hour value 0-23.
        minutes: Minute value 0-59.
        grid: Display grid to search.
        num_rows: Number of rows in the grid.
        num_cols: Number of columns in the grid.
        time_to_sentence_fn: Language-specific sentence builder.
        normalize: Optional substitutions passed to :func:`sentence_to_coords`.
        snake: Apply snake wiring. Default ``True``.

    Returns:
        :class:`LedResult` dict.
    """
    s = time_to_sentence_fn(hours, minutes)
    coords = sentence_to_coords(s, grid, num_rows, normalize=normalize)
    led_indices = coords_to_led_indices(coords, num_cols, snake=snake)
    return LedResult(
        sentence=s, coords=coords, led_indices=led_indices, hours=hours, minutes=minutes
    )


def coords_to_led_indices(
    coords: list[tuple[int, int]],
    num_cols: int,
    snake: bool = True,
) -> list[int]:
    """
    Convert ``(row, col)`` pairs to absolute LED indices.

    Args:
        coords: List of ``(row, col)`` pairs.
        num_cols: Number of columns in the grid (used for snake offset).
        snake: Apply snake wiring (odd rows reversed). Default ``True``.

    Returns:
        List of integer LED indices.
    """
    indices: list[int] = []
    for row, col in coords:
        if snake and row % 2 == 1:
            idx = row * num_cols + (num_cols - 1 - col)
        else:
            idx = row * num_cols + col
        indices.append(idx)
    return indices
