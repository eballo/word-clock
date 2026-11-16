from __future__ import annotations

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import hue_color


class RainbowScene:
    """A rainbow that slides diagonally across the matrix."""

    def __init__(self, fps: float = 20, speed: float = 0.01) -> None:
        self.fps = fps
        self.speed = speed

    def render(self, canvas: Canvas, frame: int) -> None:
        span = canvas.width + canvas.height
        for y in range(canvas.height):
            for x in range(canvas.width):
                canvas.set(x, y, hue_color((x + y) / span + frame * self.speed))
