# 04 — Assembly

## Overview

The clock is assembled in four main layers, stacked from back to front:

```
        WALL
         │
    ┌────┴────┐
    │  Back   │  ← SANNAHED back board + printed Raspberry Pi box
    ├─────────┤
    │  LED    │  ← bullet pixels in the 3D-printed light grid
    │  matrix │
    ├─────────┤
    │  Front  │  ← 3D-printed front panel (letters) + frame glazing
    └─────────┘
         │
       viewer
```

---

## 1. 3D printing

All printed parts — front panel, light grid and Raspberry Pi box — are
described in [05 — Enclosure](05-enclosure.md), together with the render
commands and the Bambu Lab A1 print settings. Print the 4 × 4 test corner
first to check fit, letters and light bleed.

---

## 2. LED matrix assembly

### 2.1 Join the light grid

Bolt the four grid tiles together through the seam holes with M3 × 8 mm
bolts and nuts. The result is one 48,4 × 48,4 cm grid with 256 cells.

### 2.2 Fit the pixels

Push one 12 mm bullet pixel into each back plate hole from behind, in snake
order. Label each string before you start so you do not lose track of the
order.

| Row | LEDs | Direction |
|-----|------|-----------|
| 0 | 0–15 | left → right |
| 1 | 16–31 | right → left |
| 2 | 32–47 | left → right |
| ... | ... | alternating |
| 15 | 240–255 | right → left |

### 2.3 Route the wiring

Fold the spare wire between pixels flat behind the back plate. Where one
string ends, join it to the next with a JST connector.

### 2.4 Join the strings

Chain the pixel strings in a snake pattern with 3-wire connectors (VCC, GND, DATA):

```
row 0  DOUT ──► row 1  DIN
row 1  DOUT ──► row 2  DIN
...
row 14 DOUT ──► row 15 DIN
```

Use 22 AWG wire for the power injection leads. Run VCC and GND in parallel to the injection points — do not chain power through the data line.

> ⚠️ Add an additional power injection point at row 8 (the midpoint) to avoid voltage drop across the matrix.

---

## 3. Electronics

### 3.1 Level shifter

Connect the level shifter between the Raspberry Pi GPIO 18 and the LED strip data line:

```
Raspberry Pi GPIO 18 (3,3V) ──► IN   74AHCT125   OUT ──► LED strip DIN
Raspberry Pi GND             ──► GND
5V PSU                       ──► VCC
```

### 3.2 Power wiring

```
5V PSU (+) ──────────────────────────── LED strip VCC (row 0)
                                    └── LED strip VCC (row 8)  ← injection
5V PSU (−) ──────────────────────────── LED strip GND (row 0)
                                    └── LED strip GND (row 8)  ← injection
5V PSU (−) ──── Raspberry Pi GND   (common ground)
```

> ⚠️ Never power the LED strip through the Raspberry Pi's 5V pin. Always connect the strip directly to the PSU.

### 3.3 Raspberry Pi placement

Mount the Raspberry Pi Zero 2 W and the level shifter in the printed box on the back of the SANNAHED back board (see [05 — Enclosure](05-enclosure.md)). Route the 3-wire LED cable through a hole in the back board to row 0 (top-left corner).

---

## 4. Final assembly

Follow this order when putting the clock together:

1. **Place the front panel** face down in the frame, against the glazing, then the light grid with the pixels on top
2. **Connect all wiring** — data, power, ground — and double-check polarity
3. **Power on briefly** (without the front panel) and run the mock test to verify all LEDs respond:
   ```bash
   sudo .venv/bin/wordclock --debug
   ```
4. **Check for dead or flickering LEDs** and re-solder any bad joints
5. **Close the SANNAHED back board** so it clamps the stack
6. **Screw the Raspberry Pi box** onto the back board
7. **Power on the full assembly** and verify the time displays correctly via the web interface at `http://wordclock.local:5000`

---

## 5. Wall mounting

Hang the clock from the SANNAHED hanging fitting, or with two ALFTA adhesive
hooks. If the Raspberry Pi box is screwed to the back board, stick two
24 mm felt pads to the bottom corners so the frame hangs straight.

> Route the power cable through the bottom of the frame, down the wall, and to a nearby socket. Use a cable raceway for a clean finish.

---

## 6. Assembly checklist

- [ ] Light grid tiles bolted together
- [ ] 256 pixels fitted in snake order
- [ ] All string connections done and tested
- [ ] Power injection at row 0 and row 8
- [ ] Level shifter wired and tested
- [ ] Common ground between PSU and Raspberry Pi
- [ ] Raspberry Pi box screwed to the back board
- [ ] Front panel and grid clamped in the frame
- [ ] Full power-on test passed (all LEDs respond)
- [ ] systemd service running on boot
- [ ] Clock accessible at `http://wordclock.local:5000`
- [ ] Mounted level on the wall
