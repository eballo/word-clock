from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from logging import getLogger
from threading import Lock

from wordclock.matrix.button import ButtonAction
from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.photo import CountdownScene, PhotoScene
from wordclock.matrix.scenes import Scene

logger = getLogger(__name__)

COUNTDOWN_SECONDS = 3
# The flash after the countdown, while the photo is taken
FLASH_SECONDS = 0.4
PHOTO_SECONDS = 8.0


@dataclass
class Clip:
    """A scene playing at its own pace inside a faster loop."""

    scene: Scene
    start: int
    seconds: float | None = None
    canvas: Canvas | None = None
    _frame: int = field(default=-1, init=False)

    def render(self, canvas: Canvas, frame: int, fps: float) -> None:
        """
        Bring the scene up to date on the canvas.

        Args:
            canvas: The canvas the scene draws on.
            frame: Frame of the outer loop.
            fps: Frames per second of the outer loop.
        """
        target = int((frame - self.start) / fps * self.scene.fps)
        while self._frame < target:
            self._frame += 1
            self.scene.render(canvas, self._frame)

    def done(self, frame: int, fps: float) -> bool:
        """
        Tell whether the clip has played its time.

        Args:
            frame: Frame of the outer loop.
            fps: Frames per second of the outer loop.

        Returns:
            True once ``seconds`` have passed; never for an open-ended clip.
        """
        return self.seconds is not None and (frame - self.start) / fps >= self.seconds


class ControlledScene:
    """
    The scene the matrix plays, with the button and the camera on top.

    It plays a base scene and handles the button actions: the lights go off
    and on, a photo is taken after a countdown and shown for a while, and a
    long press asks for a shutdown. A base scene with an ``on_press`` method,
    such as the pomodoro, takes the short presses instead of the lights.
    The same object runs on the Raspberry Pi and in the web simulator; only
    the camera and the shutdown differ, and they come in as callbacks.
    """

    def __init__(
        self,
        base: Scene,
        capture: Callable[[], None] | None = None,
        shutdown: Callable[[], None] | None = None,
        fps: float = 30,
    ) -> None:
        self.fps = fps
        self.lights_on = True
        self._capture = capture
        self._shutdown = shutdown
        self._lock = Lock()
        self._frame = 0
        self._base = Clip(base, 0)
        self._overlay: Clip | None = None
        self._base_canvas: Canvas | None = None
        self._overlay_canvas: Canvas | None = None
        self._waiting_photo = False

    def set_base(self, scene: Scene) -> None:
        """
        Play another scene.

        Args:
            scene: The new base scene.
        """
        with self._lock:
            self._base = Clip(scene, self._frame)
            if self._base_canvas is not None:
                self._base_canvas.clear()

    def handle(self, action: ButtonAction) -> None:
        """
        Do what a button press asks for.

        Args:
            action: The action of the press.
        """
        logger.info("Button: %s", action)
        on_press = getattr(self._base.scene, "on_press", None)
        if action == ButtonAction.TOGGLE and self.lights_on and callable(on_press):
            on_press()
        elif action == ButtonAction.TOGGLE:
            self.lights_on = not self.lights_on
        elif action == ButtonAction.PHOTO:
            self.lights_on = True
            with self._lock:
                self._overlay = Clip(CountdownScene(COUNTDOWN_SECONDS), self._frame)
                self._waiting_photo = True
        elif action == ButtonAction.SHUTDOWN and self._shutdown is not None:
            self._shutdown()

    def show_photo(self, pixels: list[Color], width: int) -> None:
        """
        Show a pixelated photo for a while.

        Args:
            pixels: One colour per cell, row by row.
            width: Cells per row.
        """
        with self._lock:
            self._overlay = Clip(PhotoScene(pixels, width), self._frame, PHOTO_SECONDS)

    def render(self, canvas: Canvas, frame: int) -> None:
        with self._lock:
            self._frame = frame
            if self._base_canvas is None:
                self._base_canvas = Canvas(canvas.width, canvas.height)
                self._overlay_canvas = Canvas(canvas.width, canvas.height)
            self._base.render(self._base_canvas, frame, self.fps)
            overlay = self._overlay
            if overlay is not None:
                overlay.render(self._overlay_canvas, frame, self.fps)
                countdown_over = (frame - overlay.start) / self.fps >= COUNTDOWN_SECONDS
                if self._waiting_photo and countdown_over:
                    # Take the photo during the flash; it replaces the overlay
                    # when it arrives.
                    self._waiting_photo = False
                    overlay.seconds = COUNTDOWN_SECONDS + FLASH_SECONDS
                    if self._capture is not None:
                        self._capture()
                if overlay.done(frame, self.fps):
                    self._overlay = None
            source = self._overlay_canvas if self._overlay is not None else self._base_canvas
        if not self.lights_on:
            canvas.clear()
            return
        for y, row in enumerate(source.rows()):
            for x, color in enumerate(row):
                canvas.set(x, y, color)
