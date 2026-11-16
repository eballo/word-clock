from __future__ import annotations

from colorsys import hsv_to_rgb

from wordclock.matrix.canvas import Color

WHITE: Color = (255, 255, 255)
GREEN: Color = (0, 255, 70)


def hue_color(hue: float) -> Color:
    """
    Turn a hue into a fully saturated, full brightness colour.

    Args:
        hue: Hue from 0 to 1; values outside wrap around.

    Returns:
        The RGB colour.
    """
    r, g, b = hsv_to_rgb(hue % 1.0, 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))


def scale(color: Color, level: float) -> Color:
    """
    Dim a colour.

    Args:
        color: The full colour.
        level: 0 for black, 1 for the full colour.

    Returns:
        The dimmed colour.
    """
    return (round(color[0] * level), round(color[1] * level), round(color[2] * level))


def add(a: Color, b: Color) -> Color:
    """
    Mix two lights on the same cell.

    Args:
        a: One colour.
        b: The other colour.

    Returns:
        Their sum, each channel capped at 255.
    """
    return (min(255, a[0] + b[0]), min(255, a[1] + b[1]), min(255, a[2] + b[2]))
