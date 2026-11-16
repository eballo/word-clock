from __future__ import annotations

import pytest

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.feeds import WEATHER_WORDS, Feed, Weather
from wordclock.matrix.screens import (
    LEVELS,
    REST,
    WORK,
    CommitsScene,
    LifeScene,
    PomodoroScene,
    WeatherScene,
    draw_weather,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def lit(canvas: Canvas) -> int:
    return sum(1 for row in canvas.rows() for color in row if any(color))


def feed(value: object, error: str | None = None) -> Feed:
    result = Feed(lambda: value, 3600, "test", background=False)
    if value is None:
        result = Feed(
            lambda: (_ for _ in ()).throw(OSError(error or "x")), 3600, "test", background=False
        )
    return result


class TestPomodoro:
    def test_cells_empty_as_time_runs_out(self) -> None:
        # Given: 25 min of work = 60 cells
        clock = FakeClock()
        scene = PomodoroScene(clock=clock)
        canvas = Canvas(10, 6)
        # When: 12,5 min later
        clock.now += 12.5 * 60
        scene.render(canvas, 0)
        # Then: half the cells, red
        assert lit(canvas) == 30
        assert canvas.get(0, 0) == WORK

    def test_pause_stops_the_time(self) -> None:
        # Given
        clock = FakeClock()
        scene = PomodoroScene(clock=clock)
        # When: paused for 10 min
        scene.on_press()
        clock.now += 600
        left = scene.remaining()
        scene.on_press()
        # Then
        assert left == pytest.approx(25 * 60)
        assert not scene.paused

    def test_work_turns_into_rest_with_a_flash(self) -> None:
        # Given
        clock = FakeClock()
        scene = PomodoroScene(clock=clock)
        canvas = Canvas(10, 6)
        # When: work is over
        clock.now += 25 * 60 + 0.01
        scene.render(canvas, 0)
        # Then
        assert scene.phase == "rest"
        assert lit(canvas) in (0, 60)
        clock.now += 3
        scene.render(canvas, 1)
        assert canvas.get(0, 0) == REST


class TestLife:
    def test_dead_world_starts_again(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = LifeScene(seed=1, density=0.0)
        scene.render(canvas, 0)
        # When: everything is dead from the start
        scene.density = 0.4
        scene.render(canvas, 1)
        # Then: a new world was seeded
        assert scene.generation == 0
        assert lit(canvas) > 0

    def test_runs_generations(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = LifeScene(seed=3)
        # When
        for frame in range(30):
            scene.render(canvas, frame)
        # Then: it is alive and within the canvas
        assert lit(canvas) > 0
        assert scene.generation <= 30

    def test_blinker_loops_and_restarts(self) -> None:
        # Given: a blinker, which repeats every 2 generations
        canvas = Canvas(10, 6)
        scene = LifeScene(seed=1)
        scene.render(canvas, 0)
        scene._ages = [[0] * 10 for _ in range(6)]
        for x in (3, 4, 5):
            scene._ages[2][x] = 1
        # When
        for frame in range(1, 5):
            scene.render(canvas, frame)
        # Then
        assert scene.generation < 4


class TestWeather:
    @pytest.mark.parametrize("kind", WEATHER_WORDS)
    @pytest.mark.parametrize("is_day", [True, False])
    def test_every_icon_draws_something(self, kind: str, is_day: bool) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        draw_weather(canvas, kind, is_day, 0, 8)
        # Then
        assert lit(canvas) > 0

    def test_icon_then_temperature(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = WeatherScene(feed(Weather(18.4, 61, True)))
        # When: in the icon, then in the text
        scene.render(canvas, 0)
        icon = canvas.rows()
        scene.render(canvas, 6 * 8 + 6)
        # Then
        assert lit(canvas) > 0
        assert canvas.rows() != icon

    def test_waits_for_data(self) -> None:
        # Given: the fetch fails
        canvas = Canvas(10, 6)
        scene = WeatherScene(feed(None, "offline"))
        # When
        scene.render(canvas, 20)
        # Then: three dots, the first ones red
        assert 1 <= lit(canvas) <= 3
        assert any(canvas.get(x, 3)[0] > canvas.get(x, 3)[1] for x in range(10))


class TestCommits:
    def test_one_cell_per_day(self) -> None:
        # Given: no commits except the busiest day, 59 days ago
        canvas = Canvas(10, 6)
        scene = CommitsScene(feed([8] + [0] * 59))
        # When
        scene.render(canvas, 0)
        # Then
        assert canvas.get(0, 0) == LEVELS[4]
        assert canvas.get(5, 3) == (0, 0, 0)

    def test_today_breathes(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = CommitsScene(feed([1] * 60))
        # When
        scene.render(canvas, 0)
        first = canvas.get(9, 5)
        scene.render(canvas, 4)
        # Then
        assert canvas.get(9, 5) != first

    def test_then_shows_the_total(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = CommitsScene(feed([1] * 60))
        # When: after the heatmap
        scene.render(canvas, 8 * 8 + 12)
        # Then: text, not the full heatmap
        assert 0 < lit(canvas) < 60
