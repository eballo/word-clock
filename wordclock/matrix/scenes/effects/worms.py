from __future__ import annotations

from dataclasses import dataclass
from random import Random

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import add, hue_color, scale
from wordclock.matrix.scenes.effects.grid import Cell, neighbours

HOLD_SECONDS = 2.0
# Steps after which a trail cell reaches its dimmest.
TRAIL_STEPS = 18


@dataclass
class Worm:
    head: Cell
    hue: float


class WormsScene:
    """
    One worm starts in each corner, each in its own colour. Every step it
    crawls to a random free cell next to its head and leaves its body
    behind, so the worms grow until the matrix is full. A worm boxed in
    starts again from a free cell next to its body. When the matrix is
    full it holds for a moment, ``done`` turns True and it starts again.
    """

    def __init__(self, fps: float = 10, seed: int | None = None) -> None:
        self.fps = fps
        self._random = Random(seed)
        self._owner: dict[Cell, int] = {}
        self._visited: dict[Cell, int] = {}
        self._worms: list[Worm] = []
        self._size = (0, 0)
        self._full_since: int | None = None
        self._step = 0
        self.done = False

    def _start(self, width: int, height: int) -> None:
        corners = [(0, 0), (width - 1, 0), (width - 1, height - 1), (0, height - 1)]
        offset = self._random.random()
        self._worms = [Worm(corner, offset + i / 4) for i, corner in enumerate(corners)]
        self._owner = {worm.head: i for i, worm in enumerate(self._worms)}
        self._visited = {worm.head: 0 for worm in self._worms}
        self._full_since = None
        self._step = 0

    def _free(self, cell: Cell) -> bool:
        return cell not in self._owner

    def _move(self, index: int, worm: Worm, width: int, height: int) -> None:
        options = [cell for cell in neighbours(worm.head, width, height) if self._free(cell)]
        if not options:
            # Boxed in: carry on from any free cell next to its own body.
            body = [cell for cell, owner in self._owner.items() if owner == index]
            self._random.shuffle(body)
            options = next(
                (
                    [nxt for nxt in neighbours(cell, width, height) if self._free(nxt)]
                    for cell in body
                    if any(self._free(nxt) for nxt in neighbours(cell, width, height))
                ),
                [],
            )
        if options:
            worm.head = self._random.choice(options)
            self._owner[worm.head] = index
            self._visited[worm.head] = self._step

    def render(self, canvas: Canvas, frame: int) -> None:
        width, height = canvas.width, canvas.height
        if self._size != (width, height):
            self._size = (width, height)
            self._start(width, height)
        self._step += 1
        if len(self._owner) < width * height:
            for index, worm in enumerate(self._worms):
                self._move(index, worm, width, height)
        elif self._full_since is None:
            self._full_since = self._step
        elif self._step - self._full_since >= HOLD_SECONDS * self.fps:
            self.done = True
            self._start(width, height)
        canvas.clear()
        heads = {worm.head for worm in self._worms}
        for cell, owner in self._owner.items():
            color = hue_color(self._worms[owner].hue)
            age = self._step - self._visited[cell]
            level = max(0.3, 1 - age / TRAIL_STEPS)
            shade = add(color, (80, 80, 80)) if cell in heads else scale(color, level)
            canvas.set(cell[0], cell[1], shade)
