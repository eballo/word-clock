from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import date, datetime
from logging import getLogger
from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import hue_color
from wordclock.matrix.dimmer import is_night
from wordclock.matrix.feeds import Feed, Weather
from wordclock.matrix.personal import Personal
from wordclock.matrix.scenes.base import Scene
from wordclock.matrix.scenes.clocks import CounterScene
from wordclock.matrix.scenes.effects.bounce import BounceScene
from wordclock.matrix.scenes.effects.fire import FireScene
from wordclock.matrix.scenes.effects.layers import LayersScene
from wordclock.matrix.scenes.effects.life import LifeScene
from wordclock.matrix.scenes.effects.maze import MazeScene
from wordclock.matrix.scenes.effects.rain import RainScene
from wordclock.matrix.scenes.effects.rainbow import RainbowScene, SpinScene
from wordclock.matrix.scenes.effects.snake import SnakeScene
from wordclock.matrix.scenes.effects.sparkle import SparkleScene
from wordclock.matrix.scenes.effects.stack import StackScene
from wordclock.matrix.scenes.effects.worms import WormsScene
from wordclock.matrix.scenes.icons import ICONS, RED, IconScene
from wordclock.matrix.scenes.screens.commits import CommitsScene
from wordclock.matrix.scenes.screens.weather import ForecastScene, WeatherScene
from wordclock.matrix.scenes.text import ClockScene, IpScene, TextScene
from wordclock.matrix.texts import Locale, day_texts

logger = getLogger(__name__)


# Every effect plays this long, so they all get the same time.
EFFECT_SECONDS = 150.0
ICON_SECONDS = 6.0
FADE_SECONDS = 0.5
# On a personal date, this share of the texts is the date's own text.
DATE_TEXT_SHARE = 0.5
# The clock plays for one minute at every multiple of this many minutes.
CLOCK_EVERY_MINUTES = 5
# The time scrolls past this many times before the counter.
CLOCK_PASSES = 2
# The counter runs a full minute and a little more, to show its first square.
COUNTER_SECONDS = 62.0

# Effects the show picks from, on top of the weather, the forecast and the
# commits when they are set up.
EFFECTS: tuple[str, ...] = (
    "rainbow",
    "spin",
    "rain",
    "sparkle",
    "fire",
    "layers",
    "bounce",
    "life",
    "worms",
    "snake",
    "maze",
    "stack",
)


@dataclass
class ShowItem:
    """One scene of the show and how long it plays; None for text passes."""

    scene: Scene
    seconds: float | None
    clock: bool = False
    # Text passes when ``seconds`` is None
    passes: int = 1


