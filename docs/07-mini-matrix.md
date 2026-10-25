# 07 — Mini Matrix

## Overview

A quick 10 × 6 LED matrix built before the word clock, with the 2 m
Tremex WS2812B strip (30 LEDs/metre, 60 LEDs) already at hand. Every cell
sits over one LED, so the matrix uses the whole strip. It runs the same
scene software the big clock will use (scrolling text, time, IP address,
animations) and tests the Raspberry Pi, the wiring and the printed
grid-and-face design on a small scale. The enclosure is three layers that
click together: a flat tray where the strip is stuck and soldered, the
cell grid and the face, with a camera behind one of the face rivets. This
doc covers the parts, cutting and wiring the strip, printing the
enclosure, assembly and the software.

---

## 1. Parts

| Part | Quantity | Note |
|------|----------|------|
| Tremex WS2812B strip, 30 LEDs/metre, 2 m | 1 | Cut into 6 pieces of 10 LEDs |
| Raspberry Pi 3B with microSD card | 1 | Set up as in [03 — Software](03-software.md), Wi-Fi and SSH on |
| 5V power supply, 3 A or more, 5.5 × 2.1 mm plug | 1 | Powers the strip and the Pi: the only cable; the 5V 10 A supply of the bench test is fine |
| Micro-USB plug with screw terminals (USB-C on a 4B) | 1 | Powers the Pi from the same supply, inside the box |
| 1000 µF 16 V electrolytic capacitor | 1 | Across 5V and GND at the strip input |
| 220 Ω resistor | 1 | In the data line (Freenove kit) |
| Rectifier diode | 1 | Only if the 3,3V data is not read reliably (Freenove kit) |
| Wire, 22 AWG, three colours | about 1 m | 5 joints between rows, about 6 cm each |
| M3 × 16 mm bolt and nut | 2 | Join the two tray halves |
| Panel-mount DC jack, 5.5 × 2.1 mm (DC-022, 11 mm hole) | 1 | Power input in the side of the stand box |
| Screw with a head up to 8 mm, and wall plug | 2 | Only to hang the matrix on a wall |
| Lever connectors (Wago 221), 3-way | 2 | 5V and GND joints inside the box |
| Camera, OV5647 5 MP (Raspberry Pi Camera v1.3 size) | 1 | Behind one face rivet; optional |
| Camera flat cable, 15-pin, 30 cm | 1 | From the camera, through the cable hole next to it, to the Pi; the 15 cm cable of the camera may just reach |
| Tracing paper | 1 A3 sheet | Diffuser between the face and the grid |
| PLA, white | about 250 g | Tray and light grid |
| PLA, black | about 250 g | Front face and stand box |

---

## 2. Dimensions

```
                 37,7 cm
┌──────────────────────────────────────┐
│ ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○ ○ │  margins 2,2 cm: wires
│ ┌──────────────────────────────────┐ │
│ │ 10 × 6 cells, 3,33 cm pitch      │ │ 25,0 cm
○ │ matrix 33,3 × 20,0 cm            │ ○
│ └──────────────────────────────────┘ │
│ ○  ○  ○  ○  ○  ◉  ○  ○  ○  ○  ○  ○ ○ │  bottom margin 2,8 cm: camera (◉)
└──────────────────────────────────────┘
        left half │ right half   (split after column 5)
```

| Measurement | Value |
|-------------|-------|
| Cell pitch | 3,33 cm (one LED of a 30 LEDs/metre strip) |
| Matrix | 33,3 × 20,0 cm |
| Tray | 37,7 × 25,0 cm |
| Margins | 2,2 cm at the sides and top: a 19 mm channel inside the rim, wide enough for a soldering iron; 2,8 cm at the bottom for the camera board |
| Face (with its skirt) | 38,1 × 25,4 cm |
| Depth | about 2,6 cm (2 mm back plate, 22 mm walls, paper, 2 mm face), plus 4,0 cm of stand box |
| Printed halves | Tray 18,9 × 25,0 cm, grid 18,7 × 24,7 cm, face 19,1 × 25,4 cm: each fits the 25,6 cm bed of the Bambu Lab A1 |
| Stand box | 12,0 × 10,7 × 4,0 cm, at the bottom of the back, centred |
| Tilt on the table | 15° backwards |
| Face windows | 3,03 × 3,03 cm, 3 mm bars |
| Rivets | Ø6 mm, 1 mm deep, about 2,1 cm apart around the border |

