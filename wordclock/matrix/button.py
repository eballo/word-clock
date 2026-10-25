from __future__ import annotations

import time
from collections.abc import Callable
from enum import StrEnum

# How long the button is held for each action, in seconds.
PHOTO_SECONDS = 3.0
SHUTDOWN_SECONDS = 10.0


class ButtonAction(StrEnum):
    """What one press of the button does, by how long it is held."""

    NONE = "none"
    TOGGLE = "toggle"
    PHOTO = "photo"
    SHUTDOWN = "shutdown"


def action_for(held: float) -> ButtonAction:
    """
    Pick the action for a press.

    Args:
        held: How long the button was held, in seconds.

    Returns:
        Toggle the lights for a short press, take a photo from 3 s, shut
        down from 10 s.
    """
    if held >= SHUTDOWN_SECONDS:
        return ButtonAction.SHUTDOWN
    if held >= PHOTO_SECONDS:
        return ButtonAction.PHOTO
    return ButtonAction.TOGGLE


class ButtonHandler:
    """Time a press of the button, from the real switch or the simulator."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._down_at: float | None = None

    def held(self) -> float:
        """
        Return how long the button has been held so far.

        Returns:
            Seconds since the press, or 0 when it is up.
        """
        return 0.0 if self._down_at is None else self._clock() - self._down_at

    def press(self) -> None:
        """Note the moment the button goes down."""
        if self._down_at is None:
            self._down_at = self._clock()

    def release(self) -> ButtonAction:
        """
        Note the moment the button comes up.

        Returns:
            The action for the press, or NONE when it was not down.
        """
        if self._down_at is None:
            return ButtonAction.NONE
        held = self.held()
        self._down_at = None
        return action_for(held)
