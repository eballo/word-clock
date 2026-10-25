from __future__ import annotations

import tomllib
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from logging import getLogger
from math import sin, tau
from pathlib import Path
from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.clocks import BlocksClock, DialClock, TixClock
from wordclock.matrix.scenes import (
    ClockScene,
    IpScene,
    RainbowScene,
    RainScene,
    Scene,
    SparkleScene,
    TextScene,
    hue_color,
)

logger = getLogger(__name__)

WEEKDAYS: tuple[str, ...] = (
    "DILLUNS",
    "DIMARTS",
    "DIMECRES",
    "DIJOUS",
    "DIVENDRES",
    "DISSABTE",
    "DIUMENGE",
)
MONTHS: tuple[str, ...] = (
    "GEN",
    "FEB",
    "MAR",
    "ABR",
    "MAI",
    "JUN",
    "JUL",
    "AGO",
    "SET",
    "OCT",
    "NOV",
    "DES",
)
EFFECT_SECONDS = 15.0
ICON_SECONDS = 6.0
FADE_SECONDS = 0.5
# On a personal date, this share of the texts is the date's own text.
DATE_TEXT_SHARE = 0.5
RED: Color = (255, 0, 40)

# 10 x 6 drawings, "X" for a lit cell.
ICONS: dict[str, tuple[str, ...]] = {
    "heart": (
        "..XX..XX..",
        ".XXXXXXXX.",
        ".XXXXXXXX.",
        "..XXXXXX..",
        "...XXXX...",
        "....XX....",
    ),
    "smile": (
        "..........",
        "...X..X...",
        "...X..X...",
        "..........",
        "..X....X..",
        "...XXXX...",
    ),
    "zzz": (
        "XXXX......",
        "..X.......",
        ".X....XXX.",
        "XXXX....X.",
        ".......X..",
        "......XXX.",
    ),
}


def is_night(hour: int) -> bool:
    """
    Tell whether it is sleeping time.

    Args:
        hour: Hour of the day, 0 to 23.

    Returns:
        True from 23:00 to 06:59.
    """
    return hour >= 23 or hour < 7


def greeting(hour: int) -> str:
    """
    Say hello in Catalan for the time of day.

    Args:
        hour: Hour of the day, 0 to 23.

    Returns:
        ``BON DIA``, ``BONA TARDA`` or ``BONA NIT``.
    """
    if 6 <= hour < 13:
        return "BON DIA"
    if 13 <= hour < 20:
        return "BONA TARDA"
    return "BONA NIT"


def date_text(now: datetime) -> str:
    """
    Write the day of the month and the short Catalan month.

    Args:
        now: The date to write.

    Returns:
        For example ``24 OCT``.
    """
    return f"{now.day} {MONTHS[now.month - 1]}"


def day_texts(now: datetime) -> list[str]:
    """
    List the texts that fit this moment: greeting, date, week and meals.

    Args:
        now: The current date and time.

    Returns:
        The texts to choose from, never empty.
    """
    weekday, hour = now.weekday(), now.hour
    texts = [greeting(hour), date_text(now)]
    if weekday <= 3:
        days = 4 - weekday
        texts.append("DEMÀ ÉS DIVENDRES!" if days == 1 else f"FALTEN {days} DIES PER DIVENDRES")
    elif weekday == 4 and hour >= 15:
        texts.append("BON CAP DE SETMANA!")
    elif weekday >= 5:
        texts.append(f"BON {WEEKDAYS[weekday]}")
    if 13 <= hour < 15:
        texts.append("HORA DE DINAR")
    elif 20 <= hour < 22:
        texts.append("HORA DE SOPAR")
    elif is_night(hour):
        texts.append("A DORMIR!")
    return texts


@dataclass(frozen=True)
class Personal:
    """Personal texts, kept out of the public repository."""

    messages: tuple[str, ...] = ()
    # Texts for one day of every year, keyed by "MM-DD".
    dates: dict[str, tuple[str, ...]] = field(default_factory=dict)


