from __future__ import annotations

from dataclasses import dataclass
from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import scale
from wordclock.matrix.scenes.effects.grid import Cell

# The seven four-cell pieces, as cells of their first rotation.
PIECES: dict[str, tuple[Cell, ...]] = {
    "I": ((0, 0), (1, 0), (2, 0), (3, 0)),
    "O": ((0, 0), (1, 0), (0, 1), (1, 1)),
    "T": ((0, 0), (1, 0), (2, 0), (1, 1)),
    "S": ((1, 0), (2, 0), (0, 1), (1, 1)),
    "Z": ((0, 0), (1, 0), (1, 1), (2, 1)),
    "J": ((0, 0), (0, 1), (1, 1), (2, 1)),
    "L": ((2, 0), (0, 1), (1, 1), (2, 1)),
}
COLORS: dict[str, Color] = {
    "I": (0, 200, 255),
    "O": (255, 210, 0),
    "T": (170, 40, 255),
    "S": (40, 230, 60),
    "Z": (255, 40, 40),
    "J": (40, 80, 255),
    "L": (255, 130, 0),
}
FLASH_FRAMES = 4

Board = list[list[Color | None]]


def normalise(cells: tuple[Cell, ...]) -> tuple[Cell, ...]:
    """
    Move a piece so its top-left corner is at ``(0, 0)``.

    Args:
        cells: The piece cells.

    Returns:
        The same shape, sorted, touching both axes.
    """
    left = min(x for x, _ in cells)
    top = min(y for _, y in cells)
    return tuple(sorted((x - left, y - top) for x, y in cells))


def rotations(cells: tuple[Cell, ...]) -> list[tuple[Cell, ...]]:
    """
    List the different rotations of a piece.

    Args:
        cells: The piece cells.

    Returns:
        One to four shapes, without repeats.
    """
    found: list[tuple[Cell, ...]] = []
    shape = normalise(cells)
    for _ in range(4):
        if shape not in found:
            found.append(shape)
        shape = normalise(tuple((-y, x) for x, y in shape))
    return found


def fits(board: Board, shape: tuple[Cell, ...], left: int, top: int) -> bool:
    """
    Tell whether a piece fits at a place; cells above the board are allowed.

    Args:
        board: Rows of the board, top first; None for an empty cell.
        shape: The piece cells.
        left: Column of the piece's left edge.
        top: Row of the piece's top edge, negative while entering.

    Returns:
        True if every cell is inside the walls and on an empty cell.
    """
    width, height = len(board[0]), len(board)
    for x, y in shape:
        bx, by = left + x, top + y
        if not 0 <= bx < width or by >= height:
            return False
        if by >= 0 and board[by][bx] is not None:
            return False
    return True


def drop_row(board: Board, shape: tuple[Cell, ...], left: int) -> int:
    """
    Find where a piece lands when it falls straight down.

    Args:
        board: Rows of the board.
        shape: The piece cells.
        left: Column of the piece's left edge.

    Returns:
        The top row where it rests.
    """
    top = -max(y for _, y in shape) - 1
    while fits(board, shape, left, top + 1):
        top += 1
    return top


def score(board: Board, shape: tuple[Cell, ...], left: int, top: int) -> float:
    """
    Rate a landing place: full rows are good, holes and height are bad.

    Args:
        board: Rows of the board.
        shape: The piece cells.
        left: Column of the piece's left edge.
        top: Row where it lands.

    Returns:
        Higher for a better place.
    """
    width, height = len(board[0]), len(board)
    filled = {(x, y) for y in range(height) for x in range(width) if board[y][x] is not None}
    filled |= {(left + x, top + y) for x, y in shape}
    lines = sum(all((x, y) in filled for x in range(width)) for y in range(height))
    heights, holes = [], 0
    for x in range(width):
        column = [y for y in range(height) if (x, y) in filled]
        heights.append(height - column[0] if column else 0)
        if column:
            holes += sum((x, y) not in filled for y in range(column[0], height))
    bumps = sum(abs(a - b) for a, b in zip(heights, heights[1:], strict=False))
    above = sum(1 for _, y in shape if top + y < 0)
    return lines * 8 - holes * 5 - max(heights) * 1.5 - bumps * 0.6 - above * 50


@dataclass
class Piece:
    name: str
    shape: tuple[Cell, ...]
    left: int
    top: int


class StackScene:
    """
    Four-cell pieces fall and pile up. Each piece picks a good landing
    place before it falls; full rows flash and disappear. When the pile
    reaches the top, it empties from the top down and starts again.
    """

    def __init__(self, fps: float = 10, fall_every: int = 2, seed: int | None = None) -> None:
        self.fps = fps
        self.fall_every = fall_every
        self._random = Random(seed)
        self.board: Board = []
        self.piece: Piece | None = None
        self._flash: list[int] = []
        self._flash_left = 0
        self._wipe_row: int | None = None
        self.lines = 0

    def _spawn(self) -> None:
        name = self._random.choice(list(PIECES))
        best: tuple[float, tuple[Cell, ...], int] | None = None
        width = len(self.board[0])
        for shape in rotations(PIECES[name]):
            span = max(x for x, _ in shape) + 1
            for left in range(width - span + 1):
                top = drop_row(self.board, shape, left)
                rating = score(self.board, shape, left, top) + self._random.random() * 0.5
                if best is None or rating > best[0]:
                    best = (rating, shape, left)
        assert best is not None
        _, shape, left = best
        self.piece = Piece(name, shape, left, -max(y for _, y in shape) - 1)

    def _lock(self) -> None:
        piece = self.piece
        assert piece is not None
        self.piece = None
        if any(piece.top + y < 0 for _, y in piece.shape):
            self._wipe_row = 0
            return
        for x, y in piece.shape:
            self.board[piece.top + y][piece.left + x] = COLORS[piece.name]
        self._flash = [y for y, row in enumerate(self.board) if all(row)]
        self._flash_left = FLASH_FRAMES if self._flash else 0

    def _clear_rows(self) -> None:
        width = len(self.board[0])
        kept = [row for y, row in enumerate(self.board) if y not in self._flash]
        self.lines += len(self._flash)
        self.board = [[None] * width for _ in self._flash] + kept
        self._flash = []

    def _update(self, frame: int) -> None:
        if self._wipe_row is not None:
            if self._wipe_row < len(self.board):
                self.board[self._wipe_row] = [None] * len(self.board[0])
                self._wipe_row += 1
            else:
                self._wipe_row = None
            return
        if self._flash_left:
            self._flash_left -= 1
            if not self._flash_left:
                self._clear_rows()
            return
        if self.piece is None:
            self._spawn()
            return
        if frame % self.fall_every:
            return
        piece = self.piece
        if fits(self.board, piece.shape, piece.left, piece.top + 1):
            piece.top += 1
        else:
            self._lock()

    def render(self, canvas: Canvas, frame: int) -> None:
        if len(self.board) != canvas.height or len(self.board[0]) != canvas.width:
            self.board = [[None] * canvas.width for _ in range(canvas.height)]
            self.piece = None
        self._update(frame)
        canvas.clear()
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color is None:
                    continue
                if y in self._flash:
                    color = (255, 255, 255) if self._flash_left % 2 else scale(color, 0.3)
                canvas.set(x, y, scale(color, 0.8))
        if self.piece is not None:
            for x, y in self.piece.shape:
                canvas.set(self.piece.left + x, self.piece.top + y, COLORS[self.piece.name])
