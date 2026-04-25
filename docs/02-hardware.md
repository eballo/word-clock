# 02 — Hardware

## Overview

The clock is built around a 16×16 matrix of individually addressable WS2812B LEDs mounted inside a 65×65 cm frame.
A 3D-printed front panel with letter-shaped through-holes sits in front of the matrix.
Only the letters that correspond to the current time are lit up, so only those letters are visible through the panel.

---

## Dimensions

```
┌─────────────────────────────────────────────────┐
│                   65 cm                         │
│   ┌─────────────────────────────────────────┐   │
│   │                                         │   │
│   │           LED matrix                    │   │ 65 cm
│   │           53,3 × 53,3 cm                │   │
│   │           16 × 16 = 256 LEDs            │   │
│   │                                         │   │
│   └─────────────────────────────────────────┘   │
│          ~5,85 cm margin on each side           │
└─────────────────────────────────────────────────┘
```

| Measurement | Value |
|-------------|-------|
| Frame (total) | 65 × 65 cm |
| LED matrix area | 53,3 × 53,3 cm |
| Margin (each side) | ~5,85 cm |
| Cell size | 3,33 × 3,33 cm |
| Letter size (approx.) | ~23 mm |
| Grid | 16 × 16 = 256 LEDs |

---

## Components

### LED strip

| Parameter | Value |
|-----------|-------|
| Model | WS2812B |
| Density | 30 LEDs/metre |
| Pitch | 3,33 cm between LEDs |
| Voltage | 5V DC |
| LEDs needed | 256 (16 × 16) |
| Strip length needed | ~9 metres (16 rows × 53,3 cm + connectors) |

The strip is cut into 16 rows of 16 LEDs each and wired in a snake pattern — left to right on even rows, right to left on odd rows.

```
row  0 →  LED   0 ..  15   (left → right)
row  1 ←  LED  16 ..  31   (right → left)
row  2 →  LED  32 ..  47   (left → right)
...
row 15 ←  LED 240 .. 255   (right → left)
```

### 3D-printed front panel

The front panel is printed in opaque black filament (PLA or PETG). Each cell is 3,33 × 3,33 cm with a letter-shaped through-hole. The panel depth should be at least 15 mm to prevent light from bleeding between adjacent cells.

| Parameter | Value |
|-----------|-------|
| Panel size | 53,3 × 53,3 cm |
| Cell size | 3,33 × 3,33 cm |
| Letter size | ~23 mm |
| Wall between cells | ~5 mm |
| Minimum depth | 15 mm |
| Filament | PLA or PETG, opaque black |

> **Note:** Because the panel is large (53×53 cm), it will likely need to be printed in sections and assembled. Plan the section joints to fall on the walls between cells, not through a letter opening.

### Raspberry Pi

Any Raspberry Pi with GPIO support will work. The LED strip data line connects to **GPIO 18** (PWM).

| Parameter | Value |
|-----------|-------|
| GPIO pin | GPIO 18 (PWM) |
| Protocol | WS2812B (800 kHz) |
| Logic level | 3,3V → 5V level shifter recommended |

> **Note:** The WS2812B data line runs at 5V logic. A level shifter between the Raspberry Pi (3,3V) and the strip is recommended to avoid signal issues, especially with long strips.

### Power supply

With 256 LEDs at a maximum of 60 mA each (full white), the theoretical peak draw is ~15A at 5V. In practice, a word clock never lights all LEDs at once — typical usage lights 20–40 LEDs at a time.

| Parameter | Value |
|-----------|-------|
| Voltage | 5V DC |
| Recommended supply | 5V 10A (50W) |
| Connector | Power the strip directly from the PSU, not through the Raspberry Pi |

> **Important:** Always power the LED strip directly from the power supply. Never draw more than 2–3A through the Raspberry Pi's GPIO pins.

---

## Wiring diagram

```
                    5V PSU (10A)
                   ┌────────────┐
                   │ + (5V)     ├──────────────────── LED strip VCC (red)
                   │ - (GND)    ├──────────────────── LED strip GND (black)
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
| 1 | WS2812B LED strip | 30 LEDs/metre, ~9 metres |
| 2 | Raspberry Pi | Any model with GPIO (Pi 3B+ or Pi 4 recommended) |
| 3 | Power supply | 5V 10A (50W) |
| 4 | Level shifter | 3,3V → 5V (e.g. 74AHCT125) |
| 5 | Frame | 65 × 65 cm, minimum 4 cm depth |
| 6 | 3D-printed front panel | 53,3 × 53,3 cm, opaque black PLA/PETG |
| 7 | Diffuser (optional) | Frosted acrylic sheet, 53,3 × 53,3 cm |
| 8 | JST connectors | For joining strip rows |
| 9 | Wire | 3-core, 22 AWG |
| 10 | MicroSD card | For Raspberry Pi OS (16 GB minimum) |

---

## Optional: diffuser

A frosted acrylic sheet placed between the LED strip and the front panel softens the light and makes each lit letter glow more evenly. Without it, the individual LED point may be visible through the letter opening at close range.
