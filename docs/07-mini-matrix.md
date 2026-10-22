# 07 — Mini Matrix

## Overview

A quick 10 × 6 LED matrix built before the word clock, with the 2 m
Tremex WS2812B strip (30 LEDs/metre, 60 LEDs) already at hand. Every cell
sits over one LED, so the matrix uses the whole strip. It runs the same
scene software the big clock will use (scrolling text, time, IP address,
animations) and tests the Raspberry Pi, the wiring and the printed
grid-and-face design on a small scale. This doc covers the parts, cutting
and wiring the strip, printing the enclosure, assembly and the software.

---

## 1. Parts

| Part | Quantity | Note |
|------|----------|------|
| Tremex WS2812B strip, 30 LEDs/metre, 2 m | 1 | Cut into 6 pieces of 10 LEDs |
| Raspberry Pi 3B with microSD card and its power supply | 1 | Set up as in [03 — Software](03-software.md) |
| 5V power supply, 2 A or more | 1 | The 5V 10 A supply of the bench test is fine |
| 1000 µF 16 V electrolytic capacitor | 1 | Across 5V and GND at the strip input |
| 220 Ω resistor | 1 | In the data line (Freenove kit) |
| Rectifier diode | 1 | Only if the 3,3V data is not read reliably (Freenove kit) |
| Wire, 22 AWG, three colours | about 1 m | 5 joints between rows, about 6 cm each |
| M3 × 16 mm bolt and nut | 3 | Join the two grid halves |
| Tracing paper | 1 A3 sheet | Diffuser between the face and the grid |
| PLA, white | about 150 g | Light grid |
| PLA, black | about 120 g | Front face |

---

## 2. Dimensions

```
                 35,7 cm
┌──────────────────────────────────────┐
│  margin 1,2 cm (wires between rows)  │
│ ┌──────────────────────────────────┐ │
│ │ 10 × 6 cells, 3,33 cm pitch      │ │ 22,4 cm
│ │ matrix 33,3 × 20,0 cm            │ │
│ └──────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
        left half │ right half   (split after column 5)
```

| Measurement | Value |
|-------------|-------|
| Cell pitch | 3,33 cm (one LED of a 30 LEDs/metre strip) |
| Matrix | 33,3 × 20,0 cm |
| Grid panel | 35,7 × 22,4 cm |
| Face (with its skirt) | 36,1 × 22,8 cm |
| Depth | about 2,6 cm (2 mm back plate, 22 mm walls, paper, 2 mm face) |
| Printed halves | Grid 17,9 × 22,4 cm, face 18,1 × 22,8 cm: each fits the 25,6 cm bed of the Bambu Lab A1 |
| Face windows | 3,03 × 3,03 cm, 3 mm bars |

---

## 3. Layer stack

```
   viewer
     │
     ▼
┌──────────────────────────────┐  face, black PLA, 2 mm, one window per cell
│ ▓▓  ▓▓  ▓▓  ▓▓  ▓▓  ▓▓  ▓▓   │  skirt (6 mm) hugs the grid outer wall
├──────────────────────────────┤  tracing paper
│ │    │    │    │    │    │   │  light grid, white PLA, 22 mm walls
│ │ ●  │ ●  │ ●  │ ●  │ ●  │ ● │  one WS2812B LED per cell
└──────────────────────────────┘  back plate 2 mm, strip stuck on it
```

The strip runs along the centre of every row, under the column walls
through 13 mm notches. The ends of each row come out into the margin,
where the wires that join the rows run.

---

## 4. Print the enclosure

```bash
uv run wordclock-cad --matrix    # STL files in build/stl/matrix/
```

It writes two Bambu Studio projects, one half per plate:

| Project | Parts | Filament | Orientation |
|---------|-------|----------|-------------|
| `build/bambu/matrix_grid.3mf` | `grid_left`, `grid_right` | White PLA, 3 walls, 15 % infill | Back plate on the bed |
| `build/bambu/matrix_face.3mf` | `face_left`, `face_right` | Black PLA, 100 % infill | Front on the bed, skirt up |

To change a size, edit the parameters at the top of
`wordclock/cad/matrix.scad` (wall height, margin, notch width) and render
again. Open the file in the OpenSCAD GUI to see the assembly.

---

## 5. Cut and wire the strip

### 5.1 Snake layout

LED 0 is in the top-left cell. Even rows run left to right, odd rows right
to left, so each row joins the next at alternating ends.

```
 DIN ──► [ 0  1  2  3  4  5  6  7  8  9] ─┐   row 0
      ┌─ [19 18 17 16 15 14 13 12 11 10] ◄┘   row 1
      └► [20 21 22 23 24 25 26 27 28 29] ─┐   row 2
      ┌─ [39 38 37 36 35 34 33 32 31 30] ◄┘   row 3
      └► [40 41 42 43 44 45 46 47 48 49] ─┐   row 4
         [59 58 57 56 55 54 53 52 51 50] ◄┘   row 5
```

