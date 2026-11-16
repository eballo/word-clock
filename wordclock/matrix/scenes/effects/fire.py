from __future__ import annotations

from random import Random

from wordclock.matrix.canvas import Canvas, Color

# Colours of the flames, from cold to hot.
PALETTE: tuple[Color, ...] = (
    (0, 0, 0),
    (90, 0, 0),
    (200, 20, 0),
    (255, 80, 0),
    (255, 160, 0),
    (255, 230, 90),
)


def heat_color(heat: float) -> Color:
    """
    Colour of a flame at some heat.

    Args:
        heat: 0 for cold, 1 for the hottest.

    Returns:
        The colour, blended between the two nearest of :data:`PALETTE`.
    """
    position = max(0.0, min(1.0, heat)) * (len(PALETTE) - 1)
    low = int(position)
    high = min(low + 1, len(PALETTE) - 1)
    mix = position - low
    return tuple(  # type: ignore[return-value]
        round(a + (b - a) * mix) for a, b in zip(PALETTE[low], PALETTE[high], strict=True)
    )


class FireScene:
    """
    Flames over the whole bottom row: the heat rises, drifts sideways and
    cools, so every column flickers in a gradient from yellow to dark red.
    """

    def __init__(self, fps: float = 15, seed: int | None = None) -> None:
        self.fps = fps
        self._random = Random(seed)
        self._heat: list[list[float]] = []

    def render(self, canvas: Canvas, frame: int) -> None:
        width, height = canvas.width, canvas.height
        if len(self._heat) != height or len(self._heat[0]) != width:
            self._heat = [[0.0] * width for _ in range(height)]
        old = self._heat
        new = [[0.0] * width for _ in range(height)]
        new[height - 1] = [0.75 + 0.25 * self._random.random() for _ in range(width)]
        # Taller matrices need slower cooling for the flames to reach as high.
        cooling = 1.6 / height
        for y in range(height - 1):
            for x in range(width):
                source = min(width - 1, max(0, x + self._random.choice((-1, 0, 0, 1))))
                below = old[y + 1][source]
                new[y][x] = max(0.0, below - cooling * (0.4 + 1.2 * self._random.random()))
        self._heat = new
        for y in range(height):
            for x in range(width):
                canvas.set(x, y, heat_color(new[y][x]))
