from __future__ import annotations

from random import Random
from string import ascii_uppercase

GRID_RAW: list[str] = [
    "ÉSÓNxVORAxxxxxxx",
    "UNxDOSxTRESxxxxx",
    "QUARTSxxxxxxxxxx",
    "IMENYSxCINCxxxxx",
    "DED'LAxLESxxxxxx",
    "UNADUESTRESxxxxx",
    "QUATRExCINCxxxxx",
    "SISSETVUITxxxxxx",
    "NOUxDEUONZExxxxx",
    "DOTZExxxxxxxxxxx",
    "xxxxENxPUNTxxxxx",
    "IMENYSxCINCxxxxx",
    "xxxxMINUTSxxxxxx",
    "DELLAxTARDAxxxxx",
    "LAxNITMATÍxxxxxx",
    "xxxxxxxxxxxxxxxx",
]

NUM_ROWS = 16
NUM_COLS = 16

HOUR_WORDS: list[str] = [
    "DOTZE",
    "UNA",
    "DUES",
    "TRES",
    "QUATRE",
    "CINC",
    "SIS",
    "SET",
    "VUIT",
    "NOU",
    "DEU",
    "ONZE",
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


def time_to_sentence_cat(hours: int, minutes: int) -> str:
    h = hours % 12
    m = (minutes // 5) * 5

    ph = (h + 1) % 12
    ph_word = HOUR_WORDS[ph]

    # Preposition: D' for UNA/ONZE, DE for others
    prep = "D'" if ph_word in ["UNA", "ONZE"] else "DE"

    if m == 0:
        verb = "ÉS" if h == 1 else "SÓN"
        art = "LA" if h == 1 else "LES"
        return f"{verb} {art} {HOUR_WORDS[h]} EN PUNT"

    if m == 5 or m == 10:
        verb = "SÓN" if h != 1 else "ÉS"
        art = "LA" if h == 1 else "LES"
        return f"{verb} VORA {art} {HOUR_WORDS[h]}"

    # Catalan "Quarters" system (references the NEXT hour)
    if m == 15:
        return f"ÉS UN QUART {prep} {ph_word}"
    if m == 20:
        return f"ÉS UN QUART I CINC {prep} {ph_word}"
    if m == 25:
        return f"SÓN DOS QUARTS {prep} {ph_word} MENYS CINC"
    if m == 30:
        return f"SÓN DOS QUARTS {prep} {ph_word}"
    if m == 35:
        return f"SÓN DOS QUARTS I CINC {prep} {ph_word}"
    if m == 40:
        return f"SÓN TRES QUARTS {prep} {ph_word} MENYS CINC"
    if m == 45:
        return f"SÓN TRES QUARTS {prep} {ph_word}"
    if m == 50:
        return f"SÓN TRES QUARTS I CINC {prep} {ph_word}"
    if m == 55:
        return f"SÓN VORA {('LA' if ph == 1 else 'LES')} {ph_word}"

    return ""


def sentence_to_coords(sentence: str, grid: list[str] | None = None) -> list[tuple[int, int]]:
    if grid is None:
        grid = GRID_RAW
    coords = []
    # Split apostrophe to match the "D'" in the grid
    clean_sentence = sentence.replace("D'", "D' ")
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
    sentence = time_to_sentence_cat(hours, minutes)
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
        (1, 0),  # 01:00
        (2, 5),  # 02:05
        (10, 15),  # 10:15
        (12, 30),  # 12:30
        (4, 45),  # 04:45
        (11, 55),  # 11:55
    ]
    print("=" * 55)
    print("  Catalan word clock — layout test")
    print("=" * 55)
    print()
    print(f"{'TIME':<8} | {'SENTENCE'}")
    print("-" * 40)
    for h, m in cases:
        res = get_leds_for_time(h, m)
        print(f"{h:02d}:{m:02d}    | {res['sentence']}")
