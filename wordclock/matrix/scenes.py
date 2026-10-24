from __future__ import annotations

import socket
from collections.abc import Callable, Iterator
from colorsys import hsv_to_rgb
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from random import Random
from typing import Protocol

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.font import FONT_HEIGHT, render_text

logger = getLogger(__name__)

WHITE: Color = (255, 255, 255)
GREEN: Color = (0, 255, 70)


def hue_color(hue: float) -> Color:
    """
    Turn a hue into a fully saturated, full brightness colour.

    Args:
        hue: Hue from 0 to 1; values outside wrap around.

    Returns:
        The RGB colour.
    """
    r, g, b = hsv_to_rgb(hue % 1.0, 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))


class Scene(Protocol):
    """Anything that draws frames on a canvas."""

    fps: float

    def render(self, canvas: Canvas, frame: int) -> None:
        """
        Draw one frame.

        Args:
            canvas: The canvas to draw on. It still holds the previous frame.
            frame: Frame number, 0 for the first frame.
        """
        ...


class TextScene:
    """Text that scrolls from right to left, then starts again."""

    def __init__(
        self, text: str, color: Color = WHITE, fps: float = 8, rainbow: bool = False
    ) -> None:
        self.fps = fps
        self.color = color
        self.rainbow = rainbow
        self._columns = render_text(text)

    def loop_frames(self, width: int) -> int:
        """
        Count the frames of one pass, from entering on the right to leaving
        on the left.

        Args:
            width: Width of the canvas.

        Returns:
            The number of frames in one loop.
        """
        return len(self._columns) + width

    def _text(self) -> str | None:
        """Return new text to show on the next loop, or None to keep it."""
        return None

    def render(self, canvas: Canvas, frame: int) -> None:
        loop = len(self._columns) + canvas.width
        step = frame % loop
        if step == 0 and (text := self._text()) is not None:
            self._columns = render_text(text)
            loop = len(self._columns) + canvas.width
        top = (canvas.height - FONT_HEIGHT) // 2
        canvas.clear()
        for i, column in enumerate(self._columns):
            x = canvas.width - step + i
            color = hue_color(i / 30 + frame / 60) if self.rainbow else self.color
            for y, lit in enumerate(column):
                if lit:
                    canvas.set(x, top + y, color)


class ClockScene(TextScene):
    """The current time, ``HH:MM``, scrolling across the matrix."""

    def __init__(self, color: Color = WHITE, fps: float = 8, rainbow: bool = False) -> None:
        super().__init__(self._text(), color, fps, rainbow)

    def _text(self) -> str:
        return datetime.now().strftime("%H:%M")


def local_ip() -> str:
    """
    Find the address of this machine on the local network.

    Returns:
        The IPv4 address, or ``"NO IP"`` without a network.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            # Connecting a UDP socket sends nothing; it only picks a route.
            sock.connect(("192.0.2.1", 80))
            return sock.getsockname()[0]
        except OSError:
            return "NO IP"


class IpScene(TextScene):
    """The IP address of the Raspberry Pi, scrolling."""

    def __init__(self, color: Color = WHITE, fps: float = 8) -> None:
        super().__init__(self._text(), color, fps)

    def _text(self) -> str:
        return local_ip()


class RainScene:
    """Green drops that fall down the matrix and fade, like Matrix rain."""

    def __init__(
        self, color: Color = GREEN, fps: float = 12, density: float = 0.3, seed: int | None = None
    ) -> None:
        self.fps = fps
        self.color = color
        self.density = density
        self._random = Random(seed)
        self._drops: list[list[float]] = []

    def render(self, canvas: Canvas, frame: int) -> None:
        # Fade the previous frame to leave a trail behind every drop.
        for y in range(canvas.height):
            for x in range(canvas.width):
                r, g, b = canvas.get(x, y)
                canvas.set(x, y, (r * 6 // 10, g * 6 // 10, b * 6 // 10))
        if self._random.random() < self.density:
            speed = self._random.choice((0.5, 1.0))
            self._drops.append([float(self._random.randrange(canvas.width)), 0.0, speed])
        for drop in self._drops:
            x, y, speed = drop
            canvas.set(int(x), int(y), WHITE if speed == 1.0 else self.color)
            drop[1] += speed
        self._drops = [drop for drop in self._drops if drop[1] < canvas.height]


class RainbowScene:
    """A rainbow that slides diagonally across the matrix."""

    def __init__(self, fps: float = 20, speed: float = 0.01) -> None:
        self.fps = fps
        self.speed = speed

    def render(self, canvas: Canvas, frame: int) -> None:
        span = canvas.width + canvas.height
        for y in range(canvas.height):
            for x in range(canvas.width):
                canvas.set(x, y, hue_color((x + y) / span + frame * self.speed))


class SparkleScene:
    """Cells that light up in random colours and fade out, like fireflies."""

    def __init__(self, fps: float = 15, per_frame: int = 2, seed: int | None = None) -> None:
        self.fps = fps
        self.per_frame = per_frame
        self._random = Random(seed)

    def render(self, canvas: Canvas, frame: int) -> None:
        for y in range(canvas.height):
            for x in range(canvas.width):
                r, g, b = canvas.get(x, y)
                canvas.set(x, y, (r * 8 // 10, g * 8 // 10, b * 8 // 10))
        for _ in range(self.per_frame):
            x = self._random.randrange(canvas.width)
            y = self._random.randrange(canvas.height)
            canvas.set(x, y, hue_color(self._random.random()))


class WiringScene:
    """
    Light the cells one by one in canvas order, to check the wiring.

    A wrong snake shows up as a row that runs the wrong way; a bad joint
    stops the chain.
    """

    def __init__(self, color: Color = WHITE, fps: float = 6) -> None:
        self.fps = fps
        self.color = color

    def render(self, canvas: Canvas, frame: int) -> None:
        index = frame % (canvas.width * canvas.height)
        canvas.clear()
        canvas.set(index % canvas.width, index // canvas.width, self.color)


WEEKDAYS: tuple[str, ...] = (
    "DILLUNS",
    "DIMARTS",
    "DIMECRES",
    "DIJOUS",
    "DIVENDRES",
    "DISSABTE",
    "DIUMENGE",
)
MESSAGES: tuple[str, ...] = ("HOLA!", "SOMRIU!", "♥ ♥ ♥", "ENDAVANT!", "QUIN DIA MÉS BO!")
EFFECT_SECONDS = 15.0
FADE_SECONDS = 0.5


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
    Write the day as the Catalan weekday and the day of the month.

    Args:
        now: The date to write.

    Returns:
        For example ``DIVENDRES 24``.
    """
    return f"{WEEKDAYS[now.weekday()]} {now.day}"


