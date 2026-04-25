from __future__ import annotations

from random import Random
from string import ascii_uppercase

GRID_RAW: list[str] = [
    "ESONxLASxLAxxxxx",
    "UNAxDOSxTRESxxxx",
    "CUATROxCINCOxxxx",
    "SEISxSIETExOCHOx",
    "NUEVExDIExONCExx",
    "DOCExYxMENOSxxxx",
    "CUARTOxVEINTExxx",
    "CINCOxDIEZxxxxxx",
    "MEDIAxxxxxxxxxxx",
    "ENxPUNTOxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
    "xxxxxxxxxxxxxxxx",
]

NUM_ROWS = 16
NUM_COLS = 16

HOUR_WORDS: list[str] = [
    "DOCE",
    "UNA",
    "DOS",
    "TRES",
    "CUATRO",
    "CINCO",
    "SEIS",
    "SIETE",
    "OCHO",
    "NUEVE",
    "DIEZ",
    "ONCE",
]


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


def time_to_sentence_esp(hours: int, minutes: int) -> str:
    h = hours % 12
    m = (minutes // 5) * 5

    # Adjust hour for "MENOS" (from :35 to :55)
    if m >= 35:
        h = (h + 1) % 12

    verb = "ES" if h == 1 else "SON"
    art = "LA" if h == 1 else "LAS"
    h_word = HOUR_WORDS[h]

    if m == 0:
        return f"{verb} {art} {h_word} EN PUNTO"

    # Minutes mapping for Spanish "Y" / "MENOS" system
    minutes_map = {
        5: "Y CINCO",
        10: "Y DIEZ",
        15: "Y CUARTO",
        20: "Y VEINTE",
        25: "Y VEINTICINCO",
        30: "Y MEDIA",
        35: "MENOS VEINTICINCO",
        40: "MENOS VEINTE",
        45: "MENOS CUARTO",
        50: "MENOS DIEZ",
        55: "MENOS CINCO",
    }

    # Handling "VEINTICINCO" which might be split in some grids
    # For this grid, we use separate words if needed
    m_phrase = minutes_map[m]
    return f"{verb} {art} {h_word} {m_phrase}"


def sentence_to_coords(sentence: str, grid: list[str] | None = None) -> list[tuple[int, int]]:
    if grid is None:
        grid = GRID_RAW
    coords = []
    # Special handling for "VEINTICINCO" if it's split into VEINTE and CINCO
    clean_sentence = sentence.replace("VEINTICINCO", "VEINTE CINCO")
    words = clean_sentence.split()

    current_row = 0
    current_col = 0

    for word in words:
        found = False
        for r in range(current_row, NUM_ROWS):
            start_c = current_col if r == current_row else 0
            idx = grid[r].find(word, start_c)
            if idx != -1:
                for i in range(len(word)):
                    coords.append((r, idx + i))
                current_row = r
                current_col = idx + len(word)
                found = True
                break

        if not found:
            for r in range(NUM_ROWS):
                idx = grid[r].find(word)
                if idx != -1:
                    for i in range(len(word)):
                        coords.append((r, idx + i))
                    current_row = r
                    current_col = idx + len(word)
                    break
    return coords


def coords_to_led_indices(coords: list[tuple[int, int]], snake: bool = True) -> list[int]:
    indices = []
    for row, col in coords:
        if snake and row % 2 == 1:
            idx = row * NUM_COLS + (NUM_COLS - 1 - col)
        else:
            idx = row * NUM_COLS + col
        indices.append(idx)
    return indices


def get_leds_for_time(
    hours: int, minutes: int, grid: list[str] | None = None, snake: bool = True
) -> dict:
    sentence = time_to_sentence_esp(hours, minutes)
    coords = sentence_to_coords(sentence, grid=grid)
    led_indices = coords_to_led_indices(coords, snake=snake)
    return {
        "hours": hours,
        "minutes": minutes,
        "sentence": sentence,
        "coords": coords,
        "led_indices": led_indices,
    }


if __name__ == "__main__":
    cases = [
        (1, 0),  # 01:00 -> ES LA UNA EN PUNTO
        (2, 15),  # 02:15 -> SON LAS DOS Y CUARTO
        (10, 30),  # 10:30 -> SON LAS DIEZ Y MEDIA
        (4, 45),  # 04:45 -> SON LAS CINCO MENOS CUARTO
        (12, 50),  # 12:50 -> ES LA UNA MENOS DIEZ
    ]
    print("=" * 55)
    print("  Spanish word clock — layout test")
    print("=" * 55)
    print()
    print(f"{'TIME':<8} | {'SENTENCE'}")
    print("-" * 40)
    for h, m in cases:
        res = get_leds_for_time(h, m)
        print(f"{h:02d}:{m:02d}    | {res['sentence']}")
