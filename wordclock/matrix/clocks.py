from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from random import Random

from wordclock.matrix.canvas import Canvas, Color

AM_HOURS: Color = (0, 90, 255)
PM_HOURS: Color = (150, 40, 255)
FIVE_MINUTES: Color = (0, 220, 60)
MINUTES: Color = (255, 180, 0)
SECONDS: Color = (120, 200, 255)


def scale(color: Color, level: float) -> Color:
    """
    Dim a colour.

    Args:
        color: The full colour.
        level: 0 for black, 1 for the full colour.

    Returns:
        The dimmed colour.
    """
    return (round(color[0] * level), round(color[1] * level), round(color[2] * level))


def add(a: Color, b: Color) -> Color:
    """
    Mix two lights on the same cell.

    Args:
        a: One colour.
        b: The other colour.

    Returns:
        Their sum, each channel capped at 255.
    """
    return (min(255, a[0] + b[0]), min(255, a[1] + b[1]), min(255, a[2] + b[2]))


def hour_color(hour: int) -> Color:
    """
    Colour of the hours: blue in the morning, violet in the afternoon.

    Args:
        hour: Hour of the day, 0 to 23.

    Returns:
        The colour for that half of the day.
    """
    return AM_HOURS if hour < 12 else PM_HOURS


def fill(canvas: Canvas, rows: range, count: int, color: Color) -> None:
    """
    Light ``count`` cells in reading order over some rows.

    Args:
        canvas: The canvas to draw on.
        rows: The rows to use, top to bottom.
        count: How many cells to light.
        color: Their colour.
    """
    for i in range(min(count, len(rows) * canvas.width)):
        canvas.set(i % canvas.width, rows[i // canvas.width], color)


class BlocksClock:
    """
    The time by counting cells, top to bottom.

    Rows 0-1: one cell per hour (12-hour clock, blue in the morning, violet in
    the afternoon). Rows 2-3: one cell per 5 minutes. Row 4: the minutes left
    over, 0 to 4. Row 5: one cell per 6 seconds, the current one fading in.
    """

    def __init__(self, fps: float = 10, clock: Callable[[], datetime] = datetime.now) -> None:
        self.fps = fps
        self._clock = clock

    def render(self, canvas: Canvas, frame: int) -> None:
        now = self._clock()
        canvas.clear()
        fill(canvas, range(0, 2), now.hour % 12 or 12, hour_color(now.hour))
        fill(canvas, range(2, 4), now.minute // 5, FIVE_MINUTES)
        fill(canvas, range(4, 5), now.minute % 5, MINUTES)
        seconds = now.second + now.microsecond / 1e6
        step = 60 / canvas.width
        fill(canvas, range(5, 6), int(seconds // step), SECONDS)
        current = int(seconds // step)
        if current < canvas.width:
            canvas.set(current, 5, scale(SECONDS, (seconds % step) / step))


class DialClock:
    """
    The matrix as a clock face: 60 cells, one per minute and one per second.

    The cells fill with the minutes in reading order, every row ten minutes.
    The twelve half rows are the twelve hours of a dial: the one for the
    hour glows blue. A white dot runs over every cell once a minute.
    """

    def __init__(self, fps: float = 20, clock: Callable[[], datetime] = datetime.now) -> None:
        self.fps = fps
        self._clock = clock

    def render(self, canvas: Canvas, frame: int) -> None:
        now = self._clock()
        cells = canvas.width * canvas.height
        per_hour = cells // 12
        per_minute = cells / 60
        hour_cells = range((now.hour % 12) * per_hour, (now.hour % 12 + 1) * per_hour)
        minute_cells = int(now.minute * per_minute)
        seconds = now.second + now.microsecond / 1e6
        dot = seconds * per_minute
        for i in range(cells):
            color: Color = (0, 0, 0)
            if i < minute_cells:
                color = scale(FIVE_MINUTES, 0.35)
            if i in hour_cells:
                color = add(color, scale(hour_color(now.hour), 0.8))
            # The dot and a short fading trail behind it.
            behind = dot - i
            if 0 <= behind < 3:
                color = add(color, scale((255, 255, 255), 1 - behind / 3))
            canvas.set(i % canvas.width, i // canvas.width, color)


class TixClock:
    """
    TIX style: each digit of ``HH:MM`` is a block of its own colour with as
    many cells lit as the digit, at random places that change every few
    seconds. Row 5 fills with the seconds.

    Columns on a 10-cell row: hour tens (1), hour units (3), a gap, minute
    tens (2), minute units (3); three rows high.
    """

    BLOCKS: tuple[tuple[int, int, Color], ...] = (
        (0, 1, (255, 30, 30)),
        (1, 3, (40, 220, 60)),
        (5, 2, (40, 90, 255)),
        (7, 3, (255, 30, 30)),
    )
    TOP = 1
    HEIGHT = 3

    def __init__(
        self,
        fps: float = 10,
        shuffle_seconds: int = 4,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.fps = fps
        self.shuffle_seconds = shuffle_seconds
        self._clock = clock

    def render(self, canvas: Canvas, frame: int) -> None:
        now = self._clock()
        digits = (now.hour // 10, now.hour % 10, now.minute // 10, now.minute % 10)
        # Same places for a few seconds, then new ones.
        random = Random(int(now.timestamp()) // self.shuffle_seconds)
        canvas.clear()
        for (left, width, color), digit in zip(self.BLOCKS, digits, strict=True):
            places = [(left + x, self.TOP + y) for y in range(self.HEIGHT) for x in range(width)]
            for x, y in places:
                canvas.set(x, y, scale(color, 0.06))
            for x, y in random.sample(places, min(digit, len(places))):
                canvas.set(x, y, color)
        step = 60 / canvas.width
        fill(
            canvas,
            range(canvas.height - 1, canvas.height),
            int(now.second // step),
            scale(SECONDS, 0.5),
        )
