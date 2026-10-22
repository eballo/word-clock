# 02 — Hardware

## Overview

The clock is built around a 16×16 matrix of letters lit by a WS2812B LED strip (144 LEDs/metre, 4 LEDs per letter) inside an IKEA SANNAHED 50×50 cm frame.
A 3D-printed front panel with letter-shaped holes sits in front of a 3D-printed light grid that holds the strips.
Only the letters that correspond to the current time are lit up, so only those letters are visible through the panel.

---

## Dimensions

```
┌─────────────────────────────────────────────┐
│              SANNAHED 50 cm                 │
│ ┌─────────────────────────────────────────┐ │
│ │                                         │ │
│ │           LED matrix                    │ │ 50 cm
│ │           44,4 × 44,4 cm                │ │
│ │           16 × 16 cells, 4 LEDs each    │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│       inner opening 48,5 × 48,5 cm          │
└─────────────────────────────────────────────┘
```

| Measurement | Value |
|-------------|-------|
| Frame (total) | 50 × 50 cm, 5 cm deep (IKEA SANNAHED) |
| Frame inner opening | 48,5 × 48,5 cm |
| Depth used | 4 cm |
| Panel size | 48,4 × 48,4 cm |
| LED matrix area | 44,4 × 44,4 cm |
| Cell size | 2,78 × 2,78 cm |
| Letter size (cap height) | 15 mm |
| Grid | 16 × 16 cells = 1 024 LEDs (4 per cell) |

See [05 — Enclosure](05-enclosure.md) for the printed parts.

---

## Components

### LED strip

A 30 LEDs/metre strip has a fixed 3,33 cm pitch: 16 LEDs need 53,3 cm and do
not fit in the frame. A 144 LEDs/metre strip has a 6,94 mm pitch, so four
LEDs make one 2,78 cm cell. Four LEDs per letter also light it more evenly.

| Parameter | Value |
|-----------|-------|
| Model | WS2812B, 144 LEDs/metre, 10 mm wide, IP30 |
| Voltage | 5V DC |
| LEDs per cell | 4 |
| LEDs needed | 1 024 (16 rows × 64) |
| Strip needed | 8 reels of 1 m (2 rows per reel) |

The rows are wired in a snake pattern — left to right on even rows, right to left on odd rows.

```
row  0 →  LED   0 ..   63   (left → right)
row  1 ←  LED  64 ..  127   (right → left)
row  2 →  LED 128 ..  191   (left → right)
...
row 15 ←  LED 960 .. 1023   (right → left)
```

### 3D-printed front panel and light grid

The front panel is a 2,4 mm opaque black face with stencil letter holes
(Karla Bold Stencil), with a sheet of tracing paper behind it to diffuse
the light. Behind the paper, a white light grid with 25 mm walls isolates
each cell so light does not bleed into the neighbouring letters. The strips
lie on the back plate of the grid.

| Parameter | Value |
|-----------|-------|
| Panel size | 48,4 × 48,4 cm |
| Cell size | 2,78 × 2,78 cm |
| Letter size | 15 mm cap height, Karla Bold Stencil |
| Grid wall | 1,2 mm |
| Grid depth | 25 mm + 2 mm back plate |
| Filament | Black PLA/PETG (face), white PLA (grid) |
| Diffuser | Tracing paper, 45,5 × 45,5 cm |

> **Note:** The face and the grid are printed in a 3×3 split of tiles (at
> most 17,1 × 17,1 cm) to fit the 25 × 25 cm bed of the Bambu Lab A1. Seams
> fall on the walls between cells.

### Raspberry Pi

The clock uses a Raspberry Pi 3B in the screen module under the frame, behind the official 7" Touch Display. A Raspberry Pi 4B fits the same module (same footprint and DSI connector) when more power is needed, for example for face recognition. The LED strip data line connects to **GPIO 18** (PWM), the camera uses the camera connector and the push button uses GPIO 3.