### 5.2 Steps

1. Check the arrows printed on the strip: they point away from DIN. Start
   from the DIN end.
2. Cut 6 pieces of 10 LEDs (33,3 cm each) on the copper cut marks.
3. Stick each piece along the centre of its row, through the wall notches,
   arrows pointing in the direction of the row (right on rows 0, 2 and 4,
   left on rows 1, 3 and 5).
4. Solder three wires (5V, data, GND) from the DOUT end of each row to the
   DIN end of the next one, in the side margin. Keep the colours the same
   on every joint.
5. Solder the input wires to the DIN end of row 0 and pass them through the
   hole in the back plate of the left half.

> ⚠️ Data goes from DOUT to DIN only. A row stuck the wrong way round stays
> dark, and so does every row after it.

### 5.3 Connection to the Raspberry Pi

The wiring is the same as the bench test ([06 — Bench Test](06-bench-test.md), section 2):

| From | To | Note |
|------|----|------|
| Pi GPIO 18 (pin 12) | 220 Ω resistor → strip DIN | Data line |
| Pi GND | Supply − | Common ground |
| Supply + | Strip 5V | Strip power only, never to the Pi pins |
| Supply − | Strip GND | |
| 1000 µF capacitor | Between strip 5V and GND, at the input | Stripe (negative) to GND |

60 LEDs draw up to 3,6 A in full white. The software dims any frame that
would draw more than 1,5 A (`MATRIX_MAX_MA` in `wordclock/config.py`), so
the breadboard and a 2 A supply are enough. If the colours flicker, use the
diode trick from the bench test.

---

## 6. Assemble

1. Bolt the two grid halves together with the three M3 bolts: one in the
   top margin, one in the bottom margin and one on the middle row wall.
2. Stick the strip rows and solder the joints (section 5).
3. Run the `wiring` scene (section 7) and check that the cells light in
   order before closing.
4. Lay the tracing paper over the grid, cut to the outer edge of the walls.
5. Press the two face halves onto the grid: the skirt hugs the outer wall.

---

## 7. Software

The matrix uses the `wordclock-matrix` command. On the Mac, `--mock` draws
the matrix in the terminal instead of lighting LEDs:

```bash
uv run wordclock-matrix --mock text --text "Hola!"
uv run wordclock-matrix --mock rain
uv run wordclock-matrix --mock clock --color ff8800
```

On the Raspberry Pi, after `uv sync --extra rpi` ([03 — Software](03-software.md)):

```bash
cd ~/word-clock
sudo .venv/bin/wordclock-matrix wiring          # cells one by one: checks the snake
sudo .venv/bin/wordclock-matrix rainbow         # colour order and every LED
sudo .venv/bin/wordclock-matrix ip              # IP address of the Pi
sudo .venv/bin/wordclock-matrix text --text "Bon dia" --preview
```

| Scene | What it shows |
|-------|---------------|
| `text` | Scrolling text (`--text`), 3 × 5 pixel font, accents folded (`à` → `A`) |
| `clock` | The time as `HH:MM`, scrolling |
| `ip` | The local IP address, scrolling |
| `rain` | Green drops with fading trails, like Matrix rain |
| `rainbow` | A rainbow sliding diagonally |
| `wiring` | One cell at a time, in order, to test the wiring |

| Option | Default | Use |
|--------|---------|-----|
| `--brightness` | 40 | Global brightness, 0–255 |
| `--color` | per scene | Hex colour, e.g. `ff8800` |
| `--max-ma` | 1500 | Software current limit in mA |
| `--seconds` | none | Stop after this time |
| `--no-snake` | | Every row wired left to right |
| `--preview` | with `--mock` | Also draw the matrix in the terminal |

The scenes draw on a cell canvas of any size (`--width`, `--height`), so
the same code runs on the 16 × 16 word clock later.

---

## 8. Build checklist

- [ ] Grid halves and face halves printed (`uv run wordclock-cad --matrix`)
- [ ] Grid halves bolted together with three M3 × 16 mm bolts
- [ ] Strip cut into 6 pieces of 10 LEDs, stuck in a snake, arrows checked
- [ ] Five row joints soldered, input wires through the back plate hole
- [ ] Safety check of [06 — Bench Test](06-bench-test.md) done before powering up
- [ ] `wiring` scene lights the 60 cells in order
- [ ] `rainbow` scene shows the right colours
- [ ] Tracing paper and face fitted
- [ ] `text`, `clock`, `ip` and `rain` scenes running
