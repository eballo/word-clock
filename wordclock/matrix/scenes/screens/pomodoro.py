from __future__ import annotations

import math
import time
from collections.abc import Callable

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.colors import scale

WORK: Color = (255, 40, 20)
REST: Color = (0, 200, 80)
FLASH_SECONDS = 2.0


class PomodoroScene:
    """
    A pomodoro timer: 25 minutes of work, then 5 of rest, again and again.

    The cells empty as the time runs out, red for work and green for rest,
    and the last lit cell blinks. A press of the button pauses and resumes
    it; while paused, the cells breathe. The matrix flashes when a phase
    ends.
    """

    def __init__(
        self,
        work_minutes: float = 25,
        rest_minutes: float = 5,
        fps: float = 10,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.fps = fps
        self.lengths = {"work": work_minutes * 60, "rest": rest_minutes * 60}
        self._clock = clock
        self.phase = "work"
        self._started = clock()
        self._paused_at: float | None = None
        self._flash_until = 0.0

    @property
    def paused(self) -> bool:
        return self._paused_at is not None

    def on_press(self) -> None:
        """Pause, or resume where it was."""
        now = self._clock()
        if self._paused_at is None:
            self._paused_at = now
        else:
            self._started += now - self._paused_at
            self._paused_at = None

    def remaining(self) -> float:
        """
        Return the time left in this phase, moving to the next phase when
        it is over.

        Returns:
            Seconds left.
        """
        now = self._paused_at if self._paused_at is not None else self._clock()
        left = self.lengths[self.phase] - (now - self._started)
        if left <= 0:
            self.phase = "rest" if self.phase == "work" else "work"
            self._started = now
            self._flash_until = now + FLASH_SECONDS
            left = self.lengths[self.phase]
        return left

    def render(self, canvas: Canvas, frame: int) -> None:
        left = self.remaining()
        now = self._clock()
        color = WORK if self.phase == "work" else REST
        canvas.clear()
        if now < self._flash_until:
            if int(now * 4) % 2 == 0:
                canvas.fill(color)
            return
        cells = canvas.width * canvas.height
        lit = math.ceil(left / self.lengths[self.phase] * cells)
        level = 1.0
        if self.paused:
            level = 0.45 + 0.35 * math.sin(now * 2)
        for i in range(lit):
            shade = level
            if i == lit - 1 and not self.paused and int(now * 2) % 2:
                shade = 0.3
            canvas.set(i % canvas.width, i // canvas.width, scale(color, shade))
