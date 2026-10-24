from __future__ import annotations

import socket
from colorsys import hsv_to_rgb
from datetime import datetime
from random import Random
from typing import Protocol

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.font import FONT_HEIGHT, render_text

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
        # The show plays the other scenes, so it lives in its own module.
        from wordclock.matrix.show import ShowScene

        return ShowScene()
    if name == "wiring":
        return WiringScene(**extra)
    raise ValueError(f"Unknown scene {name!r}, expected one of: {', '.join(SCENE_NAMES)}")
