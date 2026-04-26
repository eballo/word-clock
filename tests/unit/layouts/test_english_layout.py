from __future__ import annotations

import wordclock.layouts.english as _mod
from tests.unit.layouts.layout_test_mixin import (
    AllTimesMixin,
    GetLedsForTimeMixin,
    SentenceToCoordsMixin,
)
from wordclock.layouts.english import (
    sentence_to_coords,
    time_to_sentence,
)


class TestTimeToSentence(AllTimesMixin):
    mod = _mod

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


class TestSentenceToCoords(SentenceToCoordsMixin):
    mod = _mod
    sample_sentence = "IT IS HALF PAST TEN"

    def test_it_is_lights_four_cells(self) -> None:
        # Given: only two words, four letters total
        sentence = "IT IS"
        # When
        coords = sentence_to_coords(sentence)
        # Then
        assert len(coords) == 4


class TestGetLedsForTime(GetLedsForTimeMixin):
    mod = _mod
