from __future__ import annotations

import math
import time
from collections.abc import Callable
from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.clocks import add, scale
from wordclock.matrix.feeds import WEATHER_WORDS, Feed, Weather, contribution_level, weather_kind
from wordclock.matrix.scenes import TextScene, hue_color

# --- Pomodoro ---------------------------------------------------------------

WORK: Color = (255, 40, 20)
REST: Color = (0, 200, 80)
FLASH_SECONDS = 2.0


class PomodoroScene:
    """
    A pomodoro timer: 25 minutes of work, then 5 of rest, again and again.

    The cells empty as the time runs out, red for work and green for rest,
    and the last lit cell blinks. A press of the button pauses and resumes
    it; while paused, the cells breathe. The matrix flashes when a phase
    ends.
    """

    def __init__(
        self,
        work_minutes: float = 25,
        rest_minutes: float = 5,
        fps: float = 10,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.fps = fps
        self.lengths = {"work": work_minutes * 60, "rest": rest_minutes * 60}
        self._clock = clock
        self.phase = "work"
        self._started = clock()
        self._paused_at: float | None = None
        self._flash_until = 0.0

    @property
    def paused(self) -> bool:
        return self._paused_at is not None

    def on_press(self) -> None:
        """Pause, or resume where it was."""
        now = self._clock()
        if self._paused_at is None:
            self._paused_at = now
        else:
            self._started += now - self._paused_at
            self._paused_at = None

    def remaining(self) -> float:
        """
        Return the time left in this phase, moving to the next phase when
        it is over.

        Returns:
            Seconds left.
        """
        now = self._paused_at if self._paused_at is not None else self._clock()
        left = self.lengths[self.phase] - (now - self._started)
        if left <= 0:
            self.phase = "rest" if self.phase == "work" else "work"
            self._started = now
            self._flash_until = now + FLASH_SECONDS
            left = self.lengths[self.phase]
        return left

    def render(self, canvas: Canvas, frame: int) -> None:
        left = self.remaining()
        now = self._clock()
        color = WORK if self.phase == "work" else REST
        canvas.clear()
        if now < self._flash_until:
            if int(now * 4) % 2 == 0:
                canvas.fill(color)
            return
        cells = canvas.width * canvas.height
        lit = math.ceil(left / self.lengths[self.phase] * cells)
        level = 1.0
        if self.paused:
            level = 0.45 + 0.35 * math.sin(now * 2)
        for i in range(lit):
            shade = level
            if i == lit - 1 and not self.paused and int(now * 2) % 2:
                shade = 0.3
            canvas.set(i % canvas.width, i // canvas.width, scale(color, shade))


# --- Game of Life -----------------------------------------------------------


class LifeScene:
    """
    Conway's Game of Life on a matrix that wraps around at the edges.

    New cells are bright and turn bluer as they age. When life dies out,
    freezes or loops, it starts again from a new random pattern.
    """

    def __init__(
        self,
        fps: float = 5,
        density: float = 0.35,
        max_generations: int = 300,
        seed: int | None = None,
    ) -> None:
        self.fps = fps
        self.density = density
        self.max_generations = max_generations
        self._random = Random(seed)
        self._ages: list[list[int]] = []
        self._seen: list[tuple[tuple[bool, ...], ...]] = []
        self.generation = 0

    def _seed(self, width: int, height: int) -> None:
        self._ages = [
            [1 if self._random.random() < self.density else 0 for _ in range(width)]
            for _ in range(height)
        ]
        self._seen = []
        self.generation = 0

    def _step(self) -> None:
        height, width = len(self._ages), len(self._ages[0])
        new = [[0] * width for _ in range(height)]
        for y in range(height):
            for x in range(width):
                neighbours = sum(
                    1
                    for dy in (-1, 0, 1)
                    for dx in (-1, 0, 1)
                    if (dx or dy) and self._ages[(y + dy) % height][(x + dx) % width]
                )
                alive = self._ages[y][x] > 0
                if neighbours == 3 or (alive and neighbours == 2):
                    new[y][x] = self._ages[y][x] + 1
        self._ages = new
        self.generation += 1

    def _alive(self) -> tuple[tuple[bool, ...], ...]:
        return tuple(tuple(age > 0 for age in row) for row in self._ages)

    def render(self, canvas: Canvas, frame: int) -> None:
        if not self._ages or len(self._ages) != canvas.height:
            self._seed(canvas.width, canvas.height)
        elif frame > 0:
            self._step()
            state = self._alive()
            if (
                not any(any(row) for row in state)
                or state in self._seen
                or self.generation >= self.max_generations
            ):
                self._seed(canvas.width, canvas.height)
            else:
                self._seen = [*self._seen[-5:], state]
        canvas.clear()
        for y, row in enumerate(self._ages):
            for x, age in enumerate(row):
                if age:
                    canvas.set(x, y, hue_color(0.45 + min(age, 12) * 0.025))


# --- Weather ----------------------------------------------------------------

SUN: Color = (255, 190, 0)
MOON: Color = (220, 220, 170)
CLOUD: Color = (150, 150, 165)
DARK_CLOUD: Color = (70, 70, 90)
DROP: Color = (40, 120, 255)
SNOW: Color = (230, 240, 255)
BOLT: Color = (255, 230, 60)

ICON_SECONDS = 6.0


def _cloud_cells(width: int, height: int, top: float, drift: float) -> set[tuple[int, int]]:
    puffs = ((0.3, 0.55, 0.16), (0.55, 0.35, 0.21), (0.75, 0.6, 0.15))
    cells = set()
    for y in range(height):
        for x in range(width):
            for px, py, r in puffs:
                dx = (x + 0.5) / width - px - drift
                dy = ((y + 0.5) - top) / (height * 0.6) - py
                if dx * dx + (dy * 0.6) ** 2 <= r * r and y >= top:
                    cells.add((x, y))
    return cells


def draw_weather(canvas: Canvas, kind: str, is_day: bool, frame: int, fps: float) -> None:
    """
    Draw an animated weather icon over the whole matrix.

    Args:
        canvas: The canvas to draw on.
        kind: One of the keys of :data:`WEATHER_WORDS`.
        is_day: False draws the moon instead of the sun.
        frame: Frame number, for the animation.
        fps: Frames per second.
    """
    t = frame / fps
    w, h = canvas.width, canvas.height
    canvas.clear()
    if kind == "clear":
        cx, cy = (w - 1) / 2, (h - 1) / 2
        for y in range(h):
            for x in range(w):
                dist = math.hypot(x - cx, y - cy)
                if is_day:
                    angle = math.degrees(math.atan2(y - cy, x - cx)) % 45
                    ray = 2.4 < dist < 3.6 and min(angle, 45 - angle) < 12
                    if dist <= 1.9:
                        canvas.set(x, y, SUN)
                    elif ray and int(t * 2) % 2 == 0:
                        canvas.set(x, y, scale(SUN, 0.6))
                elif dist <= 2.2 and math.hypot(x - cx - 1.2, y - cy + 0.6) > 1.9:
                    canvas.set(x, y, MOON)
        if not is_day:
            random = Random(7)
            for _ in range(5):
                x, y = random.randrange(w), random.randrange(h)
                if not any(canvas.get(x, y)):
                    twinkle = 0.3 + 0.7 * abs(math.sin(t * 1.5 + x + y))
                    canvas.set(x, y, scale((255, 255, 255), twinkle))
        return
    if kind == "fog":
        for y in range(h):
            if y % 2 == 0:
                for x in range(w):
                    if (x + int(t * 3) + y) % 7 not in (0, 1):
                        canvas.set(x, y, scale(CLOUD, 0.7))
        return
    wet = kind in ("drizzle", "rain", "snow", "storm")
    drift = 0.04 * math.sin(t * 0.8)
    top = 0 if wet else h * 0.15
    cloud = _cloud_cells(w, 3 if wet else h, top, drift)
    color = DARK_CLOUD if kind == "storm" else CLOUD
    for x, y in cloud:
        canvas.set(x, y, color)
    if kind == "storm" and int(t * 3) % 9 in (0, 2):
        for x, y in ((5, 2), (4, 3), (5, 3), (4, 4), (3, 5)):
            if x < w and y < h:
                canvas.set(x, y, BOLT)
    if kind in ("drizzle", "rain", "storm"):
        speed = 6 if kind != "drizzle" else 3
        for x in range(0, w, 2 if kind != "drizzle" else 3):
            y = 3 + (int(t * speed) + x * 7) % (h - 2)
            if y < h:
                canvas.set(x, y, DROP)
    if kind == "snow":
        for x in range(1, w, 3):
            y = 3 + (int(t * 1.5) + x) % (h - 3)
            if y < h:
                canvas.set(x, y, SNOW)


class WeatherScene:
    """
    The weather now: an animated icon, then the temperature and a word
    (``18° PLUJA``) scrolling past.
    """

    def __init__(self, feed: Feed[Weather], fps: float = 8) -> None:
        self.fps = fps
        self._feed = feed
        self._text = TextScene("", fps=fps)
        self._text_key: str | None = None

    def render(self, canvas: Canvas, frame: int) -> None:
        weather = self._feed.get()
        if weather is None:
            loading(canvas, frame, self.fps, failed=self._feed.error is not None)
            return
        kind = weather_kind(weather.code)
        words = f"{round(weather.temperature)}° {WEATHER_WORDS[kind]}"
        if words != self._text_key:
            self._text = TextScene(words, color=(255, 255, 255), fps=self.fps)
            self._text_key = words
        icon_frames = int(ICON_SECONDS * self.fps)
        step = frame % (icon_frames + self._text.loop_frames(canvas.width))
        if step < icon_frames:
            draw_weather(canvas, kind, weather.is_day, frame, self.fps)
        else:
            self._text.render(canvas, step - icon_frames)


# --- GitHub contributions ---------------------------------------------------

# GitHub greens, made brighter for LEDs, for levels 1 to 4.
LEVELS: tuple[Color, ...] = ((0, 0, 0), (0, 45, 12), (0, 100, 30), (0, 170, 50), (60, 255, 90))
HEATMAP_SECONDS = 8.0


def loading(canvas: Canvas, frame: int, fps: float, failed: bool = False) -> None:
    """
    Draw three dots that wait for data, red when the last fetch failed.

    Args:
        canvas: The canvas to draw on.
        frame: Frame number, for the animation.
        fps: Frames per second.
        failed: The last fetch failed.
    """
    canvas.clear()
    color = (255, 40, 20) if failed else (120, 120, 120)
    y = canvas.height // 2
    lit = int(frame / fps * 3) % 4
    for i in range(3):
        x = canvas.width // 2 - 2 + i * 2
        canvas.set(x, y, color if i < lit else scale(color, 0.2))


class CommitsScene:
    """
    GitHub contributions of the last days, one cell per day in reading
    order, oldest top left and today bottom right, shaded like GitHub;
    today breathes. Then the total scrolls past.
    """

    def __init__(self, feed: Feed[list[int]], fps: float = 8) -> None:
        self.fps = fps
        self._feed = feed
        self._text = TextScene("", fps=fps)
        self._text_key: str | None = None

    def render(self, canvas: Canvas, frame: int) -> None:
        counts = self._feed.get()
        if counts is None:
            loading(canvas, frame, self.fps, failed=self._feed.error is not None)
            return
        cells = canvas.width * canvas.height
        days = counts[-cells:]
        words = f"{sum(days)} COMMITS"
        if words != self._text_key:
            self._text = TextScene(words, color=LEVELS[4], fps=self.fps)
            self._text_key = words
        heat_frames = int(HEATMAP_SECONDS * self.fps)
        step = frame % (heat_frames + self._text.loop_frames(canvas.width))
        if step >= heat_frames:
            self._text.render(canvas, step - heat_frames)
            return
        canvas.clear()
        offset = cells - len(days)
        for i, count in enumerate(days):
            color = LEVELS[contribution_level(count, days)]
            if i == len(days) - 1:
                breath = 0.5 + 0.5 * math.sin(frame / self.fps * 3)
                color = add(scale(color, breath), scale((255, 255, 255), 0.15 * breath))
            cell = offset + i
            canvas.set(cell % canvas.width, cell // canvas.width, color)
