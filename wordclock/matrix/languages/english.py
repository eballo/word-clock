from __future__ import annotations

from wordclock.matrix.languages.base import Texts

# Words of the matrix in English.
TEXTS = Texts(
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
)
