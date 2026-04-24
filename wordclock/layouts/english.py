"""
English layout 16x16 (256 LEDs, snake wiring).

Grid:
     0123456789012345
  0: ITKISASxTIMExxxx
  1: TWENTYxFIVExxxxx
  2: HALFxAQUARTERxxx
  3: PASTxTENxTOxMINx
  4: ONExxTWOxTHREExx
  5: FOURxFIVExSIXNIx  (X uppercase = real letter; x lowercase = filler)
  6: SEVENxEIGHTxNINx
  7: ExxxxTENxELEVENx
  8: NINExTWELVExxxxx
  9: OCLOCKxxxxxxxxxx
 10: XXXXXXXXXXXXXXXX
 ...
 15: XXXXXXXXXXXXXXXX

Time sentences:
  X:00  → IT IS <HOUR> OCLOCK
  X:05  → IT IS FIVE PAST <HOUR>
  X:10  → IT IS TEN PAST <HOUR>
  X:15  → IT IS A QUARTER PAST <HOUR>
  X:20  → IT IS TWENTY PAST <HOUR>
  X:25  → IT IS TWENTY FIVE PAST <HOUR>
  X:30  → IT IS HALF PAST <HOUR>
  X:35  → IT IS TWENTY FIVE TO <HOUR+1>
  X:40  → IT IS TWENTY TO <HOUR+1>
  X:45  → IT IS A QUARTER TO <HOUR+1>
  X:50  → IT IS TEN TO <HOUR+1>
  X:55  → IT IS FIVE TO <HOUR+1>
"""

from __future__ import annotations

from random import Random
from string import ascii_uppercase

# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------
GRID_RAW: list[str] = [
    "ITKISASxTIMExxxx",  #  0  IT IS
    "TWENTYxFIVExxxxx",  #  1  TWENTY FIVE
    "HALFxAQUARTERxxx",  #  2  HALF A QUARTER
    "PASTxTENxTOxMINx",  #  3  PAST TEN TO
    "ONExxTWOxTHREExx",  #  4  ONE TWO THREE
    "FOURxFIVExSIXNIx",  #  5  FOUR FIVE SIX  (X in SIX is a real letter)
    "SEVENxEIGHTxNINx",  #  6  SEVEN EIGHT NIN
    "ExxxxTENxELEVENx",  #  7  E(NINE) TEN ELEVEN
    "NINExTWELVExxxxx",  #  8  NINE TWELVE
    "OCLOCKxxxxxxxxxx",  #  9  OCLOCK
    "xxxxxxxxxxxxxxxx",  # 10
    "xxxxxxxxxxxxxxxx",  # 11
    "xxxxxxxxxxxxxxxx",  # 12
    "xxxxxxxxxxxxxxxx",  # 13
    "xxxxxxxxxxxxxxxx",  # 14
    "xxxxxxxxxxxxxxxx",  # 15
]

NUM_ROWS: int = len(GRID_RAW)
NUM_COLS: int = len(GRID_RAW[0])

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------
HOUR_WORDS: list[str] = [
    "TWELVE",   # 0 / 12
    "ONE",      # 1
    "TWO",      # 2
    "THREE",    # 3
    "FOUR",     # 4
    "FIVE",     # 5
    "SIX",      # 6
    "SEVEN",    # 7
    "EIGHT",    # 8
    "NINE",     # 9
    "TEN",      # 10
    "ELEVEN",   # 11
]

MINUTE_WORDS: list[str] = [
    "OCLOCK",           # 0  :00
    "FIVE PAST",        # 1  :05
    "TEN PAST",         # 2  :10
    "A QUARTER PAST",   # 3  :15
    "TWENTY PAST",      # 4  :20
    "TWENTY FIVE PAST", # 5  :25
    "HALF PAST",        # 6  :30
    "TWENTY FIVE TO",   # 7  :35
    "TWENTY TO",        # 8  :40
    "A QUARTER TO",     # 9  :45
    "TEN TO",           # 10 :50
    "FIVE TO",          # 11 :55
]

_NEXT_HOUR: frozenset[int] = frozenset(range(7, 12))  # :35 → :55


