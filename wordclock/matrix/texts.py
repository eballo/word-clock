from __future__ import annotations

from datetime import datetime
from logging import getLogger

from wordclock.matrix.dimmer import is_night
from wordclock.matrix.languages import TEXTS, MatrixLanguage, Texts

logger = getLogger(__name__)

__all__ = [
    "TEXTS",
    "Locale",
    "MatrixLanguage",
    "Texts",
    "date_text",
    "day_texts",
    "greeting",
]


class Locale:
    """
    The language the scenes write in, shared by all of them and changed
    live from the remote control.
    """

    def __init__(self, language: MatrixLanguage = MatrixLanguage.catalan) -> None:
        self.language = language

    @property
    def texts(self) -> Texts:
        """The words of the current language."""
        return TEXTS[self.language]

    def set(self, language: MatrixLanguage) -> None:
        """
        Switch the language; the next text of every scene uses it.

        Args:
            language: The new language.
        """
        if language != self.language:
            logger.info("Language: %s", language.value)
        self.language = language


def greeting(hour: int, texts: Texts = TEXTS[MatrixLanguage.catalan]) -> str:
    """
    Say hello for the time of day.

    Args:
        hour: Hour of the day, 0 to 23.
        texts: The words of one language.

    Returns:
        The morning, afternoon or night greeting, e.g. ``BON DIA``.
    """
    if 6 <= hour < 13:
        return texts.morning
    if 13 <= hour < 20:
        return texts.afternoon
    return texts.night


def date_text(now: datetime, texts: Texts = TEXTS[MatrixLanguage.catalan]) -> str:
    """
    Write the day of the month and the short month.

    Args:
        now: The date to write.
        texts: The words of one language.

    Returns:
        For example ``24 OCT``.
    """
    return f"{now.day} {texts.months[now.month - 1]}"


def day_texts(now: datetime, texts: Texts = TEXTS[MatrixLanguage.catalan]) -> list[str]:
    """
    List the texts that fit this moment: greeting, date, week and meals.

    Args:
        now: The current date and time.
        texts: The words of one language.

    Returns:
        The texts to choose from, never empty.
    """
    weekday, hour = now.weekday(), now.hour
    found = [greeting(hour, texts), date_text(now, texts)]
    if weekday <= 3:
        days = 4 - weekday
        found.append(texts.friday_tomorrow if days == 1 else texts.days_to_friday.format(days=days))
    elif weekday == 4 and hour >= 15:
        found.append(texts.weekend)
    elif weekday >= 5:
        found.append(texts.happy_day.format(day=texts.weekdays[weekday]))
    if 13 <= hour < 15:
        found.append(texts.lunch)
    elif 20 <= hour < 22:
        found.append(texts.dinner)
    elif is_night(hour):
        found.append(texts.sleep)
    return found