@dataclass
class ShowItem:
    """One scene of the show and how long it plays."""

    scene: Scene
    seconds: float


class ShowScene:
    """
    Play the other scenes one after another, with new colours every time.

    The show starts with the IP address, then repeats forever: the clock, a
    text (a greeting, the date or a message) and an effect (rainbow, rain or
    sparkles). Texts play one full pass; effects play a fixed time. Each
    scene fades in and out.
    """

    def __init__(
        self,
        fps: float = 30,
        clock: Callable[[], datetime] = datetime.now,
        seed: int | None = None,
    ) -> None:
        self.fps = fps
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
        return self._random.choice(
            (greeting(now.hour), date_text(now), self._random.choice(MESSAGES))
        )

    def _effect(self) -> Scene:
        kind = self._random.choice(("rainbow", "rain", "sparkle"))
        if kind == "rainbow":
            return RainbowScene(speed=self._random.choice((0.005, 0.01, 0.02)))
        if kind == "rain":
            return RainScene(color=self._color(), seed=self._random.randrange(2**32))
        return SparkleScene(seed=self._random.randrange(2**32))

    def _playlist(self) -> Iterator[Callable[[], Scene]]:
        yield lambda: IpScene(color=self._color())
        while True:
            yield lambda: ClockScene(color=self._color(), rainbow=self._random.random() < 0.3)
            yield lambda: TextScene(
                self._text(), color=self._color(), rainbow=self._random.random() < 0.3
            )
            yield self._effect

    def _next_item(self, canvas: Canvas, frame: int) -> ShowItem:
        scene = next(self._items)()
        if isinstance(scene, TextScene):
            seconds = scene.loop_frames(canvas.width) / scene.fps
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


SCENE_NAMES: tuple[str, ...] = (
    "show",
    "text",
    "clock",
    "ip",
    "rain",
    "rainbow",
    "sparkle",
    "wiring",
)


def create_scene(name: str, text: str = "HOLA", color: Color | None = None) -> Scene:
    """
    Build a scene by name.

    Args:
        name: One of :data:`SCENE_NAMES`.
        text: Text for the ``text`` scene.
        color: Colour for the scenes that use one; None keeps their default.

    Returns:
        A new scene.

    Raises:
        ValueError: If the name is unknown.
    """
    extra = {"color": color} if color is not None else {}
    if name == "text":
        return TextScene(text, **extra)
    if name == "clock":
        return ClockScene(**extra)
    if name == "ip":
        return IpScene(**extra)
    if name == "rain":
        return RainScene(**extra)
    if name == "rainbow":
        return RainbowScene()
    if name == "sparkle":
        return SparkleScene()
    if name == "show":
        return ShowScene()
    if name == "wiring":
        return WiringScene(**extra)
    raise ValueError(f"Unknown scene {name!r}, expected one of: {', '.join(SCENE_NAMES)}")