---

## 3. Layers

```
   viewer
     │
     ▼
┌──────────────────────────────┐  face, black PLA, 2 mm: one window per cell,
│ ▓▓  ▓▓  ▓▓  ▓▓  ▓▓  ▓▓  ▓▓   │  rivets; the skirt clicks onto the tray rim
├──────────────────────────────┤  tracing paper, cut to the grid
│ │    │    │    │    │    │   │  grid, white PLA: the 22 mm walls only,
│ │    │    │    │    │    │   │  clicks into the tray rim
│ ●    ●    ●    ●    ●    ●   │  one WS2812B LED per cell
└──────────────────────────────┘  tray, white PLA: 2 mm back plate and rim,
        ┌──────────────┐          the strip stuck on the plate
        │  Pi   ◯ jack │          stand box, 40 mm: Raspberry Pi, DC jack,
        └──────────────┘          wiring
```

The tray is open while you work on the strip: stick the rows on the flat
plate, between two shallow guide grooves per row, and solder every joint
with nothing in the way. Then the grid goes on top: the strip passes under
the walls through 13 mm notches, and the row ends come out into the side
margins, where the joints are.

### Click fit

Nothing is glued or screwed, except the two M3 bolts that join the tray
halves. Eight bridges reach from the top of the grid across the margins to
the rim, two on each side; a bump at the end of each bridge clicks into a
2,6 mm hole in the rim. The face skirt has its own bumps that click into
the same holes from outside, and once it is on, it stops the rim from
opening, so the grid cannot come out.

```
   section through the rim at a click point

        face ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
                              █ ← skirt
   grid  ┃▀▀▀▀ bridge ▀▀▀▀●○● ║ ← bump in the rim hole, from both sides
         ┃                  ║ █
         ┃   margin         ║
   ━━━━━━┻━━━━━━━━━━━━━━━━━━╝   tray: back plate and rim
```

To open it, pull the face skirt off at one corner, then lift the grid:
the rim gives way a little and lets the bumps out.

### Wires and camera

The strip input wires run in the margins, hidden behind the face border:
from the start of row 0 down the side margin, then along the bottom margin
to one of two 20 × 12 mm holes in the back plate, one on each side of the
seam. The holes sit behind the stand box, so the wires go straight into
it.

The camera board sits on four posts in the bottom margin, its lens
against the back of the face, behind one of the bottom rivets, which is a
through window. It is next to the left cable hole, so its flat cable goes
straight through the hole into the stand box, a few centimetres away. The board size, hole
positions and lens position are parameters (`cam_*` in
`wordclock/cad/matrix.scad`), set for the Raspberry Pi Camera v1.3:
measure your board before printing the tray.

```
   front view, left half

   ┌──────────────────────────────────────
   │ ║┌──────┬──────┬──────┬──────┬───
   │ ║│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ row 0 strip, DIN on the left
   │ ║┼──────┼──────┼──────┼──────┼───
   │ ║   ⋮      wires down the side margin
   │ ║└──────┴──────┴──────┴──────┴───
   │ ╚═══════════════[◉ camera]▣  ← 20 × 12 mm hole, behind the box
   └──────────────────────────────────────
```

---

## 4. Stand box

A compact box at the bottom of the back holds the Raspberry Pi and the
wiring. The same box works on a table and on a wall:

| Where | How it holds |
|-------|--------------|
| Table | The base of the box is cut at 15°: the matrix leans back, on the bottom edge of the tray and the base of the box |
| Wall | Two keyholes in the back of the box hang on two screws; the back of the box rests flat on the wall, 4 cm behind the grid |