| Parameter | Value |
|-----------|-------|
| Model | Raspberry Pi 3B (Raspberry Pi 4B as an upgrade) |
| Display | Raspberry Pi Touch Display v1, 7", 800 × 480, DSI |
| GPIO pin | GPIO 18 (PWM) |
| Button | GPIO 3 to GND (also wakes the Pi from halt) |
| Camera | 5 MP OV5647 board or Camera Module 1.3/2/3, 15-pin cable |
| Protocol | WS2812B (800 kHz) |
| Logic level | 3,3V → 5V level shifter recommended |

> **Note:** The WS2812B data line runs at 5V logic. A level shifter between the Raspberry Pi (3,3V) and the strip is recommended to avoid signal issues, especially with long strips.

### Power supply

With 1 024 LEDs at a maximum of 60 mA each (full white), the theoretical peak draw is ~60 A at 5V. In practice, a word clock never lights all LEDs at once: a typical sentence lights 25–35 letters, or 100–140 LEDs. The software limits the LED current to stay within the supply.

| Load | Current at 5V |
|------|---------------|
| 35 letters, full white (140 LEDs) | ~8,4 A (limited by software) |
| 35 letters, one colour | ~2,8 A |
| Idle LEDs (1 024 × ~0,5–1 mA) | ~0,5–1 A |
| Raspberry Pi 3B/4B + display + camera | ~1,5–2,5 A |

| Parameter | Value |
|-----------|-------|
| Voltage | 5V DC |
| Recommended supply | 5V 10A (50W) |
| LED current limit | ~6 A (software) |
| Power injection | Rows 0, 4, 8 and 12 |
| Connector | Panel-mount DC jack rated for 10 A. Power the strip directly from the PSU, not through the Raspberry Pi |

> **Important:** Always power the LED strip directly from the power supply. Never draw more than 2–3A through the Raspberry Pi's GPIO pins.

---

## Wiring diagram

```
                    5V PSU (10A)
                   ┌────────────┐
                   │ + (5V)     ├──────────────────── LED strip VCC (rows 0, 4, 8, 12)
                   │ - (GND)    ├──────────────────── LED strip GND (rows 0, 4, 8, 12)
                   └──────┬─────┘
                          │ GND
                   ┌──────┴─────┐
                   │Raspberry Pi│
                   │  GPIO 18   ├── level shifter ──── LED strip DATA (green)
                   │  GND       ├────────────────────  GND (common)
                   └────────────┘
```

---

## Bill of materials

| # | Component | Specification |
|---|-----------|---------------|
| 1 | LED strip | WS2812B, 144 LEDs/metre, 5V, IP30, 8 reels of 1 m |
| 2 | Raspberry Pi | Raspberry Pi 3B (or 4B) + Touch Display v1 (in the screen module) |
| 3 | Power supply | 5V 10A (50W) |
| 4 | Level shifter | 3,3V → 5V (e.g. 74AHCT125) |
| 5 | Frame | IKEA SANNAHED 50 × 50 cm |
| 6 | 3D-printed parts | Face, light grid, screen module (see 05 — Enclosure) |
| 7 | Bolts | 24 × M3 × 8 mm with nuts (grid seams); screen module: 4 × M3 countersunk + 4 M3 heat-set inserts (back cover), 4 × M3 countersunk with nuts (hanger), 2 × M3 × 10 mm with washers and nuts (studs) |
| 8 | Power wire | 2-core, 18 AWG (power injection) |
| 9 | Wire | 3-core, 22 AWG (row jumpers) |
| 10 | MicroSD card | For Raspberry Pi OS (16 GB minimum) |
| 11 | Tracing paper | 90 g/m², 45,5 × 45,5 cm (light diffuser) |
| 12 | Camera | 5 MP OV5647 board or Raspberry Pi Camera Module |
| 13 | Push button | 7–12 mm panel-mount momentary button |
| 14 | DC jack | Panel-mount, rated for 10 A |
| 15 | Magnets | Neodymium discs 5 × 2 mm, 24 (+12 per extra language face) |

---
