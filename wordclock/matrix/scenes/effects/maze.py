from __future__ import annotations

from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.scenes.effects.grid import Cell, neighbours

WALL: Color = (0, 25, 70)
DEAD_END: Color = (70, 25, 0)
PATH: Color = (0, 110, 150)
TOKEN: Color = (255, 255, 255)
GATE: Color = (0, 160, 40)
FLASH_SECONDS = 1.5


def carve_maze(width: int, height: int, random: Random) -> set[Cell]:
    """
    Carve a maze with one way between any two rooms.

    Rooms sit on the even cells and the cells between them are walls; a
    randomised depth-first search knocks down the walls it walks through.

    Args:
        width: Canvas width.
        height: Canvas height.
        random: Source of the random choices.

    Returns:
        The open cells: every room and the knocked-down walls.
    """
    rooms = {(x, y) for x in range(0, width, 2) for y in range(0, height, 2)}
    open_cells = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        x, y = stack[-1]
        options = [
            (x + dx, y + dy)
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
            if (x + dx, y + dy) in rooms and (x + dx, y + dy) not in open_cells
        ]
        if not options:
            stack.pop()
            continue
        nx, ny = random.choice(options)
        open_cells.add(((x + nx) // 2, (y + ny) // 2))
        open_cells.add((nx, ny))
        stack.append((nx, ny))
    return open_cells


class MazeScene:
    """
    A new maze, with a token in the top-left corner that tries to escape
    through the green gate on the right side. It explores like a person
    would, depth first: it walks on until a dead end and then goes back to
    the last fork. When it gets out, the way lights up, ``done`` turns
    True and a new maze starts.
    """

    def __init__(self, fps: float = 8, seed: int | None = None) -> None:
        self.fps = fps
        self._random = Random(seed)
        self._size = (0, 0)
        self.open: set[Cell] = set()
        self.gate: Cell = (0, 0)
        self.path: list[Cell] = []
        self._visited: set[Cell] = set()
        self._escaped_at: int | None = None
        self.escapes = 0
        self.done = False

    def _new_maze(self, width: int, height: int) -> None:
        self.open = carve_maze(width, height, self._random)
        last_x = max(x for x, _ in self.open)
        rows = sorted({y for x, y in self.open if x == last_x and y % 2 == 0})
        self.gate = (last_x + 1, self._random.choice(rows))
        self.open.add(self.gate)
        self.path = [(0, 0)]
        self._visited = {(0, 0)}
        self._escaped_at = None

    def _walk(self, width: int, height: int) -> None:
        here = self.path[-1]
        # The gate may sit just outside the canvas on odd widths.
        options = [
            cell
            for cell in neighbours(here, width + 1, height)
            if cell in self.open and cell not in self._visited
        ]
        if options:
            # Head for the gate side a little more often than not.
            options.sort(key=lambda cell: (-cell[0], self._random.random()))
            step = options[0] if self._random.random() < 0.6 else self._random.choice(options)
            self.path.append(step)
            self._visited.add(step)
        elif len(self.path) > 1:
            self.path.pop()

    def render(self, canvas: Canvas, frame: int) -> None:
        width, height = canvas.width, canvas.height
        if self._size != (width, height):
            self._size = (width, height)
            self._new_maze(width, height)
        if self._escaped_at is None:
            if frame > 0:
                self._walk(width, height)
            if self.path[-1] == self.gate:
                self._escaped_at = frame
                self.escapes += 1
        elif frame - self._escaped_at >= FLASH_SECONDS * self.fps:
            self.done = True
            self._new_maze(width, height)
        on_path = set(self.path)
        flashing = self._escaped_at is not None and (frame // 2) % 2 == 0
        for y in range(height):
            for x in range(width):
                cell = (x, y)
                color: Color = (0, 0, 0)
                if cell not in self.open:
                    color = WALL
                elif cell in on_path:
                    color = GATE if flashing else PATH
                elif cell in self._visited:
                    color = DEAD_END
                elif cell == self.gate:
                    color = GATE
                canvas.set(x, y, color)
        if self._escaped_at is None:
            x, y = self.path[-1]
            canvas.set(x, y, TOKEN)