Only the power cable comes out, from the side of the box, in both cases.

```
   side view (front on the left)

   on a table                         on a wall

          face  grid                   │ ┃ grid
              ╱   ╱                    │ ┃
             ╱   ╱                     │ ┃
            ╱   ╱━━━╱  stand box       │ ┃
           ╱   ╱   ╱                   │ ┃┏━━━┓ stand box
   ══════╱═══╱━━━╱════  table          │ ┃┃   ┠── screw in the wall
          15° lean back                │ ┃┗━━━┛
                                       wall
```

### Slide lock

The box slides onto the tray, without screws or clips. Four pins on
columns of the box have a wide conical head. They go through the wide end
of four keyhole slots in the tray back plate, on the row lines between
rows 3, 4 and 5, and the box slides 10 mm down. The heads then hold the
box against the back plate, and the cones pull it tight. Each slot crosses
under a grid row wall through a 3,8 mm tunnel, and the heads stay between the
strips, 1 mm clear of the 13 mm strip notch.

```
   keyhole slot (front view)        pin of the box (side view)

        ╭───╮                           ▄███▄  head Ø8, cone under it
        │   │  ← head goes in here        ▀█▀
   ═════╰┐ ┌╯═════ row wall,          ════█════  tray back plate (2 mm)
         │ │       tunnel under it         █
         │ │  ← box slides 10 mm down      █    column Ø10
         ╰─╯     and stays locked       ▀▀▀▀▀▀▀  floor of the stand box
```

Gravity keeps the box locked, on a table and on a wall. To take it off,
lay the matrix face down, slide the box 10 mm up and lift it.

### Inside the box

```
          seen from the back

   ┌─────────────────────────────────────┐  ← top wall: window for the
   │      ▄▄  ┌──── port window ───┐ ▄▄  │    micro-USB and HDMI plugs
   │ ◉ ┌─────────────────────────────┐ ◉ │
   │   │                             │   │
 ▯ │   │ ← microSD    Raspberry Pi   │   │ ≡ vents
   │   │   slot       3B       USB → │   │ ≡
   │ ◉ └────────────────────▀▀▀▀▀────┘ ◉ │
   │      ○ wall keyhole ○  hook        ◯ ← DC jack
   │      plug and wiring room           │
   └─────────────────────────────────────┘
   ▔▔▔▔▔▔▔▔▔▔▔▔▔ base on the table ▔▔▔▔▔▔▔▔▔▔
```

The view is from the back, so left and right are swapped against the
model, which uses front-view coordinates.

The Raspberry Pi lies across the box between the pin columns, the port
edge at the top. It clicks in without screws: four standoffs with short
pegs go into its holes, two lips on the top wall hold the port edge, and a
snap hook holds the bottom edge.

```
   click mount (section through the board)

    top wall                           snap hook
   ║ ▄▄ lip                       hook ▄ ║
   ║ ▀█▄▄▄▄▄▄▄▄▄▄ board ▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ▀█
   ║   ▐▌ peg                   peg ▐▌   █ ← arm flexes out
   ║   ██ standoff         standoff ██   █
   ╚═══════════════ floor ════════════════
```

1. Slide the port edge of the board under the two lips on the top wall,
   ports towards the window.
2. Lower the bottom edge onto the pegs and press until the hook clicks
   over it.
3. To take it out, push the hook away from the board and lift that edge.

| Opening | Where | For |
|---------|-------|-----|
| DC jack, 11 mm | Side wall, low | The 5V supply: the only cable in the finished matrix |
| Port window, 41 × 15 mm | Top wall | Micro-USB and HDMI plugs: power the Pi straight from a USB charger, or plug a screen in |
| microSD slot, 16 × 8 mm | Other side wall | Reach the card with a fingernail or tweezers |
| Wall keyholes, 60 mm apart | Back | Two screws with heads up to 8 mm |
| Cable holes, 20 × 12 mm | Tray back plate, bottom margin, inside the box | Strip input wires and camera cable, never outside |
| Vents | Back under the Pi, and a side wall | Air for the Raspberry Pi |

