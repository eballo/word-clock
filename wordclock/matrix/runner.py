from __future__ import annotations

import time
from logging import getLogger

from wordclock.led.controller import BaseLedController
from wordclock.matrix.canvas import Canvas, limit_current
from wordclock.matrix.scenes import Scene

logger = getLogger(__name__)

_ANSI_RESET = "\033[0m"
_ANSI_HIDE_CURSOR = "\033[?25l"
_ANSI_SHOW_CURSOR = "\033[?25h"


def preview_lines(canvas: Canvas) -> list[str]:
    """
    Draw the canvas for a terminal, two characters per cell in its colour.

    Args:
        canvas: The canvas to draw.

    Returns:
        One line of text per row, with ANSI true-colour codes.
    """
    lines = []
    for row in canvas.rows():
        cells = "".join(
            f"\033[38;2;{r};{g};{b}m██" if r or g or b else "\033[90m··" for r, g, b in row
        )
        lines.append(cells + _ANSI_RESET)
    return lines


class MatrixRunner:
    """Play a scene on the LED strip, frame by frame."""

    def __init__(
        self,
        canvas: Canvas,
        controller: BaseLedController,
        max_ma: float,
        snake: bool = True,
        preview: bool = False,
        rotate: bool = False,
        mirror: bool = False,
    ) -> None:
        self.canvas = canvas
        self.controller = controller
        self.max_ma = max_ma
        self.snake = snake
        self.preview = preview
        self.rotate = rotate
        self.mirror = mirror

    def show_frame(self) -> None:
        """Send the canvas to the strip, under the current limit."""
        colors = limit_current(
            self.canvas.to_strip(self.snake, self.rotate, self.mirror),
            self.max_ma,
            self.controller.brightness,
        )
        for index, (r, g, b) in enumerate(colors):
            self.controller.set_pixel(index, r, g, b)
        self.controller.show()
        if self.preview:
            lines = preview_lines(self.canvas)
            # Move the cursor back up so the next frame draws over this one.
            print("\n".join(lines) + f"\033[{len(lines)}A\r", end="", flush=True)

    def play(self, scene: Scene, seconds: float | None = None) -> None:
        """
        Play a scene until the time is up or the user presses Ctrl+C.

        Args:
            scene: The scene to play.
            seconds: How long to play it; None plays until interrupted.
        """
        frame_time = 1 / scene.fps
        start = time.monotonic()
        frame = 0
        logger.info("Playing %s at %.0f fps", type(scene).__name__, scene.fps)
        if self.preview:
            print(_ANSI_HIDE_CURSOR, end="")
        try:
            while seconds is None or frame * frame_time < seconds:
                scene.render(self.canvas, frame)
                self.show_frame()
                frame += 1
                time.sleep(max(0.0, start + frame * frame_time - time.monotonic()))
        except KeyboardInterrupt:
            pass
        finally:
            if self.preview:
                print("\n" * self.canvas.height + _ANSI_SHOW_CURSOR, end="")
            self.controller.clear()