def _texts(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise ValueError(f"Expected a text or a list of texts, got {value!r}")


def load_personal(path: Path) -> Personal:
    """
    Read the personal texts from a TOML file.

    The file has a ``messages`` list and a ``[dates]`` table that maps
    ``"MM-DD"`` to a text or a list of texts. A missing or broken file
    gives no personal texts, so the show still runs.

    Args:
        path: The TOML file.

    Returns:
        The personal texts.
    """
    if not path.is_file():
        logger.info("No personal texts at %s", path)
        return Personal()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        messages = _texts(data.get("messages", []))
        dates = {str(day): _texts(texts) for day, texts in data.get("dates", {}).items()}
    except (tomllib.TOMLDecodeError, ValueError, AttributeError) as exc:
        logger.warning("Ignoring personal texts in %s: %s", path, exc)
        return Personal()
    logger.info("Loaded %d messages and %d dates from %s", len(messages), len(dates), path)
    return Personal(messages, dates)


class IconScene:
    """A still 10 x 6 drawing, centred, that pulses like a heartbeat."""

    def __init__(self, pixels: tuple[str, ...], color: Color, fps: float = 20) -> None:
        self.fps = fps
        self.color = color
        self.pixels = pixels

    def render(self, canvas: Canvas, frame: int) -> None:
        level = 0.7 + 0.3 * sin(tau * frame / (1.5 * self.fps))
        color = (
            int(self.color[0] * level),
            int(self.color[1] * level),
            int(self.color[2] * level),
        )
        left = (canvas.width - len(self.pixels[0])) // 2
        top = (canvas.height - len(self.pixels)) // 2
        canvas.clear()
        for y, row in enumerate(self.pixels):
            for x, cell in enumerate(row):
                if cell == "X":
                    canvas.set(left + x, top + y, color)


@dataclass
class ShowItem:
    """One scene of the show and how long it plays."""

    scene: Scene
    seconds: float


class ShowScene:
    """
    Play the other scenes one after another, with new colours every time.

    The show starts with the IP address, then repeats forever: a clock (the
    scrolling time, blocks, dial or TIX), a text, an effect (rainbow, rain or
    sparkles), a clock, a text and a drawing. Texts play one full pass;
    the other scenes play a fixed time. Each scene fades in and out.
    """

    def __init__(
        self,
        personal: Personal | None = None,
        fps: float = 30,
        clock: Callable[[], datetime] = datetime.now,
        seed: int | None = None,
    ) -> None:
        self.fps = fps
        self.personal = personal or Personal()
        self._clock = clock
        self._random = Random(seed)
        self._items: Iterator[Callable[[], Scene]] = self._playlist()
        self._inner: Canvas | None = None
        self._item: ShowItem | None = None
        self._start = 0
        self._inner_frame = -1

    def _color(self) -> Color:
        return hue_color(self._random.random())

    def _text(self) -> str:
        now = self._clock()
        special = self.personal.dates.get(now.strftime("%m-%d"), ())
        if special and self._random.random() < DATE_TEXT_SHARE:
            return self._random.choice(special)
        return self._random.choice(day_texts(now) + list(self.personal.messages))

    def _effect(self) -> Scene:
        kind = self._random.choice(("rainbow", "rain", "sparkle"))
        if kind == "rainbow":
            return RainbowScene(speed=self._random.choice((0.005, 0.01, 0.02)))
        if kind == "rain":
            return RainScene(color=self._color(), seed=self._random.randrange(2**32))
        return SparkleScene(seed=self._random.randrange(2**32))

    def _icon(self) -> Scene:
        if is_night(self._clock().hour):
            return IconScene(ICONS["zzz"], self._color())
        name = self._random.choice(("heart", "smile"))
        return IconScene(ICONS[name], RED if name == "heart" else self._color())

    def _clock_scene(self) -> Scene:
        kind = self._random.choice(("text", "blocks", "dial", "tix"))
        if kind == "blocks":
            return BlocksClock(clock=self._clock)
        if kind == "dial":
            return DialClock(clock=self._clock)
        if kind == "tix":
            return TixClock(clock=self._clock)
        return ClockScene(color=self._color(), rainbow=self._random.random() < 0.3)

    def _text_scene(self) -> Scene:
        return TextScene(self._text(), color=self._color(), rainbow=self._random.random() < 0.3)

    def _playlist(self) -> Iterator[Callable[[], Scene]]:
        yield lambda: IpScene(color=self._color())
        while True:
            yield from (self._clock_scene, self._text_scene, self._effect)
            yield from (self._clock_scene, self._text_scene, self._icon)

    def _next_item(self, canvas: Canvas, frame: int) -> ShowItem:
        scene = next(self._items)()
        if isinstance(scene, TextScene):
            seconds = scene.loop_frames(canvas.width) / scene.fps
        elif isinstance(scene, IconScene):
            seconds = ICON_SECONDS
        else:
            seconds = EFFECT_SECONDS
        logger.debug("Show: %s for %.1f s", type(scene).__name__, seconds)
        self._start = frame
        self._inner_frame = -1
        canvas.clear()
        return ShowItem(scene, seconds)

    def render(self, canvas: Canvas, frame: int) -> None:
        if self._inner is None or (self._inner.width, self._inner.height) != (
            canvas.width,
            canvas.height,
        ):
            self._inner = Canvas(canvas.width, canvas.height)
        inner = self._inner
        if self._item is None or (frame - self._start) / self.fps >= self._item.seconds:
            self._item = self._next_item(inner, frame)
        item = self._item
        elapsed = (frame - self._start) / self.fps
        # Each scene keeps its own pace: render only when its next frame is due.
        target = int(elapsed * item.scene.fps)
        while self._inner_frame < target:
            self._inner_frame += 1
            item.scene.render(inner, self._inner_frame)
        fade = max(0.0, min(1.0, elapsed / FADE_SECONDS, (item.seconds - elapsed) / FADE_SECONDS))
        for y, row in enumerate(inner.rows()):
            for x, (r, g, b) in enumerate(row):
                canvas.set(x, y, (int(r * fade), int(g * fade), int(b * fade)))
