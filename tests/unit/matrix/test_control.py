from __future__ import annotations

from wordclock.matrix.button import ButtonAction
from wordclock.matrix.canvas import Canvas
from wordclock.matrix.control import COUNTDOWN_SECONDS, PHOTO_SECONDS, ControlledScene
from wordclock.matrix.scenes import RainbowScene, WiringScene

FPS = 30


def lit(canvas: Canvas) -> int:
    return sum(1 for row in canvas.rows() for color in row if any(color))


def play(scene: ControlledScene, canvas: Canvas, start: int, seconds: float) -> int:
    end = start + int(seconds * FPS)
    for frame in range(start, end):
        scene.render(canvas, frame)
    return end


class TestControlledScene:
    def test_plays_the_base_scene(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = ControlledScene(RainbowScene())
        # When
        scene.render(canvas, 0)
        # Then
        assert lit(canvas) == 60

    def test_toggle_turns_the_lights_off_and_on(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = ControlledScene(RainbowScene())
        # When
        scene.handle(ButtonAction.TOGGLE)
        scene.render(canvas, 0)
        off = lit(canvas)
        scene.handle(ButtonAction.TOGGLE)
        scene.render(canvas, 1)
        # Then
        assert off == 0
        assert lit(canvas) == 60

    def test_photo_counts_down_then_asks_the_camera(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        captures: list[int] = []
        scene = ControlledScene(RainbowScene(), capture=lambda: captures.append(1))
        # When
        scene.handle(ButtonAction.PHOTO)
        frame = play(scene, canvas, 0, COUNTDOWN_SECONDS - 0.5)
        before = list(captures)
        play(scene, canvas, frame, 1)
        # Then: once, after the countdown, during the white flash
        assert before == []
        assert captures == [1]
        assert lit(canvas) == 60

    def test_shows_the_photo_then_goes_back(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = ControlledScene(WiringScene())
        # When
        scene.show_photo([(0, 0, 9)] * 60, 10)
        frame = play(scene, canvas, 0, 2)
        photo = lit(canvas)
        play(scene, canvas, frame, PHOTO_SECONDS)
        # Then: the wiring scene lights one cell
        assert photo == 60
        assert lit(canvas) == 1

    def test_shutdown_calls_back(self) -> None:
        # Given
        calls: list[int] = []
        scene = ControlledScene(RainbowScene(), shutdown=lambda: calls.append(1))
        # When
        scene.handle(ButtonAction.SHUTDOWN)
        # Then
        assert calls == [1]

    def test_set_base_switches_the_scene(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = ControlledScene(RainbowScene())
        scene.render(canvas, 0)
        # When
        scene.set_base(WiringScene())
        scene.render(canvas, 1)
        # Then
        assert lit(canvas) == 1