class ShowScene:
    """
    Play the other scenes one after another, with new colours every time.

    The show starts with the IP address, then repeats forever: two
    effects, a text, two effects and a drawing. Texts play one full pass,
    every effect the same time. Every 5 minutes, on the minute, the time
    cuts in: ``HH:MM`` scrolls past twice, then the counter runs a minute.
    Each scene fades in and out.
    """

    def __init__(
        self,
        personal: Personal | None = None,
        fps: float = 30,
        clock: Callable[[], datetime] = datetime.now,
        seed: int | None = None,
        weather: Feed[Weather] | None = None,
        commits: Feed[list[int]] | None = None,
        locale: Locale | None = None,
    ) -> None:
        self.fps = fps
        self.personal = personal or Personal()
        self.locale = locale or Locale()
        self.weather = weather
        self.commits = commits
        self._clock = clock
        self._random = Random(seed)
        self._items: Iterator[Callable[[], ShowItem]] = self._playlist()
        self._queue: list[ShowItem] = []
        self._last_effect: str | None = None
        self._clock_slot: tuple[date, int, int] | None = None
        self._inner: Canvas | None = None
        self._item: ShowItem | None = None
        self._start = 0
        self._inner_frame = -1

    def _color(self) -> Color:
        return hue_color(self._random.random())

    def _seed(self) -> int:
        return self._random.randrange(2**32)

    def _text(self) -> str:
        now = self._clock()
        special = self.personal.dates.get(now.strftime("%m-%d"), ())
        if special and self._random.random() < DATE_TEXT_SHARE:
            return self._random.choice(special)
        return self._random.choice(day_texts(now, self.locale.texts) + list(self.personal.messages))

    def effect_names(self) -> tuple[str, ...]:
        """
        List the effects the show can pick now.

        Returns:
            :data:`EFFECTS`, plus ``weather`` and ``forecast`` with a city
            and ``commits`` with a GitHub account.
        """
        names = EFFECTS
        if self.weather is not None:
            names += ("weather", "forecast")
        if self.commits is not None:
            names += ("commits",)
        return names

    def _build_effect(self, name: str) -> Scene:
        builders: dict[str, Callable[[], Scene]] = {
            "rainbow": lambda: RainbowScene(speed=self._random.choice((0.005, 0.01, 0.02))),
            "spin": lambda: SpinScene(turn_seconds=self._random.choice((8.0, 12.0, 16.0))),
            "rain": lambda: RainScene(color=self._color(), seed=self._seed()),
            "sparkle": lambda: SparkleScene(seed=self._seed()),
            "fire": lambda: FireScene(seed=self._seed()),
            "layers": lambda: LayersScene(seed=self._seed()),
            "bounce": lambda: BounceScene(seed=self._seed()),
            "life": lambda: LifeScene(seed=self._seed()),
            "worms": lambda: WormsScene(seed=self._seed()),
            "snake": lambda: SnakeScene(seed=self._seed()),
            "maze": lambda: MazeScene(seed=self._seed()),
            "stack": lambda: StackScene(seed=self._seed()),
        }
        if name == "weather" and self.weather is not None:
            return WeatherScene(self.weather, locale=self.locale)
        if name == "forecast" and self.weather is not None:
            return ForecastScene(self.weather)
        if name == "commits" and self.commits is not None:
            return CommitsScene(self.commits)
        return builders[name]()

    def _effect(self) -> ShowItem:
        names = self.effect_names()
        # Never the same effect twice in a row.
        name = self._random.choice([n for n in names if n != self._last_effect] or names)
        self._last_effect = name
        return ShowItem(self._build_effect(name), EFFECT_SECONDS)

    def _icon(self) -> ShowItem:
        if is_night(self._clock().hour):
            return ShowItem(IconScene(ICONS["zzz"], self._color()), ICON_SECONDS)
        name = self._random.choice(("heart", "smile"))
        color = RED if name == "heart" else self._color()
        return ShowItem(IconScene(ICONS[name], color), ICON_SECONDS)

    def _text_item(self) -> ShowItem:
        scene = TextScene(self._text(), color=self._color(), rainbow=self._random.random() < 0.3)
        return ShowItem(scene, None)

    def clock_items(self, now: datetime) -> list[ShowItem]:
        """
        Plan the time: ``HH:MM`` scrolling past, then the counter.

        Args:
            now: The current time.

        Returns:
            The scrolling time for :data:`CLOCK_PASSES` passes, then the
            counter for a full minute, so its first square lights up.
        """
        rainbow = self._random.random() < 0.3
        time = ClockScene(color=self._color(), rainbow=rainbow)
        return [
            ShowItem(time, None, clock=True, passes=CLOCK_PASSES),
            ShowItem(CounterScene(), COUNTER_SECONDS, clock=True),
        ]

    def _clock_due(self, now: datetime) -> bool:
        if now.minute % CLOCK_EVERY_MINUTES:
            return False
        return self._clock_slot != (now.date(), now.hour, now.minute)

    def _playlist(self) -> Iterator[Callable[[], ShowItem]]:
        yield lambda: ShowItem(IpScene(color=self._color()), None)
        while True:
            # Mostly effects: four of them for each text and drawing.
            yield from (self._effect, self._effect, self._text_item)
            yield from (self._effect, self._effect, self._icon)

    def _next_item(self, canvas: Canvas, frame: int) -> ShowItem:
        item = self._queue.pop(0) if self._queue else next(self._items)()
        if item.seconds is None and isinstance(item.scene, TextScene):
            item.seconds = item.passes * item.scene.loop_frames(canvas.width) / item.scene.fps
        logger.debug("Show: %s for %.1f s", type(item.scene).__name__, item.seconds or 0)
        self._start = frame
        self._inner_frame = -1
        canvas.clear()
        return item

    def render(self, canvas: Canvas, frame: int) -> None:
        if self._inner is None or (self._inner.width, self._inner.height) != (
            canvas.width,
            canvas.height,
        ):
            self._inner = Canvas(canvas.width, canvas.height)
        inner = self._inner
        now = self._clock()
        if self._clock_due(now) and not (self._item and self._item.clock):
            self._clock_slot = (now.date(), now.hour, now.minute)
            self._queue = self.clock_items(now)
            self._item = None
        if self._item is None or (frame - self._start) / self.fps >= (
            self._item.seconds or EFFECT_SECONDS
        ):
            self._item = self._next_item(inner, frame)
        item = self._item
        seconds = item.seconds or EFFECT_SECONDS
        elapsed = (frame - self._start) / self.fps
        # Each scene keeps its own pace: render only when its next frame is due.
        target = int(elapsed * item.scene.fps)
        while self._inner_frame < target:
            self._inner_frame += 1
            item.scene.render(inner, self._inner_frame)
        fade = max(0.0, min(1.0, elapsed / FADE_SECONDS, (seconds - elapsed) / FADE_SECONDS))
        for y, row in enumerate(inner.rows()):
            for x, (r, g, b) in enumerate(row):
                canvas.set(x, y, (int(r * fade), int(g * fade), int(b * fade)))
