from __future__ import annotations

from random import Random

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import hue_color


class SparkleScene:
    """Cells that light up in random colours and fade out, like fireflies."""

    def __init__(self, fps: float = 15, per_frame: int = 2, seed: int | None = None) -> None:
        self.fps = fps
        self.per_frame = per_frame
        self._random = Random(seed)

    def render(self, canvas: Canvas, frame: int) -> None:
        for y in range(canvas.height):
            for x in range(canvas.width):
                r, g, b = canvas.get(x, y)
                canvas.set(x, y, (r * 8 // 10, g * 8 // 10, b * 8 // 10))
        for _ in range(self.per_frame):
            x = self._random.randrange(canvas.width)
            y = self._random.randrange(canvas.height)
            canvas.set(x, y, hue_color(self._random.random()))
