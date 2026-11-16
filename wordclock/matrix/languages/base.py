from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Texts:
    """Every word the matrix shows, in one language."""

    # Greetings for the morning (06-13 h), the afternoon (13-20 h) and the
    # evening and night (20-06 h)
    morning: str
    afternoon: str
    night: str
    # Monday first
    weekdays: tuple[str, ...]
    # January first
    months: tuple[str, ...]
    friday_tomorrow: str
    # With a {days} field
    days_to_friday: str
    weekend: str
    # With a {day} field, for Saturday and Sunday
    happy_day: str
    lunch: str
    dinner: str
    sleep: str
    # One word for each weather kind of :data:`wordclock.matrix.feeds.WEATHER_KINDS`
    weather: dict[str, str]
