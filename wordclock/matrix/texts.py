from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger

from wordclock.layouts.registry import Language

logger = getLogger(__name__)


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


TEXTS: dict[Language, Texts] = {
    Language.catalan: Texts(
        morning="BON DIA",
        afternoon="BONA TARDA",
        night="BONA NIT",
        weekdays=(
            "DILLUNS",
            "DIMARTS",
            "DIMECRES",
            "DIJOUS",
            "DIVENDRES",
            "DISSABTE",
            "DIUMENGE",
        ),
        months=(
            "GEN",
            "FEB",
            "MAR",
            "ABR",
            "MAI",
            "JUN",
            "JUL",
            "AGO",
            "SET",
            "OCT",
            "NOV",
            "DES",
        ),
        friday_tomorrow="DEMÀ ÉS DIVENDRES!",
        days_to_friday="FALTEN {days} DIES PER DIVENDRES",
        weekend="BON CAP DE SETMANA!",
        happy_day="BON {day}",
        lunch="HORA DE DINAR",
        dinner="HORA DE SOPAR",
        sleep="A DORMIR!",
        weather={
            "clear": "SOL",
            "cloudy": "NÚVOLS",
            "fog": "BOIRA",
            "drizzle": "PLUGIM",
            "rain": "PLUJA",
            "snow": "NEU",
            "storm": "TEMPESTA",
        },
    ),
    Language.english: Texts(
        morning="GOOD MORNING",
        afternoon="GOOD AFTERNOON",
        night="GOOD NIGHT",
        weekdays=(
            "MONDAY",
            "TUESDAY",
            "WEDNESDAY",
            "THURSDAY",
            "FRIDAY",
            "SATURDAY",
            "SUNDAY",
        ),
        months=(
            "JAN",
            "FEB",
            "MAR",
            "APR",
            "MAY",
            "JUN",
            "JUL",
            "AUG",
            "SEP",
            "OCT",
            "NOV",
            "DEC",
        ),
        friday_tomorrow="FRIDAY TOMORROW!",
        days_to_friday="{days} DAYS TO FRIDAY",
        weekend="HAPPY WEEKEND!",
        happy_day="HAPPY {day}",
        lunch="LUNCH TIME",
        dinner="DINNER TIME",
        sleep="BED TIME!",
        weather={
            "clear": "SUNNY",
            "cloudy": "CLOUDY",
            "fog": "FOG",
            "drizzle": "DRIZZLE",
            "rain": "RAIN",
            "snow": "SNOW",
            "storm": "STORM",
        },
    ),
    Language.spanish: Texts(
        morning="BUENOS DÍAS",
        afternoon="BUENAS TARDES",
        night="BUENAS NOCHES",
        weekdays=(
            "LUNES",
            "MARTES",
            "MIÉRCOLES",
            "JUEVES",
            "VIERNES",
            "SÁBADO",
            "DOMINGO",
        ),
        months=(
            "ENE",
            "FEB",
            "MAR",
            "ABR",
            "MAY",
            "JUN",
            "JUL",
            "AGO",
            "SEP",
            "OCT",
            "NOV",
            "DIC",
        ),
        friday_tomorrow="MAÑANA ES VIERNES!",
        days_to_friday="FALTAN {days} DÍAS PARA EL VIERNES",
        weekend="BUEN FIN DE SEMANA!",
        happy_day="FELIZ {day}",
        lunch="HORA DE COMER",
        dinner="HORA DE CENAR",
        sleep="A DORMIR!",
        weather={
            "clear": "SOL",
            "cloudy": "NUBES",
            "fog": "NIEBLA",
            "drizzle": "LLOVIZNA",
            "rain": "LLUVIA",
            "snow": "NIEVE",
            "storm": "TORMENTA",
        },
    ),
}


class Locale:
    """
    The language the scenes write in, shared by all of them and changed
    live from the remote control.
    """

    def __init__(self, language: Language = Language.catalan) -> None:
        self.language = language

    @property
    def texts(self) -> Texts:
        """The words of the current language."""
        return TEXTS[self.language]

    def set(self, language: Language) -> None:
        """
        Switch the language; the next text of every scene uses it.

        Args:
            language: The new language.
        """
        if language != self.language:
            logger.info("Language: %s", language.value)
        self.language = language
