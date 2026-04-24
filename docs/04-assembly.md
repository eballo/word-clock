# 04 — Assembly

## Overview

The clock is assembled in four main layers, stacked from back to front:

```
        WALL
         │
    ┌────┴────┐
    │  Back   │  ← 3D-printed back cover (houses Raspberry Pi + PSU)
    ├─────────┤
    │  LED    │  ← WS2812B strip mounted on backing board
    │  matrix │
    ├─────────┤
    │  Front  │  ← 3D-printed front panel (letters)
    └─────────┘
         │
       viewer
```

---

## 1. 3D printing

The enclosure is split into three 3D-printed parts. Given the total size of 65×65 cm, each part must be printed in sections and joined together.

### 1.1 Front panel (letter grid)

The front panel contains the 16×16 grid of letter-shaped through-holes.

| Parameter | Value |
|-----------|-------|
| Total size | 53,3 × 53,3 cm |
| Cell size | 3,33 × 3,33 cm |
| Letter size | ~23 mm |
| Wall between cells | ~5 mm |
| Depth | 20 mm minimum |
| Filament | PLA or PETG, opaque black |
| Infill | 100% (walls must block all light) |

**Printing in sections:**

Divide the panel into a 2×2 grid of four equal sections (~27×27 cm each), which fits most printer beds. Design the joints to fall exactly on the wall between two columns and two rows — never through a letter opening.

```
┌──────────┬──────────┐
│ section  │ section  │
│  A (8×8) │  B (8×8) │
├──────────┼──────────┤
│ section  │ section  │
│  C (8×8) │  D (8×8) │
└──────────┴──────────┘
```

Join sections with M3 bolts and nuts recessed into the panel walls, or with a snap-fit tongue-and-groove joint along the seam.

### 1.2 Frame

The frame surrounds the front panel and provides the 5,85 cm margin on each side.

| Parameter | Value |
|-----------|-------|
| Outer size | 65 × 65 cm |
| Inner opening | 53,3 × 53,3 cm |
| Depth | 40 mm (to house all layers) |
| Filament | PLA or PETG, colour of your choice |
| Infill | 40% |

Print the frame in sections (four L-shaped corners + straight sides) and join with M4 bolts or wood glue inserts.

### 1.3 Back cover

The back cover closes the enclosure and houses the Raspberry Pi and the power supply.

| Parameter | Value |
|-----------|-------|
| Size | 65 × 65 cm |
| Filament | PLA or PETG, black |
| Infill | 20% |
| Features | Ventilation slots, cable entry hole, wall-mount bracket |

Include two keyhole slots on the back cover for hanging on the wall (see section 5).

---

## 2. LED matrix assembly

### 2.1 Prepare the backing board

Cut a rigid backing board (foam board, thin plywood, or black cardboard) to **53,3 × 53,3 cm**. This is the surface the LED strip will be mounted on.

Mark a 16×16 grid with a pencil:

```bash
# Each cell is 3,33 cm — mark lines at:
# Columns: 3.33, 6.66, 9.99, 13.32 ... 53.28 cm
# Rows:    3.33, 6.66, 9.99, 13.32 ... 53.28 cm
```

### 2.2 Cut the LED strip into rows

Cut the strip into **16 rows of 16 LEDs** each. Always cut at the designated cut marks between LEDs — never through an LED or its copper pads.

> ⚠️ Label each row (0–15) with a marker before cutting so you do not lose track of the order.

| Row | LEDs | Direction |
|-----|------|-----------|
| 0 | 0–15 | left → right |
| 1 | 16–31 | right → left |
| 2 | 32–47 | left → right |
| ... | ... | alternating |
| 15 | 240–255 | right → left |

### 2.3 Mount the strip rows

Peel the adhesive backing and stick each row onto the backing board, aligning the centre of each LED with the grid marks. Press firmly along the full length of each row.

For extra hold, add a small drop of hot glue at each end of every row.

### 2.4 Solder the row connections

Connect the rows in a snake pattern using short 3-wire jumpers (VCC, GND, DATA):

```
row 0  DOUT ──► row 1  DIN
row 1  DOUT ──► row 2  DIN
...
row 14 DOUT ──► row 15 DIN
```

Use 22 AWG wire, keep jumpers as short as possible (~3–4 cm). Solder VCC and GND in parallel across all rows — do not chain power through the data line.

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

Mount the Raspberry Pi inside the back cover using M2.5 standoffs. Route the GPIO ribbon or individual wires through a cable channel to the level shifter, which should be mounted close to the LED matrix input (top-left corner, row 0).

---

## 4. Final assembly

Follow this order when putting the clock together:

1. **Mount the LED matrix** (backing board with strip) inside the frame
2. **Connect all wiring** — data, power, ground — and double-check polarity
3. **Power on briefly** (without the front panel) and run the mock test to verify all LEDs respond:
   ```bash
   sudo .venv/bin/wordclock --debug
   ```
4. **Check for dead or flickering LEDs** and re-solder any bad joints
5. **Attach the front panel** (letter grid) on top of the LED matrix, securing it to the frame with M3 bolts
6. **Close the back cover** and secure it with M3 bolts
7. **Power on the full assembly** and verify the time displays correctly via the web interface at `http://wordclock.local:5000`

---

## 5. Wall mounting

The back cover includes two **keyhole slots** for wall mounting:

```
┌─────────────────────────────────┐
│  ●                           ●  │  ← keyhole slots (60 cm apart)
│                                 │
│         back cover              │
│                                 │
│  [Pi]              [PSU]        │
└─────────────────────────────────┘
```

### Steps

1. Mark two points on the wall **60 cm apart**, horizontally level
2. Insert two **M4 wall screws** leaving ~5 mm of screw head protruding from the wall
3. Hang the clock by sliding the keyhole slots over the screw heads
4. Check with a spirit level and adjust if needed

> Route the power cable through the bottom of the frame, down the wall, and to a nearby socket. Use a cable raceway for a clean finish.

---

## 6. Assembly checklist

- [ ] All 16 LED rows cut and labelled
- [ ] Strip mounted and aligned on backing board
- [ ] All row-to-row solder joints done and tested
- [ ] Power injection at row 0 and row 8
- [ ] Level shifter wired and tested
- [ ] Common ground between PSU and Raspberry Pi
- [ ] Raspberry Pi mounted inside back cover
- [ ] Front panel sections joined and attached to frame
- [ ] Full power-on test passed (all LEDs respond)
- [ ] systemd service running on boot
- [ ] Clock accessible at `http://wordclock.local:5000`
- [ ] Mounted level on the wall