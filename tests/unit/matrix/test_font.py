from __future__ import annotations

import pytest

from wordclock.matrix.font import FONT_HEIGHT, GLYPHS, UNKNOWN, fold_char, glyph, render_text


class TestGlyphs:
    @pytest.mark.parametrize("char", sorted(GLYPHS))
    def test_every_glyph_is_a_rectangle(self, char: str) -> None:
        # Given
        rows = GLYPHS[char]
        # When
        widths = {len(row) for row in rows}
        # Then
        assert len(rows) == FONT_HEIGHT
        assert len(widths) == 1
        assert set("".join(rows)) <= {"#", "."}

    def test_covers_letters_and_digits(self) -> None:
        # Given
        wanted = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        # When
        missing = [char for char in wanted if char not in GLYPHS]
        # Then
        assert missing == []


class TestFoldChar:
    @pytest.mark.parametrize(
        ("char", "expected"),
        [("a", "A"), ("à", "A"), ("É", "E"), ("ï", "I"), ("ò", "O"), ("ç", "Ç"), ("·", "·")],
    )
    def test_folds_case_and_accents(self, char: str, expected: str) -> None:
        # Given / When
        folded = fold_char(char)
        # Then
        assert folded == expected

    def test_unknown_char_draws_a_question_mark(self) -> None:
        # Given / When
        rows = glyph("@")
        # Then
        assert rows == UNKNOWN


class TestRenderText:
    def test_letters_are_separated_by_one_column(self) -> None:
        # Given: two 3-column letters
        text = "HI"
        # When
        columns = render_text(text)
        # Then
        assert len(columns) == 3 + 1 + 3
        assert columns[3] == [False] * FONT_HEIGHT

    def test_columns_follow_the_glyph(self) -> None:
        # Given
        text = "L"
        # When
        columns = render_text(text)
        # Then: the first column of L is fully lit, the others only at the bottom
        assert columns[0] == [True] * FONT_HEIGHT
        assert columns[1] == [False, False, False, False, True]

    def test_empty_text(self) -> None:
        # Given / When
        columns = render_text("")
        # Then
        assert columns == []
