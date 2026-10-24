from __future__ import annotations

import pytest

from wordclock.led.controller import MockLedController
from wordclock.matrix.canvas import Canvas
from wordclock.matrix.runner import MatrixRunner, preview_lines
from wordclock.matrix.scenes import (
    SCENE_NAMES,
    RainbowScene,
    RainScene,
    SparkleScene,
    TextScene,
    WiringScene,
    create_scene,
    local_ip,
)


def lit_cells(canvas: Canvas) -> set[tuple[int, int]]:
    return {
        (x, y) for y, row in enumerate(canvas.rows()) for x, color in enumerate(row) if any(color)
    }


class TestTextScene:
    def test_first_frame_is_blank(self) -> None:
        # Given: text starts just off the right edge
        canvas = Canvas(10, 6)
        scene = TextScene("A")
        # When
        scene.render(canvas, 0)
        # Then
        assert lit_cells(canvas) == set()

    def test_text_enters_from_the_right(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = TextScene("L", color=(255, 0, 0))
        # When: one step in, the first column of L is on the last column
        scene.render(canvas, 1)
        # Then
        assert lit_cells(canvas) == {(9, y) for y in range(1, 6)}
        assert canvas.get(9, 5) == (255, 0, 0)

    def test_loops_after_leaving_the_left_edge(self) -> None:
        # Given: "L" is 3 columns, so one loop is 3 + 10 frames
        canvas = Canvas(10, 6)
        scene = TextScene("L")
        # When
        scene.render(canvas, 13 + 1)
        # Then
        assert lit_cells(canvas) == {(9, y) for y in range(1, 6)}

    def test_loop_frames_cover_one_pass(self) -> None:
        # Given: "L" is 3 columns wide
        scene = TextScene("L")
        # When
        frames = scene.loop_frames(10)
        # Then
        assert frames == 13

    def test_rainbow_text_changes_colour_along_the_text(self) -> None:
        # Given: "LL" fully on the canvas
        canvas = Canvas(10, 6)
        scene = TextScene("LL", rainbow=True)
        # When
        scene.render(canvas, 10)
        # Then
        colors = {canvas.get(x, y) for x, y in lit_cells(canvas)}
        assert len(colors) > 1


class TestRainScene:
    def test_drops_stay_inside_the_canvas(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = RainScene(seed=1, density=1.0)
        # When
        for frame in range(50):
            scene.render(canvas, frame)
        # Then
        assert lit_cells(canvas)
        assert all(0 <= x < 10 and 0 <= y < 6 for x, y in lit_cells(canvas))


class TestRainbowScene:
    def test_lights_every_cell(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        RainbowScene().render(canvas, 0)
        # Then
        assert len(lit_cells(canvas)) == 60


class TestSparkleScene:
    def test_lights_cells_that_then_fade(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = SparkleScene(seed=1, per_frame=3)
        # When
        scene.render(canvas, 0)
        first = lit_cells(canvas)
        for frame in range(1, 40):
            scene.render(canvas, frame)
        # Then
        assert first
        assert all(0 <= x < 10 and 0 <= y < 6 for x, y in lit_cells(canvas))


class TestWiringScene:
    @pytest.mark.parametrize(
        ("frame", "cell"), [(0, (0, 0)), (9, (9, 0)), (10, (0, 1)), (60, (0, 0))]
    )
    def test_lights_one_cell_in_order(self, frame: int, cell: tuple[int, int]) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        WiringScene().render(canvas, frame)
        # Then
        assert lit_cells(canvas) == {cell}


class TestCreateScene:
    @pytest.mark.parametrize("name", SCENE_NAMES)
    def test_builds_every_scene(self, name: str) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        scene = create_scene(name)
        scene.render(canvas, 0)
        # Then
        assert scene.fps > 0

    def test_unknown_scene(self) -> None:
        # Given / When / Then
        with pytest.raises(ValueError, match="Unknown scene"):
            create_scene("tetris")


class TestLocalIp:
    def test_returns_an_address(self) -> None:
        # Given / When
        ip = local_ip()
        # Then
        assert ip == "NO IP" or ip.count(".") == 3


class TestMatrixRunner:
    def test_sends_the_snake_to_the_strip(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        ctrl = MockLedController(num_leds=60)
        runner = MatrixRunner(canvas, ctrl, max_ma=1500)
        canvas.set(0, 1, (10, 20, 30))
        # When
        runner.show_frame()
        # Then
        assert ctrl.get_state()[19] == (10, 20, 30)

    def test_play_stops_after_the_given_time(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        ctrl = MockLedController(num_leds=60)
        runner = MatrixRunner(canvas, ctrl, max_ma=1500)
        # When
        runner.play(WiringScene(fps=1000), seconds=0.01)
        # Then: the strip is cleared at the end
        assert not any(any(px) for px in ctrl.get_state())

    def test_preview_draws_one_line_per_row(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        canvas.set(0, 0, (255, 0, 0))
        # When
        lines = preview_lines(canvas)
        # Then
        assert len(lines) == 6
        assert "38;2;255;0;0m" in lines[0]
