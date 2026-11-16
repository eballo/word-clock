from __future__ import annotations

import math
from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import scale
from wordclock.matrix.feeds import Feed, Weather, weather_kind
from wordclock.matrix.font import FONT_HEIGHT, render_text
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


# Hours ahead of each forecast slot: now, in 3 hours and in 6 hours.
FORECAST_OFFSETS: tuple[int, ...] = (0, 3, 6)
FORECAST_ICON_SECONDS = 3.0
FORECAST_TEMPERATURE_SECONDS = 2.0
SLOT_DOT: Color = (255, 255, 255)


def draw_temperature(canvas: Canvas, degrees: float, slot: int, slots: int) -> bool:
    """
    Draw a temperature, fixed and centred on the bottom rows, and one dot
    per slot on the top row, the current slot bright.

    Args:
        canvas: The canvas to draw on.
        degrees: The temperature in °C.
        slot: Which forecast slot this is, 0 for now.
        slots: How many slots there are.

    Returns:
        False when the text is wider than the canvas and nothing was drawn.
    """
    columns = render_text(f"{round(degrees)}°")
    if len(columns) > canvas.width:
        return False
    canvas.clear()
    left = (canvas.width - len(columns)) // 2
    top = canvas.height - FONT_HEIGHT
    color = (120, 200, 255) if degrees < 10 else (255, 200, 60) if degrees < 25 else (255, 90, 40)
    for i, column in enumerate(columns):
        for y, lit in enumerate(column):
            if lit:
                canvas.set(left + i, top + y, color)
    if top > 0:
        start = (canvas.width - (2 * slots - 1)) // 2
        for i in range(slots):
            canvas.set(start + 2 * i, 0, SLOT_DOT if i == slot else scale(SLOT_DOT, 0.15))
    return True


class ForecastScene:
    """
    The weather now, in 3 hours and in 6 hours: for each, the animated
    icon and then the temperature, fixed in the middle, with dots on the
    top row that tell which one it is. ``done`` turns True after the
    three of them.
    """

    def __init__(self, feed: Feed[Weather], fps: float = 8) -> None:
        self.fps = fps
        self._feed = feed
        self.done = False

    def _slots(self, weather: Weather) -> list[tuple[int, float, bool]]:
        slots = [(weather.code, weather.temperature, weather.is_day)]
        for offset in FORECAST_OFFSETS[1:]:
            if offset < len(weather.forecast):
                hour = weather.forecast[offset]
                slots.append((hour.code, hour.temperature, hour.is_day))
        return slots

    def render(self, canvas: Canvas, frame: int) -> None:
        weather = self._feed.get()
        if weather is None:
            loading(canvas, frame, self.fps, failed=self._feed.error is not None)
            return
        slots = self._slots(weather)
        icon = int(FORECAST_ICON_SECONDS * self.fps)
        per_slot = icon + int(FORECAST_TEMPERATURE_SECONDS * self.fps)
        step = frame % (per_slot * len(slots))
        if frame >= per_slot * len(slots) - 1:
            self.done = True
        slot, within = divmod(step, per_slot)
        code, degrees, is_day = slots[slot]
        if within < icon or not draw_temperature(canvas, degrees, slot, len(slots)):
            draw_weather(canvas, weather_kind(code), is_day, frame, self.fps)
