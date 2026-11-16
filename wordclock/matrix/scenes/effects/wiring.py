from __future__ import annotations

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import WHITE


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
