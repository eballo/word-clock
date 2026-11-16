from __future__ import annotations

from datetime import datetime, time

import pytest

from wordclock.led.controller import MockLedController
from wordclock.matrix.canvas import Canvas
from wordclock.matrix.dimmer import (
    DEFAULT_SUN,
    RAMP_MINUTES,
    BrightnessLevels,
    Dimmer,
    Phase,
    is_night,
    phase_at,
    ramped_level,
)
from wordclock.matrix.feeds import Feed, SunTimes
from wordclock.matrix.runner import MatrixRunner

LEVELS = BrightnessLevels(day=90, evening=30, night=6)
# A winter day: the sun rises after the night ends at 07:00.
WINTER = SunTimes(sunrise=time(8, 15), sunset=time(17, 45))


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, 16, hour, minute)


class FakeClock:
    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def __call__(self) -> datetime:
        return self.moment


class TestIsNight:
    @pytest.mark.parametrize(("hour", "night"), [(22, False), (23, True), (6, True), (7, False)])
    def test_from_23_to_7(self, hour: int, night: bool) -> None:
        # Given / When / Then
        assert is_night(hour) is night


class TestBrightnessLevels:
    def test_reads_each_phase(self) -> None:
        # Given / When / Then
        assert [LEVELS.of(phase) for phase in Phase] == [90, 30, 6]

    def test_day_is_brighter_than_the_night_by_default(self) -> None:
        # Given
        levels = BrightnessLevels()
        # When / Then
        assert levels.day > levels.evening > levels.night

    @pytest.mark.parametrize("value", [-1, 256, "high", True])
    def test_rejects_values_out_of_range(self, value: object) -> None:
        # Given / When / Then
        with pytest.raises(ValueError, match="day"):
            BrightnessLevels(day=value)


class TestPhaseAt:
    @pytest.mark.parametrize(
        ("moment", "phase"),
        [
            (at(3), Phase.NIGHT),
            (at(7, 30), Phase.EVENING),
            (at(8, 15), Phase.DAY),
            (at(13), Phase.DAY),
            (at(17, 45), Phase.EVENING),
            (at(22, 59), Phase.EVENING),
            (at(23), Phase.NIGHT),
        ],
    )
    def test_follows_the_sun_and_the_night(self, moment: datetime, phase: Phase) -> None:
        # Given / When / Then
        assert phase_at(moment, WINTER) == phase


class TestRampedLevel:
    def test_steady_inside_a_phase(self) -> None:
        # Given / When / Then
        assert ramped_level(at(13), WINTER, LEVELS) == 90

    def test_fades_after_sunset(self) -> None:
        # Given: 15 minutes after sunset, 16 of the last 30 minutes are evening
        moment = at(18, 0)
        # When
        level = ramped_level(moment, WINTER, LEVELS)
        # Then
        assert level == round((14 * 90 + 16 * 30) / 30)

    def test_reaches_the_new_level_at_the_end_of_the_ramp(self) -> None:
        # Given / When / Then
        assert ramped_level(at(23, RAMP_MINUTES - 1), WINTER, LEVELS) == 6

    def test_never_jumps_more_than_one_step_a_minute(self) -> None:
        # Given
        levels = [ramped_level(at(h, m), WINTER, LEVELS) for h in range(24) for m in range(60)]
        # When
        steps = [abs(b - a) for a, b in zip(levels, levels[1:], strict=False)]
        # Then
        assert max(steps) <= (LEVELS.day - LEVELS.evening) / RAMP_MINUTES + 1


class TestDimmer:
    def test_uses_the_default_sun_without_a_feed(self) -> None:
        # Given
        dimmer = Dimmer(LEVELS, clock=FakeClock(at(13)))
        # When / Then
        assert dimmer.sun_times() == DEFAULT_SUN
        assert dimmer.brightness() == 90

    def test_uses_the_sun_from_the_feed(self) -> None:
        # Given: an early sunset
        sun = Feed(lambda: SunTimes(time(8, 0), time(16, 0)), 60, "sun", background=False)
        dimmer = Dimmer(LEVELS, sun, clock=FakeClock(at(18)))
        # When / Then
        assert dimmer.brightness() == 30

    def test_dims_from_day_to_night(self) -> None:
        # Given
        clock = FakeClock(at(13))
        dimmer = Dimmer(LEVELS, clock=clock)
        # When
        day = dimmer.brightness()
        clock.moment = at(21)
        evening = dimmer.brightness()
        clock.moment = at(2)
        night = dimmer.brightness()
        # Then
        assert (day, evening, night) == (90, 30, 6)

    def test_manual_brightness_holds_until_the_phase_changes(self) -> None:
        # Given
        clock = FakeClock(at(13))
        dimmer = Dimmer(LEVELS, clock=clock)
        # When
        dimmer.set_manual(200)
        clock.moment = at(18, 30)
        held = dimmer.brightness()
        clock.moment = at(19, 30)
        evening = dimmer.brightness()
        # Then
        assert held == 200
        assert evening == 30
        assert not dimmer.manual


class TestRunnerWithDimmer:
    def test_sets_the_strip_brightness_every_frame(self) -> None:
        # Given
        controller = MockLedController(num_leds=60, brightness=255)
        dimmer = Dimmer(LEVELS, clock=FakeClock(at(2)))
        runner = MatrixRunner(Canvas(10, 6), controller, max_ma=1500, dimmer=dimmer)
        # When
        runner.show_frame()
        # Then
        assert controller.brightness == 6
