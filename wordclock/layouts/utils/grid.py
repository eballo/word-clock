"""Pure grid-manipulation utilities."""

from __future__ import annotations

from random import Random
from string import ascii_uppercase


def create_layout(grid_raw: list[str], seed: int | None = None) -> list[str]:
    """
    Replace lowercase 'x' filler characters with random uppercase letters.

    Args:
        grid_raw: Raw grid rows where lowercase 'x' marks filler positions.
        seed: Optional seed for deterministic output (useful in tests).

    Returns:
        A new list of rows with every 'x' replaced by a random uppercase letter.
    """
    rng = Random(seed)
    rows: list[str] = []
    for row in grid_raw:
        chars = list(row)
        for i, ch in enumerate(chars):
            if ch == "x":
                chars[i] = rng.choice(ascii_uppercase)
        rows.append("".join(chars))
    return rows
