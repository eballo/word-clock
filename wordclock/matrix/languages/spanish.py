from __future__ import annotations

from wordclock.matrix.languages.base import Texts

# Words of the matrix in Spanish.
TEXTS = Texts(
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
)
