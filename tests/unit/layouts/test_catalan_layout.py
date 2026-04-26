from __future__ import annotations

import wordclock.layouts.catalan as _mod
from tests.unit.layouts.layout_test_mixin import (
    AllTimesMixin,
    GetLedsForTimeMixin,
    SentenceToCoordsMixin,
)
from wordclock.layouts.catalan import (
    NUM_COLS,
    NUM_ROWS,
    sentence_to_coords,
    time_to_sentence,
)


class TestTimeToSentence(AllTimesMixin):
    mod = _mod

    def test_en_punt_singular(self) -> None:
        # Given: hour 1 uses singular verb and article
        hours, minutes = 1, 0
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert result == "ÉS LA UNA EN PUNT"

    def test_en_punt_plural(self) -> None:
        # Given: hour 2+ uses plural verb and article
        hours, minutes = 2, 0
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert result == "SÓN LES DUES EN PUNT"

    def test_vora_singular(self) -> None:
        # Given: ~5 past hour 1 → singular
        hours, minutes = 1, 5
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "ÉS" in result
        assert "VORA" in result
        assert "LA" in result

    def test_vora_plural(self) -> None:
        # Given: ~5 past any hour other than 1
        hours, minutes = 3, 5
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "SÓN" in result
        assert "VORA" in result
        assert "LES" in result

    def test_un_quart_with_de(self) -> None:
        # Given: next hour uses "DE" preposition
        hours, minutes = 9, 15  # next hour = 10 (DEU) → DE
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "UN QUART" in result
        assert "DE" in result
        assert "DEU" in result

    def test_un_quart_with_apostrophe(self) -> None:
        # Given: next hour is ONZE → D'
        hours, minutes = 10, 15
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "UN QUART" in result
        assert "D'" in result
        assert "ONZE" in result

    def test_un_quart_next_hour_una_apostrophe(self) -> None:
        # Given: next hour is UNA → D'
        hours, minutes = 0, 15
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "D'" in result
        assert "UNA" in result

    def test_dos_quarts(self) -> None:
        # Given
        hours, minutes = 3, 30
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "DOS QUARTS" in result

    def test_dos_quarts_menys_cinc(self) -> None:
        # Given
        hours, minutes = 11, 25
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "DOS QUARTS" in result
        assert "MENYS CINC" in result

    def test_tres_quarts(self) -> None:
        # Given
        hours, minutes = 4, 45
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TRES QUARTS" in result

    def test_tres_quarts_menys_cinc(self) -> None:
        # Given
        hours, minutes = 4, 40
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TRES QUARTS" in result
        assert "MENYS CINC" in result

    def test_vora_next_hour_singular(self) -> None:
        # Given: ~55 past and next hour is 1 → LA
        hours, minutes = 0, 55
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "VORA" in result
        assert "LA" in result
        assert "UNA" in result

    def test_vora_next_hour_plural(self) -> None:
        # Given: ~55 past and next hour is not 1 → LES
        hours, minutes = 10, 55
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "VORA" in result
        assert "LES" in result
        assert "ONZE" in result

    def test_24h_hour_wraps_correctly(self) -> None:
        # Given: hour 13 should behave like hour 1
        hours, minutes = 13, 0
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert result == "ÉS LA UNA EN PUNT"


class TestSentenceToCoords(SentenceToCoordsMixin):
    mod = _mod
    sample_sentence = "SÓN DOS QUARTS DE DEU"

    def test_apostrophe_sentence_resolves_coords(self) -> None:
        # Given: sentence with D' preposition that must be split before searching
        sentence = "ÉS UN QUART D' ONZE"
        # When
        coords = sentence_to_coords(sentence)
        # Then: coords are non-empty and in range
        assert len(coords) > 0
        for row, col in coords:
            assert 0 <= row < NUM_ROWS
            assert 0 <= col < NUM_COLS


class TestGetLedsForTime(GetLedsForTimeMixin):
    mod = _mod
