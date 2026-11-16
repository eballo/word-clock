from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import StrEnum
from logging import getLogger
from threading import Lock

from wordclock.config import (
    MATRIX_BRIGHTNESS_DAY,
    MATRIX_BRIGHTNESS_EVENING,
    MATRIX_BRIGHTNESS_NIGHT,
)
from wordclock.matrix.feeds import Feed, SunTimes

logger = getLogger(__name__)

# Used until the sun times arrive, or without a city.
DEFAULT_SUN = SunTimes(sunrise=time(8, 0), sunset=time(19, 0))
# A change of phase fades over this many minutes, so the eye hardly sees it.
RAMP_MINUTES = 30


def is_night(hour: int) -> bool:
    """
    Tell whether it is sleeping time.

    Args:
        hour: Hour of the day, 0 to 23.

    Returns:
        True from 23:00 to 06:59.
    """
    return hour >= 23 or hour < 7


class Phase(StrEnum):
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"


@dataclass(frozen=True)
class BrightnessLevels:
    """Strip brightness, 0-255, for each part of the day."""

    day: int = MATRIX_BRIGHTNESS_DAY
    evening: int = MATRIX_BRIGHTNESS_EVENING
    night: int = MATRIX_BRIGHTNESS_NIGHT

    def __post_init__(self) -> None:
        for phase in Phase:
            value = getattr(self, phase.value)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255:
                raise ValueError(f"Brightness {phase.value} must be 0-255, got {value!r}")

    def of(self, phase: Phase) -> int:
        """
        Give the brightness of a phase.

        Args:
            phase: Part of the day.

        Returns:
            The brightness, 0-255.
        """
        return getattr(self, phase.value)


def phase_at(moment: datetime, sun: SunTimes) -> Phase:
    """
    Tell which part of the day a moment falls in.

    Args:
        moment: Local date and time.
        sun: Today's sunrise and sunset.

    Returns:
        Day between sunrise and sunset, night from 23:00 to 06:59, and
        evening for the dark hours in between (after sunset, and before a
        late winter sunrise).
    """
    if sun.sunrise <= moment.time() < sun.sunset:
        return Phase.DAY
    if is_night(moment.hour):
        return Phase.NIGHT
    return Phase.EVENING


def ramped_level(moment: datetime, sun: SunTimes, levels: BrightnessLevels) -> int:
    """
    Brightness at a moment, fading in a straight line after each change.

    Args:
        moment: Local date and time.
        sun: Today's sunrise and sunset.
        levels: Brightness of each phase.

    Returns:
        The mean of the phase brightness over the last :data:`RAMP_MINUTES`.
    """
    minute = moment.replace(second=0, microsecond=0)
    samples = [
        levels.of(phase_at(minute - timedelta(minutes=back), sun)) for back in range(RAMP_MINUTES)
    ]
    return round(sum(samples) / len(samples))


class Dimmer:
    """
    Brightness that follows the time of day.

    A brightness set by hand holds until the next change of phase, then the
    automatic brightness takes over again.
    """

    def __init__(
        self,
        levels: BrightnessLevels,
        sun: Feed[SunTimes] | None = None,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.levels = levels
        self._sun = sun
        self._clock = clock
        self._lock = Lock()
        self._manual: int | None = None
        self._manual_phase: Phase | None = None
        self._cache: tuple[datetime, SunTimes, int] | None = None

    @property
    def manual(self) -> bool:
        """True while a brightness set by hand holds."""
        return self._manual is not None

    def sun_times(self) -> SunTimes:
        """
        Today's sunrise and sunset.

        Returns:
            The times from the feed, or :data:`DEFAULT_SUN` without one.
        """
        value = self._sun.get() if self._sun else None
        return value or DEFAULT_SUN

    def set_manual(self, brightness: int) -> None:
        """
        Hold a brightness until the next change of phase.

        Args:
            brightness: The brightness, 0-255.
        """
        phase = phase_at(self._clock(), self.sun_times())
        with self._lock:
            self._manual = brightness
            self._manual_phase = phase

    def brightness(self) -> int:
        """
        The brightness to use now.

        Returns:
            The brightness held by hand, or the automatic one, 0-255.
        """
        moment = self._clock()
        sun = self.sun_times()
        phase = phase_at(moment, sun)
        with self._lock:
            if self._manual is not None:
                if phase == self._manual_phase:
                    return self._manual
                logger.info("Brightness back to automatic for the %s", phase.value)
                self._manual = None
                self._manual_phase = None
            minute = moment.replace(second=0, microsecond=0)
            if self._cache and self._cache[:2] == (minute, sun):
                return self._cache[2]
            level = ramped_level(moment, sun, self.levels)
            self._cache = (minute, sun, level)
            return level
