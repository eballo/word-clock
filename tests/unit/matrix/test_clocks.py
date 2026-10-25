from __future__ import annotations

from datetime import datetime

import pytest

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.clocks import (
    AM_HOURS,
    FIVE_MINUTES,
    MINUTES,
    PM_HOURS,
    BlocksClock,
    DialClock,
    TixClock,
)

# The example of the design: 3:17:42 in the afternoon.
AFTERNOON = datetime(2026, 10, 25, 15, 17, 42)


def at(now: datetime):
    return lambda: now


def cells_of(canvas: Canvas, color: Color) -> list[tuple[int, int]]:
    return [(x, y) for y, row in enumerate(canvas.rows()) for x, c in enumerate(row) if c == color]


def row_lit(canvas: Canvas, y: int) -> int:
    return sum(1 for c in canvas.rows()[y] if any(c))


class TestBlocksClock:
    def test_counts_hours_five_minutes_and_minutes(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        BlocksClock(clock=at(AFTERNOON)).render(canvas, 0)
        # Then: 3 violet hours, 3 blocks of 5 minutes, 2 minutes
        assert cells_of(canvas, PM_HOURS) == [(0, 0), (1, 0), (2, 0)]
        assert cells_of(canvas, FIVE_MINUTES) == [(0, 2), (1, 2), (2, 2)]
        assert cells_of(canvas, MINUTES) == [(0, 4), (1, 4)]

    def test_seconds_fill_the_bottom_row(self) -> None:
        # Given: 42 s = 7 full cells of 6 s, the 8th just starting
        canvas = Canvas(10, 6)
        # When
        BlocksClock(clock=at(AFTERNOON)).render(canvas, 0)
        # Then
        assert row_lit(canvas, 5) == 7

    @pytest.mark.parametrize(("hour", "count"), [(0, 12), (12, 12), (11, 11), (23, 11)])
    def test_twelve_hour_clock(self, hour: int, count: int) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        BlocksClock(clock=at(datetime(2026, 1, 1, hour, 0))).render(canvas, 0)
        # Then: hours spill into row 1 after 10
        assert row_lit(canvas, 0) + row_lit(canvas, 1) == count

    def test_morning_hours_are_blue(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        BlocksClock(clock=at(datetime(2026, 1, 1, 9, 0))).render(canvas, 0)
        # Then
        assert len(cells_of(canvas, AM_HOURS)) == 9


class TestDialClock:
    def test_hour_half_row_and_minutes(self) -> None:
        # Given: no dot in the way at 0 s
        canvas = Canvas(10, 6)
        now = datetime(2026, 1, 1, 15, 17, 0)
        # When
        DialClock(clock=at(now)).render(canvas, 0)
        # Then: hour 3 is the right half of row 1, minutes fill 17 cells
        hour_cells = {(x, y) for x, y in [(5, 1), (6, 1), (7, 1), (8, 1), (9, 1)]}
        assert all(canvas.get(x, y)[2] > 0 for x, y in hour_cells)
        assert all(canvas.get(x, 0)[1] > 0 for x in range(10))
        # Minute 17 (cell 16) is lit, minute 18 (cell 17) only has the hour glow
        assert canvas.get(6, 1)[1] > canvas.get(7, 1)[1]

    def test_dot_goes_round_once_a_minute(self) -> None:
        # Given: 42 s, at the top of the hour so nothing else is lit there
        canvas = Canvas(10, 6)
        now = datetime(2026, 1, 1, 0, 0, 42)
        # When
        DialClock(clock=at(now)).render(canvas, 0)
        # Then: cell 42 is row 4, column 2
        assert canvas.get(2, 4) == (255, 255, 255)


class TestTixClock:
    def test_lights_as_many_cells_as_each_digit(self) -> None:
        # Given: 15:17
        canvas = Canvas(10, 6)
        # When
        TixClock(clock=at(AFTERNOON)).render(canvas, 0)
        # Then
        full = [c for _, _, c in TixClock.BLOCKS]
        assert len(cells_of(canvas, full[1])) == 5
        assert len(cells_of(canvas, full[2])) == 1
        # Hour tens and minute units share red: 1 + 7
        assert len(cells_of(canvas, full[0])) == 8

    def test_places_change_every_few_seconds(self) -> None:
        # Given
        first, later = Canvas(10, 6), Canvas(10, 6)
        # When
        TixClock(clock=at(datetime(2026, 1, 1, 8, 8, 0))).render(first, 0)
        TixClock(clock=at(datetime(2026, 1, 1, 8, 8, 20))).render(later, 0)
        # Then
        assert first.rows()[1:4] != later.rows()[1:4]

    def test_same_places_within_the_shuffle_time(self) -> None:
        # Given
        first, later = Canvas(10, 6), Canvas(10, 6)
        # When
        TixClock(clock=at(datetime(2026, 1, 1, 8, 8, 0))).render(first, 0)
        TixClock(clock=at(datetime(2026, 1, 1, 8, 8, 1))).render(later, 0)
        # Then: only the seconds row may differ
        assert first.rows()[1:4] == later.rows()[1:4]
