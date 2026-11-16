from __future__ import annotations

from collections.abc import Callable

import pytest

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.scenes.base import Scene
from wordclock.matrix.scenes.effects.bounce import BounceScene
from wordclock.matrix.scenes.effects.fire import PALETTE, FireScene, heat_color
from wordclock.matrix.scenes.effects.grid import neighbours, room, shortest_path
from wordclock.matrix.scenes.effects.layers import LayersScene, layer_order
from wordclock.matrix.scenes.effects.maze import WALL, MazeScene, carve_maze
from wordclock.matrix.scenes.effects.rainbow import SpinScene
from wordclock.matrix.scenes.effects.snake import SnakeScene
from wordclock.matrix.scenes.effects.stack import (
    PIECES,
    StackScene,
    drop_row,
    fits,
    rotations,
)
from wordclock.matrix.scenes.effects.worms import WormsScene

NEW_EFFECTS: dict[str, Callable[[], Scene]] = {
    "fire": lambda: FireScene(seed=1),
    "spin": lambda: SpinScene(),
    "layers": lambda: LayersScene(seed=1),
    "bounce": lambda: BounceScene(seed=1),
    "worms": lambda: WormsScene(seed=1),
    "snake": lambda: SnakeScene(seed=1),
    "maze": lambda: MazeScene(seed=1),
    "stack": lambda: StackScene(seed=1),
}


def lit(canvas: Canvas) -> int:
    return sum(1 for row in canvas.rows() for color in row if any(color))


def valid(canvas: Canvas) -> bool:
    return all(0 <= c <= 255 for row in canvas.rows() for color in row for c in color)


class TestEveryNewEffect:
    @pytest.mark.parametrize("name", NEW_EFFECTS)
    @pytest.mark.parametrize("size", [(10, 6), (16, 16), (7, 5)])
    def test_runs_and_lights_cells(self, name: str, size: tuple[int, int]) -> None:
        # Given
        scene = NEW_EFFECTS[name]()
        canvas = Canvas(*size)
        most = 0
        # When
        for frame in range(1500):
            scene.render(canvas, frame)
            most = max(most, lit(canvas))
            assert valid(canvas)
        # Then
        assert most > 0


class TestGrid:
    def test_neighbours_stay_inside(self) -> None:
        # Given / When / Then
        assert sorted(neighbours((0, 0), 10, 6)) == [(0, 1), (1, 0)]

    def test_shortest_path_goes_round_walls(self) -> None:
        # Given: a wall in column 1 with a gap at the bottom
        wall = {(1, 0), (1, 1)}
        # When
        path = shortest_path((0, 0), (2, 0), lambda cell: cell not in wall, 3, 3)
        # Then
        assert path == [(0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0)]

    def test_no_path(self) -> None:
        # Given
        wall = {(1, 0), (1, 1), (1, 2)}
        # When / Then
        assert shortest_path((0, 0), (2, 0), lambda cell: cell not in wall, 3, 3) is None

    def test_room_counts_the_open_area(self) -> None:
        # Given
        wall = {(1, 0), (1, 1), (1, 2)}
        # When / Then
        assert room((0, 0), lambda cell: cell not in wall, 3, 3) == 3


