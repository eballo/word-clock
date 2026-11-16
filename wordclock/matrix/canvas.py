from __future__ import annotations

Color = tuple[int, int, int]

BLACK: Color = (0, 0, 0)

# Current drawn by one WS2812B channel at full brightness, in milliamps.
MA_PER_CHANNEL: float = 20.0


def hex_to_color(value: str) -> Color:
    """
    Parse a hex colour such as ``ff8800`` or ``#ff8800``.

    Args:
        value: Six hex digits, with or without ``#``.

    Returns:
        The RGB colour.

    Raises:
        ValueError: If the value is not a hex colour.
    """
    digits = value.removeprefix("#")
    if len(digits) != 6:
        raise ValueError(f"Expected a hex colour like ff8800, got {value!r}")
    return (int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16))


class Canvas:
    """
    A grid of coloured cells that scenes draw on, one colour per cell.

    Coordinates are ``(x, y)`` with ``(0, 0)`` in the top-left corner.
    Drawing outside the canvas is ignored, so scenes can scroll freely.
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._cells: list[Color] = [BLACK] * (width * height)

    def clear(self) -> None:
        """Turn every cell off."""
        self.fill(BLACK)

    def fill(self, color: Color) -> None:
        """
        Paint every cell.

        Args:
            color: RGB colour, each channel 0-255.
        """
        self._cells = [color] * (self.width * self.height)

    def set(self, x: int, y: int, color: Color) -> None:
        """
        Paint one cell. Cells outside the canvas are ignored.

        Args:
            x: Column, 0 on the left.
            y: Row, 0 at the top.
            color: RGB colour, each channel 0-255.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self._cells[y * self.width + x] = color

    def get(self, x: int, y: int) -> Color:
        """
        Read one cell.

        Args:
            x: Column, 0 on the left.
            y: Row, 0 at the top.

        Returns:
            The cell colour, or black outside the canvas.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._cells[y * self.width + x]
        return BLACK

    def rows(self) -> list[list[Color]]:
        """
        Return the cells row by row, top row first.

        Returns:
            One list of colours per row.
        """
        return [self._cells[y * self.width : (y + 1) * self.width] for y in range(self.height)]

    def to_strip(
        self, snake: bool = True, rotate: bool = False, mirror: bool = False
    ) -> list[Color]:
        """
        Order the cells as the LEDs along the strip.

        Args:
            snake: Odd rows run right to left (snake wiring). False when every
                   row runs left to right.
            rotate: The matrix is mounted upside down: turn the picture 180°.
            mirror: Flip the picture left to right.

        Returns:
            One colour per LED, LED 0 first.
        """
        rows = self.rows()
        if rotate:
            rows = [list(reversed(row)) for row in reversed(rows)]
        if mirror:
            rows = [list(reversed(row)) for row in rows]
        colors: list[Color] = []
        for y, row in enumerate(rows):
            colors.extend(reversed(row) if snake and y % 2 == 1 else row)
        return colors


def strip_to_canvas(
    colors: list[Color],
    width: int,
    height: int,
    snake: bool = True,
    rotate: bool = False,
    mirror: bool = False,
) -> Canvas:
    """
    Turn LED colours back into the picture they show: the inverse of
    :meth:`Canvas.to_strip`.

    Args:
        colors: One colour per LED, LED 0 first.
        width: Cells per row.
        height: Number of rows.
        snake: Odd rows run right to left.
        rotate: The matrix is mounted upside down.
        mirror: The picture is flipped left to right.

    Returns:
        A canvas with the picture as seen from the front.
    """
    rows = [list(colors[y * width : (y + 1) * width]) for y in range(height)]
    rows = [list(reversed(row)) if snake and y % 2 == 1 else row for y, row in enumerate(rows)]
    if mirror:
        rows = [list(reversed(row)) for row in rows]
    if rotate:
        rows = [list(reversed(row)) for row in reversed(rows)]
    canvas = Canvas(width, height)
    for y, row in enumerate(rows):
        for x, color in enumerate(row):
            canvas.set(x, y, color)
    return canvas


def estimate_current_ma(colors: list[Color], brightness: int = 255) -> float:
    """
    Estimate the strip current for a frame.

    Args:
        colors: One colour per LED.
        brightness: Global strip brightness, 0-255.

    Returns:
        The estimated current in milliamps, without the LEDs' idle current.
    """
    total = sum(sum(color) for color in colors)
    return total / 255 * MA_PER_CHANNEL * brightness / 255


def limit_current(colors: list[Color], max_ma: float, brightness: int = 255) -> list[Color]:
    """
    Dim a frame so the strip stays under a current limit.

    Args:
        colors: One colour per LED.
        max_ma: Highest current allowed, in milliamps.
        brightness: Global strip brightness, 0-255.

    Returns:
        The same colours, scaled down when the frame would draw too much.
    """
    current = estimate_current_ma(colors, brightness)
    if current <= max_ma:
        return colors
    scale = max_ma / current
    return [(int(r * scale), int(g * scale), int(b * scale)) for r, g, b in colors]
