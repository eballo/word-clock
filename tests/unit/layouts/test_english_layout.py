"""Unit tests — English layout."""

from __future__ import annotations

import pytest

from wordclock.layouts.english import (
    NUM_COLS,
    NUM_ROWS,
    get_leds_for_time,
    sentence_to_coords,
    time_to_sentence,
)


class TestTimeToSentence:
    def test_oclock(self) -> None:
        # Given: time exactly on the hour
        hours, minutes = 10, 0
        # When: converting to sentence
        result = time_to_sentence(hours, minutes)
        # Then: sentence contains OCLOCK
        assert "OCLOCK" in result

    def test_five_past(self) -> None:
        # Given
        hours, minutes = 10, 5
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "FIVE" in result
        assert "PAST" in result

    def test_ten_past(self) -> None:
        # Given
        hours, minutes = 10, 10
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TEN" in result
        assert "PAST" in result

    def test_quarter_past(self) -> None:
        # Given
        hours, minutes = 10, 15
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "QUARTER" in result
        assert "PAST" in result

    def test_twenty_past(self) -> None:
        # Given
        hours, minutes = 10, 20
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TWENTY" in result
        assert "PAST" in result

    def test_twenty_five_past(self) -> None:
        # Given
        hours, minutes = 10, 25
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TWENTY" in result
        assert "FIVE" in result
        assert "PAST" in result

    def test_half_past(self) -> None:
        # Given
        hours, minutes = 10, 30
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "HALF" in result
        assert "PAST" in result

    def test_twenty_five_to(self) -> None:
        # Given
        hours, minutes = 10, 35
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TWENTY" in result
        assert "FIVE" in result
        assert "TO" in result

    def test_twenty_to(self) -> None:
        # Given
        hours, minutes = 10, 40
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TWENTY" in result
        assert "TO" in result

    def test_quarter_to(self) -> None:
        # Given
        hours, minutes = 10, 45
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "QUARTER" in result
        assert "TO" in result

    def test_ten_to(self) -> None:
        # Given
        hours, minutes = 10, 50
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "TEN" in result
        assert "TO" in result

    def test_five_to(self) -> None:
        # Given
        hours, minutes = 10, 55
        # When
        result = time_to_sentence(hours, minutes)
        # Then
        assert "FIVE" in result
        assert "TO" in result

    def test_to_advances_to_next_hour(self) -> None:
        # Given: time that requires showing the next hour
        hours, minutes = 10, 35
        # When
        result = time_to_sentence(hours, minutes)
        # Then: next hour (eleven) is shown, not current
        assert "ELEVEN" in result

    def test_all_sentences_start_with_it_is(self) -> None:
        # Given: every valid hour
        # When / Then: all sentences begin with IT IS
        for h in range(24):
            assert time_to_sentence(h, 0).startswith("IT IS"), f"Failed for hour {h}"

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
        sentence = "IT IS TEN OCLOCK"
        # When
        coords = sentence_to_coords(sentence)
        # Then: every coord falls inside the grid
        for row, col in coords:
            assert 0 <= row < NUM_ROWS
            assert 0 <= col < NUM_COLS

    def test_no_duplicate_coords(self) -> None:
        # Given
        sentence = "IT IS HALF PAST TEN"
        # When
        coords = sentence_to_coords(sentence)
        # Then
        assert len(coords) == len(set(coords))

    def test_it_is_lights_four_cells(self) -> None:
        # Given: only two words, four letters total
        sentence = "IT IS"
        # When
        coords = sentence_to_coords(sentence)
        # Then
        assert len(coords) == 4


class TestGetLedsForTime:
    def test_result_contains_required_keys(self) -> None:
        # Given
        hours, minutes = 10, 0
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        assert all(k in result for k in ("sentence", "coords", "led_indices", "hours", "minutes"))

    def test_led_indices_are_integers(self) -> None:
        # Given
        hours, minutes = 10, 0
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        assert all(isinstance(i, int) for i in result["led_indices"])

    def test_led_indices_within_grid_bounds(self) -> None:
        # Given
        hours, minutes = 10, 0
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        max_idx = NUM_ROWS * NUM_COLS - 1
        assert all(0 <= i <= max_idx for i in result["led_indices"])

    def test_hours_and_minutes_echoed_in_result(self) -> None:
        # Given
        hours, minutes = 7, 35
        # When
        result = get_leds_for_time(hours, minutes)
        # Then
        assert result["hours"] == hours
        assert result["minutes"] == minutes
