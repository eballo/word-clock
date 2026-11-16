from __future__ import annotations

from datetime import datetime

import pytest

from wordclock.layouts.registry import Language
from wordclock.matrix.feeds import WEATHER_KINDS
from wordclock.matrix.show import date_text, day_texts, greeting
from wordclock.matrix.texts import TEXTS, Locale


class TestTexts:
    def test_every_language_has_texts(self) -> None:
        # Given / When / Then
        assert set(TEXTS) == set(Language)

    @pytest.mark.parametrize("language", list(Language))
    def test_complete_lists(self, language: Language) -> None:
        # Given
        texts = TEXTS[language]
        # When / Then
        assert len(texts.weekdays) == 7
        assert len(texts.months) == 12
        assert set(texts.weather) == {kind for kind, _ in WEATHER_KINDS}

    @pytest.mark.parametrize(
        ("language", "expected"),
        [
            (Language.catalan, "FALTEN 3 DIES PER DIVENDRES"),
            (Language.english, "3 DAYS TO FRIDAY"),
            (Language.spanish, "FALTAN 3 DÍAS PARA EL VIERNES"),
        ],
    )
    def test_counts_the_days_to_friday(self, language: Language, expected: str) -> None:
        # Given: Tuesday 20 October 2026
        now = datetime(2026, 10, 20, 10)
        # When
        texts = day_texts(now, TEXTS[language])
        # Then
        assert expected in texts

    @pytest.mark.parametrize(
        ("language", "hour", "expected"),
        [
            (Language.english, 8, "GOOD MORNING"),
            (Language.english, 21, "GOOD NIGHT"),
            (Language.spanish, 14, "BUENAS TARDES"),
        ],
    )
    def test_greets_in_each_language(self, language: Language, hour: int, expected: str) -> None:
        # Given / When / Then
        assert greeting(hour, TEXTS[language]) == expected

    def test_date_uses_the_short_month_of_the_language(self) -> None:
        # Given
        now = datetime(2026, 12, 24)
        # When / Then
        assert date_text(now, TEXTS[Language.english]) == "24 DEC"
        assert date_text(now, TEXTS[Language.spanish]) == "24 DIC"


class TestLocale:
    def test_catalan_by_default(self) -> None:
        # Given / When / Then
        assert Locale().texts == TEXTS[Language.catalan]

    def test_switches_live(self) -> None:
        # Given
        locale = Locale()
        # When
        locale.set(Language.english)
        # Then
        assert locale.language == Language.english
        assert locale.texts.morning == "GOOD MORNING"
