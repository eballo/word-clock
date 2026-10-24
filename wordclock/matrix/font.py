from __future__ import annotations

from unicodedata import category, normalize

# Pixel font, 5 rows high. Each glyph is a list of rows; "#" is a lit cell.
# Most glyphs are 3 cells wide; M, N, W and a few symbols are wider.
FONT_HEIGHT: int = 5
LETTER_SPACING: int = 1

GLYPHS: dict[str, tuple[str, ...]] = {
    "A": (".#.", "#.#", "###", "#.#", "#.#"),
    "B": ("##.", "#.#", "##.", "#.#", "##."),
    "C": (".##", "#..", "#..", "#..", ".##"),
    "D": ("##.", "#.#", "#.#", "#.#", "##."),
    "E": ("###", "#..", "##.", "#..", "###"),
    "F": ("###", "#..", "##.", "#..", "#.."),
    "G": (".##", "#..", "#.#", "#.#", ".##"),
    "H": ("#.#", "#.#", "###", "#.#", "#.#"),
    "I": ("###", ".#.", ".#.", ".#.", "###"),
    "J": ("..#", "..#", "..#", "#.#", ".#."),
    "K": ("#.#", "#.#", "##.", "#.#", "#.#"),
    "L": ("#..", "#..", "#..", "#..", "###"),
    "M": ("#...#", "##.##", "#.#.#", "#...#", "#...#"),
    "N": ("#..#", "##.#", "#.##", "#..#", "#..#"),
    "O": (".#.", "#.#", "#.#", "#.#", ".#."),
    "P": ("##.", "#.#", "##.", "#..", "#.."),
    "Q": (".#.", "#.#", "#.#", "##.", ".##"),
    "R": ("##.", "#.#", "##.", "#.#", "#.#"),
    "S": (".##", "#..", ".#.", "..#", "##."),
    "T": ("###", ".#.", ".#.", ".#.", ".#."),
    "U": ("#.#", "#.#", "#.#", "#.#", "###"),
    "V": ("#.#", "#.#", "#.#", "#.#", ".#."),
    "W": ("#...#", "#...#", "#.#.#", "##.##", "#...#"),
    "X": ("#.#", "#.#", ".#.", "#.#", "#.#"),
    "Y": ("#.#", "#.#", ".#.", ".#.", ".#."),
    "Z": ("###", "..#", ".#.", "#..", "###"),
    "Ç": (".##", "#..", "#..", ".##", ".#."),
    "0": ("###", "#.#", "#.#", "#.#", "###"),
    "1": (".#.", "##.", ".#.", ".#.", "###"),
    "2": ("##.", "..#", ".#.", "#..", "###"),
    "3": ("##.", "..#", ".#.", "..#", "##."),
    "4": ("#.#", "#.#", "###", "..#", "..#"),
    "5": ("###", "#..", "##.", "..#", "##."),
    "6": (".##", "#..", "###", "#.#", "###"),
    "7": ("###", "..#", ".#.", ".#.", ".#."),
    "8": ("###", "#.#", "###", "#.#", "###"),
    "9": ("###", "#.#", "###", "..#", "##."),
    " ": ("..", "..", "..", "..", ".."),
    ".": (".", ".", ".", ".", "#"),
    ",": ("..", "..", "..", ".#", "#."),
    ":": (".", "#", ".", "#", "."),
    "'": ("#", "#", ".", ".", "."),
    "!": ("#", "#", "#", ".", "#"),
    "?": ("##.", "..#", ".#.", "...", ".#."),
    "-": ("...", "...", "###", "...", "..."),
    "+": ("...", ".#.", "###", ".#.", "..."),
    "/": ("..#", "..#", ".#.", "#..", "#.."),
    "%": ("#.#", "..#", ".#.", "#..", "#.#"),
    "·": (".", ".", "#", ".", "."),
    "♥": (".#.#.", "#####", "#####", ".###.", "..#.."),
}

# Shown for characters the font does not have.
UNKNOWN: tuple[str, ...] = GLYPHS["?"]


def fold_char(char: str) -> str:
    """
    Map a character to one the font can draw.

    Lowercase becomes uppercase and accents are dropped (``à`` → ``A``),
    except ``Ç``, which has its own glyph.

    Args:
        char: A single character.

    Returns:
        A key of :data:`GLYPHS`, or the input when there is no match.
    """
    upper = char.upper()
    if upper in GLYPHS:
        return upper
    stripped = "".join(c for c in normalize("NFD", upper) if category(c) != "Mn")
    return stripped if stripped in GLYPHS else char


def glyph(char: str) -> tuple[str, ...]:
    """
    Return the pixel rows of a character.

    Args:
        char: A single character.

    Returns:
        :data:`FONT_HEIGHT` rows of ``#`` (lit) and ``.`` (off).
    """
    return GLYPHS.get(fold_char(char), UNKNOWN)


def render_text(text: str) -> list[list[bool]]:
    """
    Lay out a line of text as columns of pixels.

    Args:
        text: The text to draw, any case, accents allowed.

    Returns:
        One list per column, each with :data:`FONT_HEIGHT` booleans, top
        first. Glyphs are separated by :data:`LETTER_SPACING` empty columns.
    """
    columns: list[list[bool]] = []
    for i, char in enumerate(text):
        if i > 0:
            columns.extend([[False] * FONT_HEIGHT for _ in range(LETTER_SPACING)])
        rows = glyph(char)
        for x in range(len(rows[0])):
            columns.append([row[x] == "#" for row in rows])
    return columns
