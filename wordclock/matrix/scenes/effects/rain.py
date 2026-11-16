from __future__ import annotations

from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import GREEN, WHITE


class RainScene:
    """Green drops that fall down the matrix and fade, like Matrix rain."""

    def __init__(
        self, color: Color = GREEN, fps: float = 12, density: float = 0.3, seed: int | None = None
    ) -> None:
        self.fps = fps
        self.color = color
        self.density = density
        self._random = Random(seed)
        self._drops: list[list[float]] = []

    def render(self, canvas: Canvas, frame: int) -> None:
        # Fade the previous frame to leave a trail behind every drop.
        for y in range(canvas.height):
            for x in range(canvas.width):
                r, g, b = canvas.get(x, y)
                canvas.set(x, y, (r * 6 // 10, g * 6 // 10, b * 6 // 10))
        if self._random.random() < self.density:
            speed = self._random.choice((0.5, 1.0))
            self._drops.append([float(self._random.randrange(canvas.width)), 0.0, speed])
        for drop in self._drops:
            x, y, speed = drop
            canvas.set(int(x), int(y), WHITE if speed == 1.0 else self.color)
            drop[1] += speed
        self._drops = [drop for drop in self._drops if drop[1] < canvas.height]
