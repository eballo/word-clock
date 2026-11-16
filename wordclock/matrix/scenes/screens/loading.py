from __future__ import annotations

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.colors import scale


def loading(canvas: Canvas, frame: int, fps: float, failed: bool = False) -> None:
    """
    Draw three dots that wait for data, red when the last fetch failed.

    Args:
        canvas: The canvas to draw on.
        frame: Frame number, for the animation.
        fps: Frames per second.
        failed: The last fetch failed.
    """
    canvas.clear()
    color = (255, 40, 20) if failed else (120, 120, 120)
    y = canvas.height // 2
    lit = int(frame / fps * 3) % 4
    for i in range(3):
        x = canvas.width // 2 - 2 + i * 2
        canvas.set(x, y, color if i < lit else scale(color, 0.2))