To hang it on a wall, drive two screws 60 mm apart on a level line, with
5 mm of the screw left out, and lower the keyholes onto them.

To make the matrix stand steeper or flatter, change `tilt`; a deeper box
(`box_d`) gives a longer base and a steadier stand.

Wiring inside the box:

```
 DC jack + ──► Wago 5V ──┬──────────────────► strip 5V (red)
                         ├──[1000 µF]──┐
                         └──────────────────► micro-USB plug + ──► Pi power
 DC jack − ──► Wago GND ─┴─────────────┴────► strip GND (white)
                         └──────────────────► micro-USB plug − 
 Pi GPIO 18 (pin 12) ──[220 Ω]──────────────► strip DIN (green)
```

The Pi takes its power through its own micro-USB port, from the same
supply, so it keeps its input protection. The micro-USB cable also joins
the Pi GND to the strip GND. Hold the Wago connectors and the capacitor
with double-sided tape.

---

## 5. Print the enclosure

```bash
uv run wordclock-cad --matrix    # STL files in build/stl/matrix/
```

It writes four Bambu Studio projects, one part per plate:

| Project | Parts | Filament | Orientation |
|---------|-------|----------|-------------|
| `build/bambu/matrix_tray.3mf` | `tray_left`, `tray_right` | White PLA, 3 walls, 15 % infill | Back plate on the bed |
| `build/bambu/matrix_grid.3mf` | `grid_left`, `grid_right` | White PLA, 3 walls, 15 % infill | Upside down: bridges on the bed |
| `build/bambu/matrix_face.3mf` | `face_left`, `face_right` | Black PLA, 100 % infill | Front on the bed, skirt up |
| `build/bambu/matrix_box.3mf` | `box` | Black PLA, 3 walls, 15 % infill | Floor on the bed |

To change a size, edit the parameters at the top of
`wordclock/cad/matrix.scad` (wall height, margin, notch width, box depth,
jack hole) and render
again. Open the file in the OpenSCAD GUI to see the assembly.

---

## 6. Cut and wire the strip

### 6.1 Snake layout

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

### 6.2 Steps

1. Check the arrows printed on the strip: they point away from DIN. Start
   from the DIN end.
2. Cut 6 pieces of 10 LEDs (33,3 cm each) on the copper cut marks.
3. Bolt the two tray halves together (section 7, step 1), so the rows run
   straight across the seam.
4. Stick each piece on the tray, between the two guide grooves of its row,
   arrows pointing in the direction of the row (right on rows 0, 2 and 4,
   left on rows 1, 3 and 5). The grid is not on yet: the plate is flat.
5. Solder three wires (5V, data, GND) from the DOUT end of each row to the
   DIN end of the next one, in the side margin. Keep the colours the same
   on every joint, and keep the joints flat on the plate, clear of the
   grid walls.
6. Solder the input wires to the DIN end of row 0, about 40 cm long. Run
   them down the side margin and along the bottom margin, and pass them
   through the nearest 20 × 12 mm hole in the back plate.

> ⚠️ Data goes from DOUT to DIN only. A row stuck the wrong way round stays
> dark, and so does every row after it.

### 6.3 Connection to the Raspberry Pi

Test first on the breadboard, as in the bench test ([06 — Bench Test](06-bench-test.md), section 2),
then move the wiring into the stand box (section 4):

| From | To | Note |
|------|----|------|
| Pi GPIO 18 (pin 12) | 220 Ω resistor → strip DIN | Data line |
| Supply + | Strip 5V and micro-USB plug + | Never to the Pi GPIO pins |
| Supply − | Strip GND and micro-USB plug − | Common ground through the micro-USB cable |
| 1000 µF capacitor | Between strip 5V and GND, at the input | Stripe (negative) to GND |

