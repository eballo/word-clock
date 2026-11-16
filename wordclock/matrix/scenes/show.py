from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from random import Random

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import hue_color
from wordclock.matrix.dimmer import is_night
from wordclock.matrix.feeds import Feed, Weather
from wordclock.matrix.personal import Personal
from wordclock.matrix.scenes.base import Scene
from wordclock.matrix.scenes.clocks import BlocksClock, DialClock, TixClock
from wordclock.matrix.scenes.effects.life import LifeScene
from wordclock.matrix.scenes.effects.rain import RainScene
from wordclock.matrix.scenes.effects.rainbow import RainbowScene
from wordclock.matrix.scenes.effects.sparkle import SparkleScene
from wordclock.matrix.scenes.icons import ICONS, RED, IconScene
from wordclock.matrix.scenes.screens.commits import CommitsScene
from wordclock.matrix.scenes.screens.weather import WeatherScene
from wordclock.matrix.scenes.text import ClockScene, IpScene, TextScene
from wordclock.matrix.texts import Locale, day_texts

logger = getLogger(__name__)


EFFECT_SECONDS = 15.0
ICON_SECONDS = 6.0
FADE_SECONDS = 0.5
# On a personal date, this share of the texts is the date's own text.
DATE_TEXT_SHARE = 0.5


@dataclass
class ShowItem:
    """One scene of the show and how long it plays."""

    scene: Scene
    seconds: float


class ShowScene:
    """
    Play the other scenes one after another, with new colours every time.

    The show starts with the IP address, then repeats forever: a clock (the
    scrolling time, blocks, dial or TIX), a text, an effect (rainbow, rain,
    sparkles, the Game of Life, and the weather and the commits when they
    are set up), a clock, a text and a drawing. Texts play one full pass;
    the other scenes play a fixed time. Each scene fades in and out.
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
        return self._random.choice(day_texts(now, self.locale.texts) + list(self.personal.messages))

    def _effect(self) -> Scene:
        kinds = ["rainbow", "rain", "sparkle", "life"]
        if self.weather is not None:
            kinds.append("weather")
        if self.commits is not None:
            kinds.append("commits")
        kind = self._random.choice(kinds)
        if kind == "weather" and self.weather is not None:
            return WeatherScene(self.weather, locale=self.locale)
        if kind == "commits" and self.commits is not None:
            return CommitsScene(self.commits)
        if kind == "life":
            return LifeScene(seed=self._random.randrange(2**32))
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
