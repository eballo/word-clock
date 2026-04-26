from __future__ import annotations

from types import ModuleType

import pytest


class GetLedsForTimeMixin:
    """Shared tests for get_leds_for_time — inherit in each layout's TestGetLedsForTime."""

    mod: ModuleType

    def test_result_contains_required_keys(self) -> None:
        # Given / When
        result = self.mod.get_leds_for_time(10, 0)
        # Then
        assert all(k in result for k in ("sentence", "coords", "led_indices", "hours", "minutes"))

    def test_led_indices_are_integers(self) -> None:
        # Given / When
        result = self.mod.get_leds_for_time(10, 0)
        # Then
        assert all(isinstance(i, int) for i in result["led_indices"])

    def test_led_indices_within_grid_bounds(self) -> None:
        # Given / When
        result = self.mod.get_leds_for_time(10, 0)
        # Then
        max_idx = self.mod.NUM_ROWS * self.mod.NUM_COLS - 1
        assert all(0 <= i <= max_idx for i in result["led_indices"])

    def test_hours_and_minutes_echoed_in_result(self) -> None:
        # Given
        hours, minutes = 7, 35
        # When
        result = self.mod.get_leds_for_time(hours, minutes)
        # Then
        assert result["hours"] == hours
        assert result["minutes"] == minutes


class SentenceToCoordsMixin:
    """Shared tests for sentence_to_coords — inherit in each layout's TestSentenceToCoords."""

    mod: ModuleType
    sample_sentence: str

    def test_coords_within_grid_bounds(self) -> None:
        # Given / When
        coords = self.mod.sentence_to_coords(self.sample_sentence)
        # Then
        for row, col in coords:
            assert 0 <= row < self.mod.NUM_ROWS
            assert 0 <= col < self.mod.NUM_COLS

    def test_no_duplicate_coords(self) -> None:
        # Given / When
        coords = self.mod.sentence_to_coords(self.sample_sentence)
        # Then
        assert len(coords) == len(set(coords))


class AllTimesMixin:
    """Shared parametrized test that every time produces a non-empty sentence."""

    mod: ModuleType

    @pytest.mark.parametrize("h,m", [(h, m) for h in range(24) for m in range(0, 60, 5)])
    def test_all_times_produce_non_empty_sentence(self, h: int, m: int) -> None:
        # Given: any valid time
        # When
        result = self.mod.time_to_sentence(h, m)
        # Then
        assert len(result) > 0
