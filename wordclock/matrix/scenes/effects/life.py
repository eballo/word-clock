from __future__ import annotations

from random import Random

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import hue_color


class LifeScene:
    """
    Conway's Game of Life on a matrix that wraps around at the edges.

    New cells are bright and turn bluer as they age. When life dies out,
    freezes or loops, it starts again from a new random pattern.
    """

    def __init__(
        self,
        fps: float = 5,
        density: float = 0.35,
        max_generations: int = 300,
        seed: int | None = None,
    ) -> None:
        self.fps = fps
        self.density = density
        self.max_generations = max_generations
        self._random = Random(seed)
        self._ages: list[list[int]] = []
        self._seen: list[tuple[tuple[bool, ...], ...]] = []
        self.generation = 0

    def _seed(self, width: int, height: int) -> None:
        self._ages = [
            [1 if self._random.random() < self.density else 0 for _ in range(width)]
            for _ in range(height)
        ]
        self._seen = []
        self.generation = 0

    def _step(self) -> None:
        height, width = len(self._ages), len(self._ages[0])
        new = [[0] * width for _ in range(height)]
        for y in range(height):
            for x in range(width):
                neighbours = sum(
                    1
                    for dy in (-1, 0, 1)
                    for dx in (-1, 0, 1)
                    if (dx or dy) and self._ages[(y + dy) % height][(x + dx) % width]
                )
                alive = self._ages[y][x] > 0
                if neighbours == 3 or (alive and neighbours == 2):
                    new[y][x] = self._ages[y][x] + 1
        self._ages = new
        self.generation += 1

    def _alive(self) -> tuple[tuple[bool, ...], ...]:
        return tuple(tuple(age > 0 for age in row) for row in self._ages)

    def render(self, canvas: Canvas, frame: int) -> None:
        if not self._ages or len(self._ages) != canvas.height:
            self._seed(canvas.width, canvas.height)
        elif frame > 0:
            self._step()
            state = self._alive()
            if (
                not any(any(row) for row in state)
                or state in self._seen
                or self.generation >= self.max_generations
            ):
                self._seed(canvas.width, canvas.height)
            else:
                self._seen = [*self._seen[-5:], state]
        canvas.clear()
        for y, row in enumerate(self._ages):
            for x, age in enumerate(row):
                if age:
                    canvas.set(x, y, hue_color(0.45 + min(age, 12) * 0.025))