class TestFire:
    def test_bottom_row_burns(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = FireScene(seed=2)
        # When
        for frame in range(30):
            scene.render(canvas, frame)
        # Then
        assert all(any(color) for color in canvas.rows()[-1])

    def test_hotter_is_brighter(self) -> None:
        # Given / When / Then
        assert heat_color(0) == PALETTE[0]
        assert heat_color(1) == PALETTE[-1]
        assert sum(heat_color(0.8)) > sum(heat_color(0.3))


class TestSpin:
    def test_stripes_turn(self) -> None:
        # Given: rows at the start, columns a quarter turn later
        scene = SpinScene(fps=20, turn_seconds=4, speed=0)
        canvas = Canvas(10, 6)
        # When
        scene.render(canvas, 0)
        start = canvas.rows()
        scene.render(canvas, 20)
        later = canvas.rows()
        # Then: first the colour changes along a row, then down a column
        assert len(set(start[0])) > 1 and start[0][0] == start[5][0]
        assert len({row[0] for row in later}) > 1 and later[0][0] == later[0][9]


class TestLayers:
    def test_centre_square_first(self) -> None:
        # Given / When
        order = layer_order(10, 6)
        # Then
        assert {(x, y) for x, y, _ in order[:4]} == {(4, 2), (5, 2), (4, 3), (5, 3)}
        assert [ring for _, _, ring in order] == sorted(ring for _, _, ring in order)
        assert len(order) == 60

    def test_fills_the_matrix_then_is_done(self) -> None:
        # Given
        scene = LayersScene(fps=12, seed=1)
        canvas = Canvas(10, 6)
        full = False
        # When
        frame = 0
        while not scene.done and frame < 1000:
            scene.render(canvas, frame)
            full = full or lit(canvas) == 60
            frame += 1
        # Then
        assert full and scene.done


class TestBounce:
    def test_stays_inside_and_moves(self) -> None:
        # Given
        scene = BounceScene(seed=4)
        canvas = Canvas(10, 6)
        places = set()
        # When
        for frame in range(600):
            scene.render(canvas, frame)
            assert 0 <= scene.x <= 9 and 0 <= scene.y <= 5
            places.add((round(scene.x), round(scene.y)))
        # Then: it visits most of the matrix, top rows included
        assert len(places) > 30
        assert min(y for _, y in places) <= 1


class TestWorms:
    def test_one_worm_per_corner(self) -> None:
        # Given
        scene = WormsScene(seed=1)
        canvas = Canvas(10, 6)
        # When
        scene.render(canvas, 0)
        # Then: each corner belongs to its own worm
        corners = [(0, 0), (9, 0), (9, 5), (0, 5)]
        assert sorted(scene._owner[corner] for corner in corners) == [0, 1, 2, 3]
        assert len({round(worm.hue % 1, 3) for worm in scene._worms}) == 4

    @pytest.mark.parametrize("seed", range(10))
    def test_fill_the_matrix_and_are_done(self, seed: int) -> None:
        # Given
        scene = WormsScene(fps=10, seed=seed)
        canvas = Canvas(10, 6)
        # When
        frame = 0
        while not scene.done and frame < 500:
            scene.render(canvas, frame)
            frame += 1
        # Then
        assert scene.done


class TestSnake:
    @pytest.mark.parametrize("seed", range(5))
    def test_never_crosses_itself_and_eats(self, seed: int) -> None:
        # Given
        scene = SnakeScene(seed=seed)
        canvas = Canvas(10, 6)
        longest = 0
        # When
        for frame in range(800):
            scene.render(canvas, frame)
            assert len(set(scene.body)) == len(scene.body)
            assert scene.food not in scene.body
            longest = max(longest, len(scene.body))
        # Then
        assert longest > 8

    def test_changes_colour_when_it_eats(self) -> None:
        # Given
        scene = SnakeScene(seed=1)
        canvas = Canvas(10, 6)
        scene.render(canvas, 0)
        hue = scene.hue
        # When
        frame = 1
        while scene.meals == 0:
            scene.render(canvas, frame)
            frame += 1
        # Then
        assert scene.hue != hue
        assert len(scene.body) == 3


class TestMaze:
    @pytest.mark.parametrize("size", [(10, 6), (16, 16), (7, 5)])
    def test_every_room_is_reachable(self, size: tuple[int, int]) -> None:
        # Given
        from random import Random

        width, height = size
        # When
        open_cells = carve_maze(width, height, Random(1))
        # Then
        rooms = {(x, y) for x in range(0, width, 2) for y in range(0, height, 2)}
        assert rooms <= open_cells
        assert room((0, 0), lambda cell: cell in open_cells, width, height) == len(open_cells)

    @pytest.mark.parametrize("seed", range(50))
    def test_token_escapes(self, seed: int) -> None:
        # Given
        scene = MazeScene(seed=seed)
        canvas = Canvas(10, 6)
        # When
        frame = 0
        while not scene.done and frame < 1000:
            scene.render(canvas, frame)
            frame += 1
        # Then
        assert scene.done and scene.escapes == 1

    def test_walls_are_drawn(self) -> None:
        # Given
        scene = MazeScene(seed=1)
        canvas = Canvas(10, 6)
        # When
        scene.render(canvas, 0)
        # Then
        assert any(color == WALL for row in canvas.rows() for color in row)


class TestStack:
    def test_rotations(self) -> None:
        # Given / When / Then
        assert len(rotations(PIECES["O"])) == 1
        assert len(rotations(PIECES["I"])) == 2
        assert len(rotations(PIECES["T"])) == 4

    def test_pieces_land_on_the_floor(self) -> None:
        # Given
        board = [[None] * 10 for _ in range(6)]
        # When
        top = drop_row(board, PIECES["O"], 0)
        # Then
        assert top == 4
        assert fits(board, PIECES["O"], 0, top)
        assert not fits(board, PIECES["O"], 0, top + 1)

    def test_clears_full_rows(self) -> None:
        # Given
        scene = StackScene(seed=1)
        canvas = Canvas(10, 6)
        # When
        for frame in range(3000):
            scene.render(canvas, frame)
        # Then
        assert scene.lines > 0

    def test_piece_never_overlaps_the_pile(self) -> None:
        # Given
        scene = StackScene(seed=3)
        canvas = Canvas(10, 6)
        # When / Then
        for frame in range(2000):
            scene.render(canvas, frame)
            piece = scene.piece
            if piece is not None:
                assert fits(scene.board, piece.shape, piece.left, piece.top)