60 LEDs draw up to 3,6 A in full white. The software dims any frame that
would draw more than 1,5 A (`MATRIX_MAX_MA` in `wordclock/config.py`); with
the Pi 3B (up to about 1,2 A) that needs a 3 A supply at least. If the
colours flicker, use the diode trick from the bench test.

### 6.4 Quick test powered from the Raspberry Pi

To try the strip before the 5V supply arrives, power it from the Pi's own
5V pin, with only the Pi's power cable plugged in.

```
 Raspberry Pi 3B
   pin 2  (5V) ─────────────────────► strip 5V (red)
   pin 6  (GND) ────────────────────► strip GND (white)
   pin 12 (GPIO 18) ──[220 Ω]───────► strip DIN (green)
```

The Pi 3B supply gives 2,5 A, the Pi uses 0,5–1 A of it, and the
micro-USB input has a fuse of about 2,5 A. That leaves about 1 A for the
LEDs, so keep the software limit low:

```bash
sudo .venv/bin/wordclock-matrix wiring --brightness 30 --max-ma 600
sudo .venv/bin/wordclock-matrix rainbow --brightness 30 --max-ma 600
```

| Symptom | Fix |
|---------|-----|
| The Pi reboots, or shows the under-voltage warning | Lower `--max-ma`; `vcgencmd get_throttled` must print `throttled=0x0` |
| Random colours or flicker | Put the rectifier diode between pin 2 and the strip 5V, stripe towards the strip |

> ⚠️ Never run without `--max-ma`: 60 LEDs in full white draw 3,6 A and
> would reset the Pi. Do not connect or disconnect the strip while the Pi
> is on.

For the finished matrix, use the DC jack of the stand box (section 4): it
powers the strip and the Pi together without going through the Pi's fuse,
so the limit can stay at 1,5 A.

---

## 7. Assemble

1. Bolt the two tray halves together with the two M3 bolts, in the blocks
   in the top and bottom margins.
2. Stick the strip rows and solder the joints on the open tray (section 6).
3. Run the `wiring` scene (section 8) and check that the cells light in
   order. A bad joint is still easy to reach.
4. Optional: press the camera board onto the pegs of its four posts in the
   bottom margin, lens up, and pass its flat cable through the cable hole
   next to it.
5. Click the two grid halves into the tray: lower each half straight
   down, the strip under the wall notches, until the four bumps click into
   the rim.
6. Lay the tracing paper over the grid, cut to the outer edge of the
   grid walls, so it does not cover the margins or the camera.
7. Press the two face halves onto the tray until their skirts click over
   the rim.
8. Click the Raspberry Pi into the stand box (section 4) and fit the DC
   jack in the side wall. Wire the strip input wires inside the box
   (section 4), with about 2 cm of slack for the 10 mm slide.
9. Lay the matrix face down. Put the four pin heads into the wide ends of
   the keyhole slots and slide the box 10 mm down, towards the bottom edge,
   until its base lines up with the bottom of the tray.
10. Stand the matrix on the table, or hang it on the wall (section 4), and
    plug in the power cable.

---

## 8. Software

The matrix uses the `wordclock-matrix` command. On the Mac, `--mock` draws
the matrix in the terminal instead of lighting LEDs:

```bash
uv run wordclock-matrix --mock show
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
| `show` | The default: every scene in turn, with new colours each time (section 9) |
| `text` | Scrolling text (`--text`), 3 × 5 pixel font on the bottom five rows, accents folded (`à` → `A`) |
| `clock` | The time as `HH:MM`, scrolling |
| `ip` | The local IP address, scrolling |
| `rain` | Green drops with fading trails, like Matrix rain |
| `rainbow` | A rainbow sliding diagonally |
| `sparkle` | Cells that light up in random colours and fade out |
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

## 9. Start the show on boot

The `show` scene plays on its own, without a keyboard or a network. It
starts with the IP address once, then repeats forever:

```
   IP ──► clock ──► text ──► effect ──► clock ──► text ──► drawing ──► …
          HH:MM                rainbow,                     heart, smile,
                               rain or sparkles             ZZZ at night
