from __future__ import annotations

import pytest

from wordclock.layouts.registry import SUPPORTED_LANGUAGES, get_layout


class TestGetLayout:
    def test_returns_english_layout(self) -> None:
        # Given
        lang = "english"
        # When
        layout = get_layout(lang)
        # Then: module exposes required attributes
        assert hasattr(layout, "GRID_RAW")
        assert hasattr(layout, "NUM_ROWS")
        assert hasattr(layout, "NUM_COLS")
        assert hasattr(layout, "get_leds_for_time")

    def test_returns_catalan_layout(self) -> None:
        # Given
        lang = "catalan"
        # When
        layout = get_layout(lang)
        # Then
        assert hasattr(layout, "GRID_RAW")
        assert hasattr(layout, "get_leds_for_time")

    def test_returns_spanish_layout(self) -> None:
        # Given
        lang = "spanish"
        # When
        layout = get_layout(lang)
        # Then
        assert hasattr(layout, "GRID_RAW")
        assert hasattr(layout, "get_leds_for_time")

    def test_unknown_language_raises_value_error(self) -> None:
        # Given: a language that does not exist
        lang = "klingon"
        # When / Then
        with pytest.raises(ValueError, match="klingon"):
            get_layout(lang)

    def test_all_supported_languages_resolve(self) -> None:
        # Given: every language in SUPPORTED_LANGUAGES
        # When / Then: none raise
        for lang in SUPPORTED_LANGUAGES:
            layout = get_layout(lang)
            assert layout is not None
