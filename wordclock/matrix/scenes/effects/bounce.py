from __future__ import annotations

from math import sqrt
from random import Random

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import add, hue_color, scale

# Cells per second squared.
GRAVITY = 30.0
# Share of the speed kept after hitting the floor.
BOUNCE = 0.85


class BounceScene:
    """
    A light that jumps around the matrix: it falls, bounces off the floor
    and the walls, and gets a new kick when it runs out of energy. It
    leaves a fading trail and slowly goes round the colour wheel.
    """

    def __init__(self, fps: float = 30, seed: int | None = None) -> None:
        self.fps = fps
        self._random = Random(seed)
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self._size = (0, 0)

    def _kick(self, height: int) -> None:
        # Enough speed to reach somewhere between the middle and the top.
        top = sqrt(2 * GRAVITY * max(1, height - 1))
        self.vy = -top * (0.7 + 0.3 * self._random.random())
        self.vx = self._random.choice((-1, 1)) * (4 + 6 * self._random.random())

    def _step(self, width: int, height: int) -> None:
        dt = 1 / self.fps
        self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < 0:
            self.x, self.vx = -self.x, abs(self.vx)
        elif self.x > width - 1:
            self.x, self.vx = 2 * (width - 1) - self.x, -abs(self.vx)
        if self.y < 0:
            self.y, self.vy = 0.0, abs(self.vy)
        if self.y > height - 1:
            self.y = float(height - 1)
            self.vy = -abs(self.vy) * BOUNCE
            self.vx *= 0.95
            if abs(self.vy) < 3:
                self._kick(height)

    def render(self, canvas: Canvas, frame: int) -> None:
        if self._size != (canvas.width, canvas.height):
            self._size = (canvas.width, canvas.height)
            self.x = self._random.uniform(0, canvas.width - 1)
            self.y = float(canvas.height - 1)
            self._kick(canvas.height)
        self._step(canvas.width, canvas.height)
        canvas.fade(0.7)
        color = hue_color(frame / self.fps / 8)
        x, y = round(self.x), round(self.y)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            glow = add(canvas.get(x + dx, y + dy), scale(color, 0.25))
            canvas.set(x + dx, y + dy, glow)
        canvas.set(x, y, add(color, (90, 90, 90)))
