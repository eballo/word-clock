"""Unit tests — shared base functions (create_layout, coords_to_led_indices)."""

from __future__ import annotations

from wordclock.layouts.base import coords_to_led_indices
from wordclock.layouts.utils.grid import create_layout


class TestCreateLayout:
    def test_replaces_x_with_uppercase_letter(self) -> None:
        # Given: a raw grid with x fillers
        raw = ["xxxx"]
        # When
        result = create_layout(raw)
        # Then: every x is replaced by an uppercase letter
        assert result[0].isupper()
        assert "x" not in result[0]

    def test_preserves_real_letters(self) -> None:
        # Given: a row mixing real letters and fillers
        raw = ["ITxx"]
        # When
        result = create_layout(raw)
        # Then: real letters are unchanged
        assert result[0][0] == "I"
        assert result[0][1] == "T"

    def test_result_rows_same_length_as_input(self) -> None:
        # Given
        raw = ["ITKISASxTIMExxxx", "TWENTYxFIVExxxxx"]
        # When
        result = create_layout(raw)
        # Then: row lengths are preserved
        for raw_row, result_row in zip(raw, result):
            assert len(result_row) == len(raw_row)

    def test_deterministic_with_seed(self) -> None:
        # Given: same raw grid and same seed
        raw = ["xxxxxx"]
        # When: called twice with the same seed
        result_a = create_layout(raw, seed=42)
        result_b = create_layout(raw, seed=42)
        # Then: outputs are identical
        assert result_a == result_b

    def test_different_seeds_produce_different_output(self) -> None:
        # Given: a long row of fillers (enough variance to differ)
        raw = ["x" * 16]
        # When
        result_a = create_layout(raw, seed=1)
        result_b = create_layout(raw, seed=2)
        # Then: results are not identical (probabilistically certain for 16 chars)
        assert result_a != result_b


class TestCoordsToLedIndices:
    def test_even_row_uses_linear_index(self) -> None:
        # Given: a coord on an even row (no snake reversal)
        coords = [(0, 3)]
        num_cols = 16
        # When
        result = coords_to_led_indices(coords, num_cols)
        # Then: index = row * cols + col
        assert result == [3]

    def test_odd_row_snake_reversed(self) -> None:
        # Given: a coord on an odd row (snake wiring reverses column)
        coords = [(1, 0)]
        num_cols = 16
        # When
        result = coords_to_led_indices(coords, num_cols)
        # Then: index = 1*16 + (16-1-0) = 31
        assert result == [31]

    def test_snake_false_no_reversal_on_odd_row(self) -> None:
        # Given: snake disabled — odd rows should not be reversed
        coords = [(1, 0)]
        num_cols = 16
        # When
        result = coords_to_led_indices(coords, num_cols, snake=False)
        # Then: index = row * cols + col = 16
        assert result == [16]

    def test_multiple_coords_returns_multiple_indices(self) -> None:
        # Given
        coords = [(0, 0), (0, 1), (0, 2)]
        num_cols = 16
        # When
        result = coords_to_led_indices(coords, num_cols)
        # Then
        assert result == [0, 1, 2]
