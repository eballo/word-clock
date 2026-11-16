from __future__ import annotations

from collections import deque
from math import sin
from random import Random

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import GREEN, add, hue_color, scale
from wordclock.matrix.scenes.effects.grid import Cell, neighbours, room, shortest_path

START_LENGTH = 2
# Hue step after eating, so the next colour is clearly different.
HUE_STEP = 0.27


class SnakeScene:
    """
    A worm that hunts a green dot: it takes the shortest way that does not
    cross its body, and when it eats the dot it grows by one cell, changes
    colour and a new dot appears. Without a way it moves to the side with
    the most room; boxed in or with the matrix full, it starts again.
    """

    def __init__(self, fps: float = 8, seed: int | None = None) -> None:
        self.fps = fps
        self._random = Random(seed)
        self.body: deque[Cell] = deque()
        self.food: Cell | None = None
        self.hue = 0.0
        self._size = (0, 0)
        self.meals = 0

    def _start(self, width: int, height: int) -> None:
        y = height // 2
        self.body = deque((max(0, START_LENGTH - 1 - i), y) for i in range(START_LENGTH))
        self.hue = self._random.random()
        self.meals = 0
        self._place_food(width, height)

    def _place_food(self, width: int, height: int) -> None:
        taken = set(self.body)
        free = [(x, y) for y in range(height) for x in range(width) if (x, y) not in taken]
        self.food = self._random.choice(free) if free else None

    def _next_cell(self, width: int, height: int) -> Cell | None:
        # The tail moves away this step, so its cell is free.
        blocked = set(list(self.body)[:-1])

        def free(cell: Cell) -> bool:
            return cell not in blocked

        head = self.body[0]
        if self.food is not None:
            path = shortest_path(head, self.food, free, width, height)
            if path:
                return path[0]
        options = [cell for cell in neighbours(head, width, height) if free(cell)]
        if not options:
            return None
        return max(options, key=lambda cell: room(cell, free, width, height))

    def _step(self, width: int, height: int) -> None:
        nxt = self._next_cell(width, height)
        if nxt is None:
            self._start(width, height)
            return
        self.body.appendleft(nxt)
        if nxt == self.food:
            self.meals += 1
            self.hue += HUE_STEP
            self._place_food(width, height)
            if self.food is None:
                self._start(width, height)
        else:
            self.body.pop()

    def render(self, canvas: Canvas, frame: int) -> None:
        width, height = canvas.width, canvas.height
        if self._size != (width, height):
            self._size = (width, height)
            self._start(width, height)
        elif frame > 0:
            self._step(width, height)
        canvas.clear()
        if self.food is not None:
            pulse = 0.6 + 0.4 * abs(sin(frame / self.fps * 3))
            canvas.set(self.food[0], self.food[1], scale(GREEN, pulse))
        color = hue_color(self.hue)
        length = len(self.body)
        for i, (x, y) in enumerate(self.body):
            if i == 0:
                canvas.set(x, y, add(color, (90, 90, 90)))
            else:
                canvas.set(x, y, scale(color, 1 - 0.6 * i / max(1, length)))
