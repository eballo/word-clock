from __future__ import annotations

from datetime import datetime
from importlib import import_module

import pytest

from wordclock.matrix.feeds import WEATHER_KINDS
from wordclock.matrix.languages import MatrixLanguage
from wordclock.matrix.show import date_text, day_texts, greeting
from wordclock.matrix.texts import TEXTS, Locale


class TestTexts:
    def test_every_language_has_texts(self) -> None:
        # Given / When / Then
        assert set(TEXTS) == set(MatrixLanguage)

    @pytest.mark.parametrize("language", list(MatrixLanguage))
    def test_complete_lists(self, language: MatrixLanguage) -> None:
        # Given
        texts = TEXTS[language]
        # When / Then
        assert len(texts.weekdays) == 7
        assert len(texts.months) == 12
        assert set(texts.weather) == {kind for kind, _ in WEATHER_KINDS}

    @pytest.mark.parametrize(
        ("language", "expected"),
        [
            (MatrixLanguage.catalan, "FALTEN 3 DIES PER DIVENDRES"),
            (MatrixLanguage.english, "3 DAYS TO FRIDAY"),
            (MatrixLanguage.spanish, "FALTAN 3 DÍAS PARA EL VIERNES"),
            (MatrixLanguage.dutch, "NOG 3 DAGEN TOT VRIJDAG"),
        ],
    )
    def test_counts_the_days_to_friday(self, language: MatrixLanguage, expected: str) -> None:
        # Given: Tuesday 20 October 2026
        now = datetime(2026, 10, 20, 10)
        # When
        texts = day_texts(now, TEXTS[language])
        # Then
        assert expected in texts

    @pytest.mark.parametrize(
        ("language", "hour", "expected"),
        [
            (MatrixLanguage.english, 8, "GOOD MORNING"),
            (MatrixLanguage.english, 21, "GOOD NIGHT"),
            (MatrixLanguage.spanish, 14, "BUENAS TARDES"),
            (MatrixLanguage.dutch, 8, "GOEDEMORGEN"),
        ],
    )
    def test_greets_in_each_language(
        self, language: MatrixLanguage, hour: int, expected: str
    ) -> None:
        # Given / When / Then
        assert greeting(hour, TEXTS[language]) == expected

    def test_date_uses_the_short_month_of_the_language(self) -> None:
        # Given
        now = datetime(2026, 12, 24)
        # When / Then
        assert date_text(now, TEXTS[MatrixLanguage.english]) == "24 DEC"
        assert date_text(now, TEXTS[MatrixLanguage.spanish]) == "24 DIC"
        assert date_text(now, TEXTS[MatrixLanguage.dutch]) == "24 DEC"

    def test_dutch_weekend(self) -> None:
        # Given: Saturday 24 October 2026
        now = datetime(2026, 10, 24, 10)
        # When
        texts = day_texts(now, TEXTS[MatrixLanguage.dutch])
        # Then
        assert "FIJNE ZATERDAG" in texts


class TestLocale:
    def test_catalan_by_default(self) -> None:
        # Given / When / Then
        assert Locale().texts == TEXTS[MatrixLanguage.catalan]

    def test_switches_live(self) -> None:
        # Given
        locale = Locale()
        # When
        locale.set(MatrixLanguage.english)
        # Then
        assert locale.language == MatrixLanguage.english
        assert locale.texts.morning == "GOOD MORNING"


class TestLanguageModules:
    @pytest.mark.parametrize("language", list(MatrixLanguage))
    def test_one_module_per_language(self, language: MatrixLanguage) -> None:
        # Given
        module = import_module(f"wordclock.matrix.languages.{language.value}")
        # When / Then
        assert module.TEXTS is TEXTS[language]
