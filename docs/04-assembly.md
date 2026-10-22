# 04 — Assembly

## Overview

The clock is assembled in four main layers inside the SANNAHED frame,
stacked from back to front:

```
        WALL
         │
    ┌────┴────┐
    │  Back   │  ← SANNAHED back board + Raspberry Pi tray (10 mm gap)
    ├─────────┤
    │  LED    │  ← WS2812B strips on the 3D-printed light grid
    │  matrix │
    ├─────────┤
    │  Front  │  ← tracing paper + 3D-printed front panel + frame glazing
    └─────────┘
         │
       viewer
```

---

## 1. 3D printing

All printed parts — front panel, light grid (with the camera bracket) and
Raspberry Pi tray — are described in [05 — Enclosure](05-enclosure.md), together with the
render commands and the Bambu Lab A1 print settings. Print the 4 × 4 test
corner first to check fit, letters and light bleed.

---

## 2. LED matrix assembly

### 2.1 Join the light grid

Press the dovetail tabs of the nine grid tiles into their sockets, then
bolt every seam with M3 × 8 mm bolts and nuts (24 in total). The result is
one 48,4 × 48,4 cm grid with 256 cells.

### 2.2 Cut and stick the strips

Cut 16 rows of 64 LEDs from the 144 LEDs/metre strip, always on the copper
cut marks. Take one row from each 0,5 m segment of a reel, so no row
contains the factory solder joint. Label each row (0–15) before you stick
it.

Stick each row on the back plate, along the centre of its row of cells,
passing under the walls through the notches. Every cell must sit over
exactly four LEDs.

| Row | LEDs | Direction |
|-----|------|-----------|
| 0 | 0–63 | left → right |
| 1 | 64–127 | right → left |
| 2 | 128–191 | left → right |
| ... | ... | alternating |
| 15 | 960–1023 | right → left |

### 2.3 Join the rows

Join the rows in a snake pattern with short 3-wire jumpers (VCC, GND, DATA)
in the hollow side margins of the grid. Follow the arrows printed on the
strip: data flows from DOUT to DIN.

```
row 0  DOUT ──► row 1  DIN     (right margin)
row 1  DOUT ──► row 2  DIN     (left margin)
...
row 14 DOUT ──► row 15 DIN
```

Use 22 AWG wire for the jumpers and 18 AWG for the power injection leads.
Run VCC and GND in parallel to the injection points — do not chain power
through the data line.

> ⚠️ Inject power at rows 0, 4, 8 and 12. With 1 024 LEDs, a single feed
> point causes a visible voltage drop at the far end of the matrix.

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
DC jack (+) ──┬──────────────────────── LED strip VCC (rows 0, 4, 8, 12)
              └──────────────────────── Raspberry Pi 5V
DC jack (−) ──┬──────────────────────── LED strip GND (rows 0, 4, 8, 12)
              └──────────────────────── Raspberry Pi GND (common ground)
```

> ⚠️ Never power the LED strip through the Raspberry Pi's 5V pin. Always connect the strip directly to the PSU.

### 3.3 Raspberry Pi, camera and button

Mount the Raspberry Pi Zero 2 W and the level shifter on the printed tray,
and bolt the tray to the back board behind the grid. Screw the camera onto
the bracket in the bottom margin of the grid, behind the pinhole of the
face, and connect it with a Pi Zero camera cable. Fit the push button in the bottom rail of the
frame and wire it between GPIO 3 and GND. See
[05 — Enclosure](05-enclosure.md) for the details.

---

## 4. Final assembly

Follow this order when putting the clock together:

1. **Place the front panel** face down in the frame, against the glazing,
   then the tracing paper, then the light grid with the strips on top
2. **Connect all wiring** — data, power, ground, camera, button — and
   double-check polarity
3. **Power on briefly** (with the back board open) and run the mock test to
   verify all LEDs respond:
   ```bash
   sudo .venv/bin/wordclock --debug
   ```
4. **Check for dead or flickering LEDs** and re-solder any bad joints
5. **Close the SANNAHED back board** so it clamps the stack
6. **Power on the full assembly** and verify the time displays correctly via the web interface at `http://wordclock.local:5000`

---

## 5. Wall mounting

Hang the clock from the SANNAHED hanging fitting, or with two ALFTA adhesive
hooks. Everything is inside the frame, so it hangs flat against the wall.

> Plug the power cable into the DC jack on the back board, then run it down the wall to a nearby socket. Use a cable raceway for a clean finish.

---

## 6. Assembly checklist

- [ ] Light grid tiles fitted together and bolted
- [ ] 16 strip rows cut, labelled and stuck in snake order
- [ ] All row jumpers done and tested
- [ ] Power injection at rows 0, 4, 8 and 12
- [ ] Level shifter wired and tested
- [ ] Common ground between PSU and Raspberry Pi
- [ ] Raspberry Pi tray bolted to the back board
- [ ] Camera aligned with the pinhole
- [ ] Button fitted in the bottom rail and wired to GPIO 3
- [ ] Front panel, paper and grid clamped in the frame
- [ ] Full power-on test passed (all LEDs respond)
- [ ] systemd service running on boot
- [ ] Clock accessible at `http://wordclock.local:5000`
- [ ] Mounted level on the wall
