from __future__ import annotations

from wordclock.matrix.languages.base import Texts

# Words of the matrix in Catalan.
TEXTS = Texts(
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
)
