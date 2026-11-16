from __future__ import annotations

from math import cos, sin, tau

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


class SpinScene:
    """
    A rainbow whose stripes turn: across the rows, then the columns, the
    diagonals and back, while the colours keep sliding.
    """

    def __init__(self, fps: float = 20, turn_seconds: float = 12.0, speed: float = 0.01) -> None:
        self.fps = fps
        self.turn_seconds = turn_seconds
        self.speed = speed

    def render(self, canvas: Canvas, frame: int) -> None:
        angle = tau * frame / self.fps / self.turn_seconds
        dx, dy = cos(angle), sin(angle)
        cx, cy = (canvas.width - 1) / 2, (canvas.height - 1) / 2
        span = max(canvas.width, canvas.height)
        for y in range(canvas.height):
            for x in range(canvas.width):
                along = ((x - cx) * dx + (y - cy) * dy) / span
                canvas.set(x, y, hue_color(along + frame * self.speed))
