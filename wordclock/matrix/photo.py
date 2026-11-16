from __future__ import annotations

from io import BytesIO
from random import Random

from PIL import Image, ImageEnhance, ImageOps

from wordclock.matrix.canvas import Canvas, Color
from wordclock.matrix.font import FONT_HEIGHT, render_text

# LEDs give out light in proportion to the value they get, while photos are
# stored for screens, which darken the middle tones: undo that.
LED_GAMMA = 2.2
SATURATION = 1.6
CONTRAST = 1.2


def pixelate(data: bytes, width: int, height: int, mirror: bool = True) -> list[Color]:
    """
    Turn a photo into one colour per cell.

    The photo is cropped to the shape of the matrix, averaged down to one
    pixel per cell, made more colourful and corrected for the LEDs.

    Args:
        data: The photo, in any format Pillow reads (JPEG, PNG...).
        width: Cells per row.
        height: Number of rows.
        mirror: Flip it left to right, so the matrix acts as a mirror.

    Returns:
        One colour per cell, row by row from the top-left corner.

    Raises:
        PIL.UnidentifiedImageError: If the data is not an image.
    """
    with Image.open(BytesIO(data)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    image = ImageOps.fit(image, (width, height), method=Image.Resampling.BOX)
    if mirror:
        image = ImageOps.mirror(image)
    image = ImageEnhance.Color(image).enhance(SATURATION)
    image = ImageEnhance.Contrast(image).enhance(CONTRAST)
    image = image.point(lambda v: round(255 * (v / 255) ** LED_GAMMA))
    return [image.getpixel((x, y)) for y in range(height) for x in range(width)]


class CountdownScene:
    """3, 2, 1 before the photo, then a white flash."""

    def __init__(self, seconds: int = 3, color: Color = (255, 255, 255), fps: float = 10) -> None:
        self.fps = fps
        self.seconds = seconds
        self.color = color

    def render(self, canvas: Canvas, frame: int) -> None:
        left = self.seconds - int(frame / self.fps)
        if left <= 0:
            canvas.fill((255, 255, 255))
            return
        canvas.clear()
        columns = render_text(str(left))
        x0 = (canvas.width - len(columns)) // 2
        y0 = canvas.height - FONT_HEIGHT
        for i, column in enumerate(columns):
            for y, lit in enumerate(column):
                if lit:
                    canvas.set(x0 + i, y0 + y, self.color)


class PhotoScene:
    """A pixelated photo that appears cell by cell, then stays."""

    def __init__(
        self,
        pixels: list[Color],
        width: int,
        fps: float = 20,
        reveal_seconds: float = 1.5,
        seed: int | None = None,
    ) -> None:
        self.fps = fps
        self.pixels = pixels
        self.width = width
        self.reveal_frames = max(1, round(reveal_seconds * fps))
        self._order = list(range(len(pixels)))
        Random(seed).shuffle(self._order)

    def render(self, canvas: Canvas, frame: int) -> None:
        shown = min(len(self._order), (frame + 1) * len(self._order) // self.reveal_frames)
        canvas.clear()
        for index in self._order[:shown]:
            canvas.set(index % self.width, index // self.width, self.pixels[index])
