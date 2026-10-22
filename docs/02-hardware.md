# 02 — Hardware

## Overview

The clock is built around a 16×16 matrix of individually addressable WS2812B LEDs mounted inside an IKEA SANNAHED 50×50 cm frame.
A 3D-printed front panel with letter-shaped holes sits in front of a 3D-printed light grid that holds one pixel per cell.
Only the letters that correspond to the current time are lit up, so only those letters are visible through the panel.

---

## Dimensions

```
┌─────────────────────────────────────────────┐
│              SANNAHED 50 cm                 │
│ ┌─────────────────────────────────────────┐ │
│ │                                         │ │
│ │           LED matrix                    │ │ 50 cm
│ │           48,0 × 48,0 cm                │ │
│ │           16 × 16 = 256 LEDs            │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│       inner opening 48,5 × 48,5 cm          │
└─────────────────────────────────────────────┘
```

| Measurement | Value |
|-------------|-------|
| Frame (total) | 50 × 50 cm (IKEA SANNAHED) |
| Frame inner opening | 48,5 × 48,5 cm |
| Panel size | 48,4 × 48,4 cm |
| LED matrix area | 48,0 × 48,0 cm |
| Cell size | 3,0 × 3,0 cm |
| Letter size (cap height) | 16 mm |
| Grid | 16 × 16 = 256 LEDs |

See [05 — Enclosure](05-enclosure.md) for the printed parts.

---

## Components

### LED pixels

A 30 LEDs/metre strip has a fixed 3,33 cm pitch: 16 LEDs need 53,3 cm and do
not fit in the frame. The clock uses individual 12 mm bullet pixels instead,
pushed into the back plate of the light grid at a 3,0 cm pitch.

| Parameter | Value |
|-----------|-------|
| Model | 12 mm bullet pixel, WS2811 or WS2812B |
| Voltage | 5V DC |
| Pitch | 3,0 cm (set by the light grid) |
| Pixels needed | 256 (16 × 16), e.g. 6 strings of 50 |
| Wire between pixels | 5–10 cm (spare wire folds behind the grid) |

The pixels are wired in a snake pattern — left to right on even rows, right to left on odd rows.

```
row  0 →  LED   0 ..  15   (left → right)
row  1 ←  LED  16 ..  31   (right → left)
row  2 →  LED  32 ..  47   (left → right)
...
row 15 ←  LED 240 .. 255   (right → left)
```

### 3D-printed front panel and light grid

The front panel is a 2,4 mm opaque black face with stencil letter holes
(Karla Bold Stencil), with a sheet of tracing paper behind it to diffuse
the light. Behind the paper, a white light grid with 20 mm
walls isolates each cell so light does not bleed into the neighbouring
letters.

| Parameter | Value |
|-----------|-------|
| Panel size | 48,4 × 48,4 cm |
| Cell size | 3,0 × 3,0 cm |
| Letter size | 16 mm cap height, Karla Bold Stencil |
| Grid wall | 1,2 mm |
| Grid depth | 20 mm + 2 mm back plate |
| Filament | Black PLA/PETG (face), white PLA (grid) |
| Diffuser | Tracing paper, 48,4 × 48,4 cm |

> **Note:** Every part is printed in a 2×2 split of 24,2 × 24,2 cm tiles to fit
> the Bambu Lab A1 bed. Seams fall on the walls between cells.

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
| 1 | Bullet pixels | 12 mm, WS2811/WS2812B, 5V, 256 units |
| 2 | Raspberry Pi | Pi Zero 2 W (fits the printed box) or any model with GPIO |
| 3 | Power supply | 5V 10A (50W) |
| 4 | Level shifter | 3,3V → 5V (e.g. 74AHCT125) |
| 5 | Frame | IKEA SANNAHED 50 × 50 cm |
| 6 | 3D-printed parts | Face, light grid, Pi box (see 05 — Enclosure) |
| 7 | Bolts | 8 × M3 × 8 mm with nuts (grid seams) |
| 8 | JST connectors | For joining pixel strings |
| 9 | Wire | 3-core, 22 AWG |
| 10 | MicroSD card | For Raspberry Pi OS (16 GB minimum) |
| 11 | Tracing paper | 90 g/m², 48,4 × 48,4 cm (light diffuser) |
| 12 | Camera | Raspberry Pi Camera Module 3 + Pi Zero camera cable |
| 13 | Push button | 12 mm panel-mount momentary button |

---
