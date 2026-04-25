"""Unit tests — English layout."""

import pytest

from wordclock.layouts.english import (
    NUM_COLS,
    NUM_ROWS,
    get_leds_for_time,
    sentence_to_coords,
    time_to_sentence,
)


class TestTimeToSentence:
    def test_oclock(self):
        assert "OCLOCK" in time_to_sentence(10, 0)

    def test_five_past(self):
        s = time_to_sentence(10, 5)
        assert "FIVE" in s and "PAST" in s

    def test_ten_past(self):
        s = time_to_sentence(10, 10)
        assert "TEN" in s and "PAST" in s

    def test_quarter_past(self):
        s = time_to_sentence(10, 15)
        assert "QUARTER" in s and "PAST" in s

    def test_twenty_past(self):
        s = time_to_sentence(10, 20)
        assert "TWENTY" in s and "PAST" in s

    def test_twenty_five_past(self):
        s = time_to_sentence(10, 25)
        assert "TWENTY" in s and "FIVE" in s and "PAST" in s

    def test_half_past(self):
        s = time_to_sentence(10, 30)
        assert "HALF" in s and "PAST" in s

    def test_twenty_five_to(self):
        s = time_to_sentence(10, 35)
        assert "TWENTY" in s and "FIVE" in s and "TO" in s

    def test_twenty_to(self):
        s = time_to_sentence(10, 40)
        assert "TWENTY" in s and "TO" in s

    def test_quarter_to(self):
        s = time_to_sentence(10, 45)
        assert "QUARTER" in s and "TO" in s

    def test_ten_to(self):
        s = time_to_sentence(10, 50)
        assert "TEN" in s and "TO" in s

    def test_five_to(self):
        s = time_to_sentence(10, 55)
        assert "FIVE" in s and "TO" in s

    def test_next_hour_on_to(self):
        # 10:35 → IT IS TWENTY FIVE TO ELEVEN
        s = time_to_sentence(10, 35)
        assert "ELEVEN" in s

    def test_it_is_prefix(self):
        for h in range(24):
            s = time_to_sentence(h, 0)
            assert s.startswith("IT IS"), f"Failed for hour {h}: {s}"

    @pytest.mark.parametrize("h,m", [(h, m) for h in range(24) for m in range(0, 60, 5)])
    def test_all_times_generate_sentence(self, h, m):
        s = time_to_sentence(h, m)
        assert len(s) > 0


class TestSentenceToCoords:
    def test_coords_in_range(self):
        coords = sentence_to_coords("IT IS TEN OCLOCK")
        for row, col in coords:
            assert 0 <= row < NUM_ROWS
            assert 0 <= col < NUM_COLS

    def test_no_duplicates(self):
        coords = sentence_to_coords("IT IS HALF PAST TEN")
        assert len(coords) == len(set(coords))

    def test_finds_it_is(self):
        coords = sentence_to_coords("IT IS")
        assert len(coords) == 4  # I T I S


class TestGetLedsForTime:
    def test_returns_correct_keys(self):
        result = get_leds_for_time(10, 0)
        assert all(k in result for k in ("sentence", "coords", "led_indices", "hours", "minutes"))

    def test_led_indices_are_ints(self):
        result = get_leds_for_time(10, 0)
        assert all(isinstance(i, int) for i in result["led_indices"])

    def test_led_indices_in_range(self):
        result = get_leds_for_time(10, 0)
        max_idx = NUM_ROWS * NUM_COLS - 1
        assert all(0 <= i <= max_idx for i in result["led_indices"])
