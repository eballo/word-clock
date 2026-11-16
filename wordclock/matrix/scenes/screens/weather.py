from __future__ import annotations

import math
from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import scale
from wordclock.matrix.feeds import Feed, Weather, weather_kind
from wordclock.matrix.scenes.screens.loading import loading
from wordclock.matrix.scenes.text import TextScene
from wordclock.matrix.texts import Locale

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
        kind: One of the kinds of :data:`wordclock.matrix.feeds.WEATHER_KINDS`.
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

    def __init__(self, feed: Feed[Weather], fps: float = 8, locale: Locale | None = None) -> None:
        self.fps = fps
        self._feed = feed
        self._locale = locale or Locale()
        self._text = TextScene("", fps=fps)
        self._text_key: str | None = None

    def render(self, canvas: Canvas, frame: int) -> None:
        weather = self._feed.get()
        if weather is None:
            loading(canvas, frame, self.fps, failed=self._feed.error is not None)
            return
        kind = weather_kind(weather.code)
        words = f"{round(weather.temperature)}° {self._locale.texts.weather[kind]}"
        if words != self._text_key:
            self._text = TextScene(words, color=(255, 255, 255), fps=self.fps)
            self._text_key = words
        icon_frames = int(ICON_SECONDS * self.fps)
        step = frame % (icon_frames + self._text.loop_frames(canvas.width))
        if step < icon_frames:
            draw_weather(canvas, kind, weather.is_day, frame, self.fps)
        else:
            self._text.render(canvas, step - icon_frames)
