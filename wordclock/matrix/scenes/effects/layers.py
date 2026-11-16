from __future__ import annotations

from math import atan2, floor
from random import Random

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import hue_color, scale

HOLD_SECONDS = 1.0


def layer_order(width: int, height: int) -> list[tuple[int, int, int]]:
    """
    Order the cells from the centre outwards, ring by ring.

    The centre square is ring 0; each ring around it is one cell further
    away (the largest of the horizontal and vertical distances). Inside a
    ring, the cells go round like a clock hand.

    Args:
        width: Canvas width.
        height: Canvas height.

    Returns:
        ``(x, y, ring)`` for every cell, centre first.
    """
    cx, cy = (width - 1) / 2, (height - 1) / 2
    cells = []
    for y in range(height):
        for x in range(width):
            ring = floor(max(abs(x - cx), abs(y - cy)))
            angle = atan2(y - cy, x - cx)
            cells.append((ring, angle, x, y))
    cells.sort()
    return [(x, y, ring) for ring, _, x, y in cells]


class LayersScene:
    """
    The centre square fills cell by cell, then every ring around it, each
    in a new colour, until the matrix is full; then it empties from the
    outside in. ``done`` turns True after the first full cycle.
    """

    def __init__(self, fps: float = 12, seed: int | None = None) -> None:
        self.fps = fps
        self._random = Random(seed)
        self._hue = self._random.random()
        self._order: list[tuple[int, int, int]] = []
        self._size = (0, 0)
        self.done = False

    def render(self, canvas: Canvas, frame: int) -> None:
        if self._size != (canvas.width, canvas.height):
            self._size = (canvas.width, canvas.height)
            self._order = layer_order(canvas.width, canvas.height)
        cells = len(self._order)
        hold = int(HOLD_SECONDS * self.fps)
        cycle = 2 * (cells + hold)
        step = frame % cycle
        if step == cycle - 1:
            self.done = True
            self._hue = self._random.random()
        if step < cells:
            lit = step + 1
        elif step < cells + hold:
            lit = cells
        elif step < 2 * cells + hold:
            lit = cells - (step - cells - hold) - 1
        else:
            lit = 0
        canvas.clear()
        for i, (x, y, ring) in enumerate(self._order[:lit]):
            color = hue_color(self._hue + ring * 0.13)
            # The newest cell of the growing ring is a little brighter.
            canvas.set(x, y, color if i == lit - 1 else scale(color, 0.75))
