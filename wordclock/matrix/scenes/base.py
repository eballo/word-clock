from __future__ import annotations

from typing import Protocol

from wordclock.matrix.canvas import Canvas


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
