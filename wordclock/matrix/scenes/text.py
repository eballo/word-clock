from __future__ import annotations

import socket
from datetime import datetime

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import WHITE, hue_color
from wordclock.matrix.font import FONT_HEIGHT, render_text


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
        # Sit the text on the bottom row.
        top = canvas.height - FONT_HEIGHT
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