```

| Part | Content | Time |
|------|---------|------|
| Clock | `HH:MM`, a random colour or rainbow letters | One pass across the matrix |
| Text | One text that fits the moment (table below), or a personal one | One pass across the matrix |
| Effect | `rainbow` at a random speed, `rain` in a random colour, or `sparkle` | 15 s |
| Drawing | A red heart or a smile; `ZZZ` from 23:00 to 06:59. It pulses like a heartbeat | 6 s |

Every scene fades in and out over 0,5 s.

| Text | When |
|------|------|
| `BON DIA` / `BONA TARDA` / `BONA NIT` | 06–13 h / 13–20 h / 20–06 h |
| `24 OCT` | Always |
| `FALTEN 3 DIES PER DIVENDRES`, `DEMÀ ÉS DIVENDRES!` | Monday to Thursday |
| `BON CAP DE SETMANA!` | Friday from 15:00 |
| `BON DISSABTE`, `BON DIUMENGE` | Weekend |
| `HORA DE DINAR` / `HORA DE SOPAR` | 13–15 h / 20–22 h |
| `A DORMIR!` | 23:00 to 06:59 |

### Personal texts

Names and dates stay out of the public repository, in `matrix.toml` next
to the code on the Pi (`~/word-clock/matrix.toml`, ignored by git). The
show mixes the messages with the texts above. On a date of the list, half
of the texts are that date's own.

```toml
# Shown any day
messages = ["HOLA ENRIC", "♥ CASA ♥"]

# Shown on one day of every year, "MM-DD"
[dates]
"03-14" = "FELICITATS ANNA!"
"12-25" = ["BON NADAL!", "♥ ♥ ♥"]
```

The show reads the file when it starts: restart the service after editing
it. A missing or broken file only leaves the personal texts out
(`journalctl` says why). `--config` reads another file.

A systemd service starts the show when the Pi boots. Create it on the Pi:

```bash
sudo nano /etc/systemd/system/wordclock-matrix.service
```

```ini
[Unit]
Description=Mini LED matrix show
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/eballo/word-clock
ExecStart=/home/eballo/word-clock/.venv/bin/wordclock-matrix show
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace `/home/eballo` with your user's home directory. Enable and start
it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now wordclock-matrix
sudo systemctl status wordclock-matrix
```

| Command | Use |
|---------|-----|
| `sudo systemctl stop wordclock-matrix` | Stop the show and turn the LEDs off, e.g. to run another scene by hand |
| `sudo systemctl start wordclock-matrix` | Start it again |
| `sudo systemctl disable wordclock-matrix` | Do not start it on boot any more |
| `journalctl -u wordclock-matrix -f` | Follow its log |

> ⚠️ Stop the service before running `wordclock-matrix` by hand: two
> programs driving GPIO 18 at once garble the strip.

---

## 10. Build checklist

- [ ] Tray, grid and face halves and the stand box printed (`uv run wordclock-cad --matrix`)
- [ ] Tray halves bolted together with two M3 × 16 mm bolts
- [ ] Raspberry Pi clicked into the stand box, DC jack fitted, box slid onto the tray
- [ ] Strip cut into 6 pieces of 10 LEDs, stuck on the open tray in a snake, arrows checked
- [ ] Five row joints soldered, input wires along the margins and through the hole behind the box
- [ ] Quick test powered from the Pi (section 6.4): `wiring` scene with `--max-ma 600`
- [ ] Safety check of [06 — Bench Test](06-bench-test.md) done before powering up
- [ ] `wiring` scene lights the 60 cells in order
- [ ] `rainbow` scene shows the right colours
- [ ] Grid clicked in, tracing paper cut to the grid, face clicked on
- [ ] Optional: camera on its posts, lens behind the rivet window
- [ ] `text`, `clock`, `ip` and `rain` scenes running
- [ ] `wordclock-matrix` service enabled: the show starts when the matrix is plugged in
- [ ] Matrix on the table or on the wall, only the power cable showing
