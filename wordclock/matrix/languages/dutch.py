from __future__ import annotations

from wordclock.matrix.languages.base import Texts

# Words of the matrix in Dutch.
TEXTS = Texts(
    morning="GOEDEMORGEN",
    afternoon="GOEDEMIDDAG",
    night="GOEDENAVOND",
    weekdays=(
        "MAANDAG",
        "DINSDAG",
        "WOENSDAG",
        "DONDERDAG",
        "VRIJDAG",
        "ZATERDAG",
        "ZONDAG",
    ),
    months=(
        "JAN",
        "FEB",
        "MRT",
        "APR",
        "MEI",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OKT",
        "NOV",
        "DEC",
    ),
    friday_tomorrow="MORGEN IS HET VRIJDAG!",
    days_to_friday="NOG {days} DAGEN TOT VRIJDAG",
    weekend="FIJN WEEKEND!",
    happy_day="FIJNE {day}",
    lunch="LUNCHTIJD",
    dinner="ETENSTIJD",
    sleep="BEDTIJD!",
    weather={
        "clear": "ZON",
        "cloudy": "BEWOLKT",
        "fog": "MIST",
        "drizzle": "MOTREGEN",
        "rain": "REGEN",
        "snow": "SNEEUW",
        "storm": "ONWEER",
    },
)
