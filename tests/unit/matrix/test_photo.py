from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image, UnidentifiedImageError

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.photo import CountdownScene, PhotoScene, pixelate


def jpeg(width: int, height: int, left: tuple[int, int, int], right: tuple[int, int, int]) -> bytes:
    image = Image.new("RGB", (width, height), left)
    image.paste(right, (width // 2, 0, width, height))
    data = BytesIO()
    image.save(data, "PNG")
    return data.getvalue()


def lit(canvas: Canvas) -> set[tuple[int, int]]:
    return {(x, y) for y, row in enumerate(canvas.rows()) for x, c in enumerate(row) if any(c)}


class TestPixelate:
    def test_one_colour_per_cell(self) -> None:
        # Given
        data = jpeg(200, 120, (255, 0, 0), (0, 0, 255))
        # When
        pixels = pixelate(data, 10, 6, mirror=False)
        # Then
        assert len(pixels) == 60
        assert pixels[0][0] > 200 and pixels[0][2] < 50
        assert pixels[9][2] > 200 and pixels[9][0] < 50

    def test_mirror_swaps_left_and_right(self) -> None:
        # Given
        data = jpeg(200, 120, (255, 0, 0), (0, 0, 255))
        # When
        pixels = pixelate(data, 10, 6)
        # Then: red is now on the right
        assert pixels[9][0] > 200

    def test_crops_to_the_matrix_shape(self) -> None:
        # Given: a tall photo, red on the left half
        data = jpeg(120, 400, (255, 0, 0), (0, 0, 255))
        # When
        pixels = pixelate(data, 10, 6, mirror=False)
        # Then: still split down the middle
        assert pixels[0][0] > 200
        assert pixels[9][2] > 200

    def test_darkens_middle_tones_for_the_leds(self) -> None:
        # Given: a plain middle grey
        data = jpeg(100, 60, (128, 128, 128), (128, 128, 128))
        # When
        pixels = pixelate(data, 10, 6, mirror=False)
        # Then: LED light is linear, so 50 % grey needs much less than 128
        assert pixels[0][0] < 64

    def test_rejects_data_that_is_not_an_image(self) -> None:
        # Given / When / Then
        with pytest.raises(UnidentifiedImageError):
            pixelate(b"not an image", 10, 6)


class TestCountdownScene:
    def test_counts_down_then_flashes(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = CountdownScene(seconds=3, fps=10)
        # When
        scene.render(canvas, 0)
        three = lit(canvas)
        scene.render(canvas, 30)
        # Then
        assert three and len(three) < 60
        assert len(lit(canvas)) == 60


class TestPhotoScene:
    def test_reveals_every_cell_in_time(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = PhotoScene([(9, 9, 9)] * 60, 10, fps=20, reveal_seconds=1, seed=1)
        # When
        scene.render(canvas, 0)
        first = len(lit(canvas))
        scene.render(canvas, 19)
        # Then
        assert 0 < first < 60
        assert len(lit(canvas)) == 60
