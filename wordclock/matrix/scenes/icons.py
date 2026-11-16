from __future__ import annotations

from math import sin, tau

from wordclock.matrix.canvas import Canvas, Color

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
