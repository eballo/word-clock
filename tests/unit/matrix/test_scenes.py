from __future__ import annotations

from datetime import datetime

import pytest

from wordclock.led.controller import MockLedController
from wordclock.matrix.canvas import Canvas
from wordclock.matrix.font import GLYPHS, fold_char
from wordclock.matrix.runner import MatrixRunner, preview_lines
from wordclock.matrix.scenes import (
    EFFECT_SECONDS,
    MESSAGES,
    SCENE_NAMES,
    WEEKDAYS,
    ClockScene,
    IpScene,
    RainbowScene,
    RainScene,
    ShowScene,
    SparkleScene,
    TextScene,
    WiringScene,
    create_scene,
    date_text,
    greeting,
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
        assert lit_cells(canvas) == {(9, y) for y in range(5)}
        assert canvas.get(9, 0) == (255, 0, 0)

    def test_loops_after_leaving_the_left_edge(self) -> None:
        # Given: "L" is 3 columns, so one loop is 3 + 10 frames
        canvas = Canvas(10, 6)
        scene = TextScene("L")
        # When
        scene.render(canvas, 13 + 1)
        # Then
        assert lit_cells(canvas) == {(9, y) for y in range(5)}

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


class TestGreeting:
    @pytest.mark.parametrize(
        ("hour", "text"),
        [(0, "BONA NIT"), (6, "BON DIA"), (12, "BON DIA"), (13, "BONA TARDA"), (20, "BONA NIT")],
    )
    def test_greets_for_the_time_of_day(self, hour: int, text: str) -> None:
        # Given / When / Then
        assert greeting(hour) == text

    @pytest.mark.parametrize("text", MESSAGES + WEEKDAYS + ("BONA TARDA",))
    def test_every_show_text_has_glyphs(self, text: str) -> None:
        # Given / When
        missing = [char for char in text if fold_char(char) not in GLYPHS]
        # Then
        assert missing == []

    def test_date_uses_the_catalan_weekday(self) -> None:
        # Given: 24 October 2026 is a Saturday
        now = datetime(2026, 10, 24, 10, 0)
        # When / Then
        assert date_text(now) == "DISSABTE 24"


class TestShowScene:
    def play(self, scene: ShowScene, seconds: float) -> list[type]:
        canvas = Canvas(10, 6)
        seen: list[type] = []
        for frame in range(int(seconds * scene.fps)):
            scene.render(canvas, frame)
            assert scene._item is not None
            if not seen or seen[-1] is not type(scene._item.scene):
                seen.append(type(scene._item.scene))
        return seen

    def test_starts_with_the_ip_then_clock_text_and_effect(self) -> None:
        # Given
        scene = ShowScene(seed=1, clock=lambda: datetime(2026, 10, 24, 10, 0))
        # When: long enough for the first round
        seen = self.play(scene, 60 + EFFECT_SECONDS)
        # Then
        assert seen[:3] == [IpScene, ClockScene, TextScene]
        assert seen[3] in (RainbowScene, RainScene, SparkleScene)

    def test_fades_in_from_black(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = ShowScene(seed=1)
        scene._items = iter([RainbowScene])
        # When
        scene.render(canvas, 0)
        dark = max(max(color) for row in canvas.rows() for color in row)
        for frame in range(1, int(scene.fps)):
            scene.render(canvas, frame)
        # Then
        assert dark == 0
        assert max(max(color) for row in canvas.rows() for color in row) == 255

    def test_effect_ends_after_its_time(self) -> None:
        # Given: an effect, then a clock
        canvas = Canvas(10, 6)
        scene = ShowScene(seed=1)
        scene._items = iter([RainbowScene, ClockScene])
        # When
        for frame in range(int(EFFECT_SECONDS * scene.fps) + 1):
            scene.render(canvas, frame)
        # Then
        assert isinstance(scene._item.scene if scene._item else None, ClockScene)


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
