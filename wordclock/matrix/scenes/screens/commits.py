from __future__ import annotations

import math

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import add, scale
from wordclock.matrix.feeds import Feed, contribution_level
from wordclock.matrix.scenes.screens.loading import loading
from wordclock.matrix.scenes.text import TextScene

# GitHub greens, made brighter for LEDs, for levels 1 to 4.
LEVELS: tuple[Color, ...] = ((0, 0, 0), (0, 45, 12), (0, 100, 30), (0, 170, 50), (60, 255, 90))
HEATMAP_SECONDS = 8.0


class CommitsScene:
    """
    GitHub contributions of the last days, one cell per day in reading
    order, oldest top left and today bottom right, shaded like GitHub;
    today breathes. Then the total scrolls past.
    """

    def __init__(self, feed: Feed[list[int]], fps: float = 8) -> None:
        self.fps = fps
        self._feed = feed
        self._text = TextScene("", fps=fps)
        self._text_key: str | None = None

    def render(self, canvas: Canvas, frame: int) -> None:
        counts = self._feed.get()
        if counts is None:
            loading(canvas, frame, self.fps, failed=self._feed.error is not None)
            return
        cells = canvas.width * canvas.height
        days = counts[-cells:]
        words = f"{sum(days)} COMMITS"
        if words != self._text_key:
            self._text = TextScene(words, color=LEVELS[4], fps=self.fps)
            self._text_key = words
        heat_frames = int(HEATMAP_SECONDS * self.fps)
        step = frame % (heat_frames + self._text.loop_frames(canvas.width))
        if step >= heat_frames:
            self._text.render(canvas, step - heat_frames)
            return
        canvas.clear()
        offset = cells - len(days)
        for i, count in enumerate(days):
            color = LEVELS[contribution_level(count, days)]
            if i == len(days) - 1:
                breath = 0.5 + 0.5 * math.sin(frame / self.fps * 3)
                color = add(scale(color, breath), scale((255, 255, 255), 0.15 * breath))
            cell = offset + i
            canvas.set(cell % canvas.width, cell // canvas.width, color)