# ---------------------------------------------------------------------------
# Display grid (random filler letters)
# ---------------------------------------------------------------------------
def build_display_grid(seed: int | None = None) -> list[str]:
    """Replace X and space fillers with random uppercase letters."""
    rng = Random(seed)
    rows: list[str] = []
    for row in GRID_RAW:
        chars = list(row)
        for i, ch in enumerate(chars):
            if ch in ("x", " "):
                chars[i] = rng.choice(ascii_uppercase)
        rows.append("".join(chars))
    return rows


# ---------------------------------------------------------------------------
# Time → sentence
# ---------------------------------------------------------------------------
def time_to_sentence(hours: int, minutes: int) -> str:
    """
    Convert hours (0-23) and minutes (0-59) to an English word clock sentence.

    Examples:
        >>> time_to_sentence(10, 0)
        'IT IS TEN OCLOCK'
        >>> time_to_sentence(10, 15)
        'IT IS A QUARTER PAST TEN'
        >>> time_to_sentence(10, 45)
        'IT IS A QUARTER TO ELEVEN'
    """
    minute_index = minutes // 5
    h = hours % 12
    if minute_index in _NEXT_HOUR:
        h = (h + 1) % 12

    hour_word = HOUR_WORDS[h]
    minute_phrase = MINUTE_WORDS[minute_index]

    if minute_index == 0:
        return f"IT IS {hour_word} {minute_phrase}"
    else:
        return f"IT IS {minute_phrase} {hour_word}"


# ---------------------------------------------------------------------------
# Sentence → grid coordinates
# ---------------------------------------------------------------------------
def sentence_to_coords(
    sentence: str,
    grid: list[str] | None = None,
) -> list[tuple[int, int]]:
    """
    Find each word of the sentence in the grid (left-to-right, top-to-bottom)
    and return the (row, col) coordinates of every lit letter.

    Uses the same sequential search logic as the original JS prototype.
    """
    if grid is None:
        grid = GRID_RAW

    coords: list[tuple[int, int]] = []
    search_row = 0
    search_col = 0

    for word in sentence.split():
        for row_idx in range(search_row, NUM_ROWS):
            col_start = search_col if row_idx == search_row else 0
            col_idx = grid[row_idx].find(word, col_start)
            if col_idx != -1:
                for offset in range(len(word)):
                    coords.append((row_idx, col_idx + offset))
                search_row = row_idx
                search_col = col_idx + len(word)
                break

    return coords


# ---------------------------------------------------------------------------
# Coordinates → LED indices (snake wiring)
# ---------------------------------------------------------------------------
def coords_to_led_indices(
    coords: list[tuple[int, int]],
    snake: bool = True,
) -> list[int]:
    """Convert (row, col) pairs to absolute LED indices."""
    indices: list[int] = []
    for row, col in coords:
        if snake and row % 2 == 1:
            idx = row * NUM_COLS + (NUM_COLS - 1 - col)
        else:
            idx = row * NUM_COLS + col
        indices.append(idx)
    return indices


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def get_leds_for_time(
    hours: int,
    minutes: int,
    grid: list[str] | None = None,
    snake: bool = True,
) -> dict:
    """
    Return everything needed to update the display for a given time.

    Returns:
        {
          "sentence":    "IT IS A QUARTER PAST TEN",
          "coords":      [(row, col), ...],
          "led_indices": [42, 43, ...],
          "hours":       10,
          "minutes":     15,
        }
    """
    sentence = time_to_sentence(hours, minutes)
    coords = sentence_to_coords(sentence, grid)
    led_indices = coords_to_led_indices(coords, snake=snake)
    return {
        "sentence":    sentence,
        "coords":      coords,
        "led_indices": led_indices,
        "hours":       hours,
        "minutes":     minutes,
    }


# ---------------------------------------------------------------------------
# Quick CLI test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cases = [
        (12,  0), (1,   0), (3,   5), (6,  10),
        (10, 15), (8,  20), (4,  25), (7,  30),
        (11, 35), (2,  40), (9,  45), (5,  50), (3, 55),
    ]
    print("=" * 55)
    print("  English word clock — layout test")
    print("=" * 55)
    for h, m in cases:
        r = get_leds_for_time(h, m)
        print(f"  {h:02d}:{m:02d}  →  {r['sentence']}")
