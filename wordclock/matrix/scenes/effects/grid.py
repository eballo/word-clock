from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterator

Cell = tuple[int, int]

# Right, down, left, up.
STEPS: tuple[Cell, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))


def neighbours(cell: Cell, width: int, height: int) -> Iterator[Cell]:
    """
    The cells next to one, inside the canvas, without diagonals.

    Args:
        cell: ``(x, y)``.
        width: Canvas width.
        height: Canvas height.

    Yields:
        Each neighbour ``(x, y)``.
    """
    x, y = cell
    for dx, dy in STEPS:
        if 0 <= x + dx < width and 0 <= y + dy < height:
            yield (x + dx, y + dy)


def shortest_path(
    start: Cell, goal: Cell, free: Callable[[Cell], bool], width: int, height: int
) -> list[Cell] | None:
    """
    Find the shortest way between two cells, by breadth-first search.

    Args:
        start: Where it starts.
        goal: Where it wants to go.
        free: Whether a cell can be stepped on.
        width: Canvas width.
        height: Canvas height.

    Returns:
        The cells after ``start`` up to ``goal``, or None without a way.
    """
    previous: dict[Cell, Cell] = {start: start}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == goal:
            path = []
            while cell != start:
                path.append(cell)
                cell = previous[cell]
            return path[::-1]
        for nxt in neighbours(cell, width, height):
            if nxt not in previous and (nxt == goal or free(nxt)):
                previous[nxt] = cell
                queue.append(nxt)
    return None


def room(start: Cell, free: Callable[[Cell], bool], width: int, height: int) -> int:
    """
    Count the free cells that can be reached from one, itself included.

    Args:
        start: The first cell.
        free: Whether a cell can be stepped on.
        width: Canvas width.
        height: Canvas height.

    Returns:
        The size of the open area around ``start``.
    """
    seen = {start}
    queue = deque([start])
    while queue:
        for nxt in neighbours(queue.popleft(), width, height):
            if nxt not in seen and free(nxt):
                seen.add(nxt)
                queue.append(nxt)
    return len(seen)
