"""Unit tests — Spanish layout."""

from __future__ import annotations

import pytest

from wordclock.layouts.spanish import (
    NUM_COLS,
    NUM_ROWS,
    get_leds_for_time,
    sentence_to_coords,
    time_to_sentence,
)


class TestTimeToSentence:
    def test_en_punto_singular(self) -> None:
        # Given: hour 1 uses singular verb and article
        hours, minutes = 1, 0
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert result == "ES LA UNA EN PUNTO"

    def test_en_punto_plural(self) -> None:
        # Given: hour 2+ uses plural
        hours, minutes = 2, 0
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert result == "SON LAS DOS EN PUNTO"

    def test_y_cuarto(self) -> None:
        # Given
        hours, minutes = 10, 15
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "DIEZ" in result
        assert "Y CUARTO" in result

    def test_y_media(self) -> None:
        # Given
        hours, minutes = 10, 30
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "DIEZ" in result
        assert "Y MEDIA" in result

    def test_y_veinte(self) -> None:
        # Given
        hours, minutes = 10, 20
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "Y VEINTE" in result

    def test_y_veinticinco(self) -> None:
        # Given
        hours, minutes = 10, 25
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "Y VEINTICINCO" in result

    def test_menos_cuarto_advances_hour(self) -> None:
        # Given: :45 references the next hour
        hours, minutes = 10, 45
        # When
        result = time_to_sentence(hours, minutes)
        # Then: next hour (ONCE) appears
        assert "ONCE" in result
        assert "MENOS CUARTO" in result

    def test_menos_veinticinco(self) -> None:
        # Given
        hours, minutes = 10, 35
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "MENOS VEINTICINCO" in result

    def test_menos_advances_to_singular_hour(self) -> None:
        # Given: :50 past hour 12 → next hour is 1 (singular)
        hours, minutes = 12, 50
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert result.startswith("ES LA UNA")

    def test_y_cinco(self) -> None:
        # Given
        hours, minutes = 3, 5
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "Y CINCO" in result

    def test_24h_hour_wraps_correctly(self) -> None:
        # Given: hour 13 should behave like hour 1
        hours, minutes = 13, 0
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert result == "ES LA UNA EN PUNTO"

    @pytest.mark.parametrize("h,m", [(h, m) for h in range(24) for m in range(0, 60, 5)])
    def test_all_times_produce_non_empty_sentence(self, h: int, m: int) -> None:
        # Given: any valid time
        # When
        result = time_to_sentence(h, m)
        # Then
        assert len(result) > 0


class TestSentenceToCoords:
    def test_coords_within_grid_bounds(self) -> None:
        # Given
        sentence = "SON LAS DIEZ Y MEDIA"
        # When
        coords = sentence_to_coords(sentence)
        # Then
        for row, col in coords:
            assert 0 <= row < NUM_ROWS
            assert 0 <= col < NUM_COLS

    def test_no_duplicate_coords(self) -> None:
        # Given
        sentence = "ES LA UNA EN PUNTO"
        # When
        coords = sentence_to_coords(sentence)
        # Then
        assert len(coords) == len(set(coords))

    def test_veinticinco_normalised_and_found(self) -> None:
        # Given: VEINTICINCO is split to VEINTE + CINCO before searching
        sentence = "SON LAS DIEZ Y VEINTICINCO"
        # When
        coords = sentence_to_coords(sentence)
        # Then: coords are non-empty and in range
        assert len(coords) > 0
        for row, col in coords:
            assert 0 <= row < NUM_ROWS
            assert 0 <= col < NUM_COLS

    def test_menos_veinticinco_normalised_and_found(self) -> None:
        # Given: MENOS VEINTICINCO also requires normalisation
        sentence = "SON LAS ONCE MENOS VEINTICINCO"
        # When
        coords = sentence_to_coords(sentence)
        # Then
        assert len(coords) > 0


class TestGetLedsForTime:
    def test_result_contains_required_keys(self) -> None:
        # Given
        hours, minutes = 10, 30
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        assert all(k in result for k in ("sentence", "coords", "led_indices", "hours", "minutes"))

    def test_led_indices_are_integers(self) -> None:
        # Given
        hours, minutes = 2, 15
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        assert all(isinstance(i, int) for i in result["led_indices"])

    def test_led_indices_within_grid_bounds(self) -> None:
        # Given
        hours, minutes = 4, 45
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        max_idx = NUM_ROWS * NUM_COLS - 1
        assert all(0 <= i <= max_idx for i in result["led_indices"])

    def test_hours_and_minutes_echoed_in_result(self) -> None:
        # Given
        hours, minutes = 6, 20
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        assert result["hours"] == hours
        assert result["minutes"] == minutes
