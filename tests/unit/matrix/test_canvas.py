from __future__ import annotations

from wordclock.matrix.canvas import Canvas, estimate_current_ma, limit_current


class TestCanvas:
    def test_starts_black(self) -> None:
        # Given / When
        canvas = Canvas(10, 6)
        # Then
        assert all(cell == (0, 0, 0) for row in canvas.rows() for cell in row)
        assert len(canvas.rows()) == 6
        assert len(canvas.rows()[0]) == 10

    def test_set_and_get(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        canvas.set(3, 2, (1, 2, 3))
        # Then
        assert canvas.get(3, 2) == (1, 2, 3)
        assert canvas.rows()[2][3] == (1, 2, 3)

    def test_ignores_cells_outside(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        canvas.set(-1, 0, (255, 0, 0))
        canvas.set(10, 0, (255, 0, 0))
        canvas.set(0, 6, (255, 0, 0))
        # Then
        assert canvas.get(-1, 0) == (0, 0, 0)
        assert canvas.to_strip() == [(0, 0, 0)] * 60

    def test_fill_and_clear(self) -> None:
        # Given
        canvas = Canvas(4, 2)
        # When
        canvas.fill((9, 9, 9))
        filled = canvas.to_strip()
        canvas.clear()
        # Then
        assert filled == [(9, 9, 9)] * 8
        assert canvas.to_strip() == [(0, 0, 0)] * 8


class TestToStrip:
    def test_snake_reverses_odd_rows(self) -> None:
        # Given: the last cell of row 0 and the first cell of row 1
        canvas = Canvas(10, 6)
        canvas.set(9, 0, (1, 0, 0))
        canvas.set(0, 1, (2, 0, 0))
        # When
        strip = canvas.to_strip(snake=True)
        # Then: row 1 starts on the right, so its first cell is LED 19
        assert strip[9] == (1, 0, 0)
        assert strip[19] == (2, 0, 0)

    def test_without_snake_keeps_rows_in_order(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        canvas.set(0, 1, (2, 0, 0))
        # When
        strip = canvas.to_strip(snake=False)
        # Then
        assert strip[10] == (2, 0, 0)

    def test_rotate_turns_the_picture_upside_down(self) -> None:
        # Given: the top-left cell
        canvas = Canvas(10, 6)
        canvas.set(0, 0, (1, 0, 0))
        # When
        strip = canvas.to_strip(rotate=True)
        # Then: it lands on the bottom-right cell, which row 5 (right to left) starts with
        assert strip.index((1, 0, 0)) == 50

    def test_mirror_flips_left_and_right(self) -> None:
        # Given: the top-left cell
        canvas = Canvas(10, 6)
        canvas.set(0, 0, (1, 0, 0))
        # When
        strip = canvas.to_strip(mirror=True)
        # Then: it lands on the top-right cell
        assert strip.index((1, 0, 0)) == 9

    def test_rotate_and_mirror_flip_top_and_bottom(self) -> None:
        # Given: the top-left cell
        canvas = Canvas(10, 6)
        canvas.set(0, 0, (1, 0, 0))
        # When
        strip = canvas.to_strip(rotate=True, mirror=True)
        # Then: it lands on the bottom-left cell, the last LED of row 5
        assert strip.index((1, 0, 0)) == 59


class TestCurrentLimit:
    def test_full_white_draws_60_ma_per_led(self) -> None:
        # Given
        colors = [(255, 255, 255)] * 60
        # When
        current = estimate_current_ma(colors)
        # Then
        assert current == 3600

    def test_brightness_scales_the_estimate(self) -> None:
        # Given
        colors = [(255, 255, 255)] * 60
        # When
        current = estimate_current_ma(colors, brightness=51)
        # Then
        assert current == 720

    def test_frame_under_limit_is_unchanged(self) -> None:
        # Given
        colors = [(255, 0, 0)] * 10
        # When
        limited = limit_current(colors, max_ma=1500)
        # Then
        assert limited == colors

    def test_frame_over_limit_is_dimmed(self) -> None:
        # Given: 3600 mA of white against a 1500 mA limit
        colors = [(255, 255, 255)] * 60
        # When
        limited = limit_current(colors, max_ma=1500)
        # Then
        assert estimate_current_ma(limited) <= 1500
        assert limited[0][0] > 0
