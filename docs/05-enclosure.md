# 05 — Enclosure (IKEA SANNAHED)

## Overview

The clock is built inside an IKEA SANNAHED 50 × 50 cm frame. The LEDs are a
WS2812B strip with 144 LEDs/metre, four LEDs under every letter. Every
printed part is made on a Bambu Lab A1 (25 × 25 cm bed), split into 3 × 3 tiles,
and generated from one parametric OpenSCAD model with `uv run wordclock-cad`.
The Raspberry Pi Zero 2 W, the camera and the wiring all fit inside the
frame. This doc covers the dimensions, the printed parts, how to render and
print them, and how everything stacks inside the frame.

---

## 1. Dimensions

The panel fills the inner opening of the frame. Every cell sits over four
LEDs of the strip, so the cell pitch is 4 × 6,94 mm = 27,78 mm. The bottom
margin is wider than the top one and hides the camera.

```
            SANNAHED frame, 50 × 50 cm
┌───────────────────────────────────────────┐
│  inner opening 48,5 × 48,5 cm             │
│ ┌───────────────────────────────────────┐ │
│ │        top margin 1,18 cm             │ │
│ │ ┌───────────────────────────────────┐ │ │
│ │ │ 16 × 16 cells, 2,78 cm pitch      │ │ │
│ │ │ matrix 44,4 × 44,4 cm             │ │ │  side margins
│ │ └───────────────────────────────────┘ │ │  1,98 cm
│ │        bottom margin 2,78 cm   (◉)    │ │  ← hidden camera
│ └───────────────────────────────────────┘ │
│   panel 48,4 × 48,4 cm (1 mm clearance)   │
└───────────────────────────────────────────┘
```

| Measurement | Value |
|-------------|-------|
| Frame (outer) | 50 × 50 cm, 5 cm deep |
| Frame inner opening | 48,5 × 48,5 cm |
| Depth used | 4 cm |
| Panel size | 48,4 × 48,4 cm |
| Cell pitch | 2,78 cm (4 LEDs of a 144 LEDs/metre strip) |
| LED matrix | 44,4 × 44,4 cm |
| Margins | 1,18 cm top, 1,98 cm sides, 2,78 cm bottom |
| Letter cap height | 15 mm (Karla Bold Stencil) |

---

## 2. Layer stack

```
   viewer
     │
     ▼
┌──────────────────────────┐  SANNAHED front glazing
├──────────────────────────┤  face        2,4 mm  black, stencil letter holes
├──────────────────────────┤  paper       tracing paper, diffuses the light
│ │    │    │    │    │    │  light grid  25 mm walls, white
│▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬│  LED strip on the back plate (2 mm)
├──────────────────────────┤
│   [Pi tray]   wiring     │  back gap    10 mm
└──────────────────────────┘  SANNAHED back board
```

| Layer | Thickness | Colour / material |
|-------|-----------|-------------------|
| Face | 2,4 mm | Opaque black PLA/PETG |
| Paper diffuser | ~0,1 mm | Tracing paper, 90 g/m² |
| Light grid + back plate | 27 mm | White PLA (reflects light) |
| Back gap (Pi, wiring) | 10 mm | — |
| **Total** | **~40 mm** | |

---

## 3. Printed parts

| File | Qty | Depends on language | Purpose |
|------|-----|---------------------|---------|
| `<lang>/face_rXcY.stl` | 9 | yes | Black face with stencil letter holes and the camera pinhole |
| `common/grid_rXcY.stl` | 9 | no | Light grid that isolates each cell and holds the LED strips; `grid_r2c1` also holds the camera |
| `common/pitray.stl` | 1 | no | Tray for the Raspberry Pi Zero 2 W and the 74AHCT125 board |

Only the face depends on the language. To change the language of the
clock, open the back board, lift out the grid, swap the face panel and put
the grid back. The camera stays on the grid, so nothing is glued to the
face.

Tiles are named by row and column: `r0c0` is top-left, `r2c2` is
bottom-right, as seen from the front. The panel is split after columns and
rows 5 and 11 (5 + 6 + 5 cells). All seams fall on a cell wall, never
through a letter, and the camera sits in the middle of `r2c1`, away from
any seam.

```
┌────────┬──────────┬────────┐
│  r0c0  │   r0c1   │  r0c2  │   largest tile 17,1 × 17,1 cm
├────────┼──────────┼────────┤   (with tabs)
│  r1c0  │   r1c1   │  r1c2  │
├────────┼──────────┼────────┤
│  r2c0  │   r2c1 ◉ │  r2c2  │
└────────┴──────────┴────────┘
```

---

## 4. Letters

The face uses **Karla Bold Stencil** (SIL Open Font License 1.1, bundled in
`wordclock/cad/fonts/`). Every letter is a single through-hole: the counters
of letters such as O, A, D or B are held by small bridges, so the face prints
in one material without loose islands. The paper behind the face diffuses
the light and hides the LEDs.

| Parameter | Value |
|-----------|-------|
| Font | Karla Bold Stencil |
| Cap height | 15 mm |
| Accents | É, Í, Ó fit inside the cell |
| Face thickness | 2,4 mm |

---

## 5. Rendering the STL files

The model lives in `wordclock/cad/wordclock.scad`. It needs OpenSCAD 2025
or later (Manifold backend).

```bash
brew install --cask openscad@snapshot

uv run wordclock-cad                         # every language, grid and extra parts
uv run wordclock-cad --lang catalan          # one language
uv run wordclock-cad --test --lang catalan   # 4 × 4 test corner only
```

STL files are written to `build/stl/`, and Bambu Studio projects for the
Bambu Lab A1 to `build/bambu/`, with one part per plate:

| Project | Plates | Settings per part |
|---------|--------|-------------------|
| `face_<lang>.3mf` | 9 face tiles of one language | 100% infill |
| `grid.3mf` | 9 grid tiles + Pi tray | 3 walls, 15% infill |
| `test_<lang>.3mf` | Face and grid test corner (with `--test`) | default |

Open a project in Bambu Studio, pick the filament for each plate and print
plate by plate:

```bash
open -a BambuStudio build/bambu/face_catalan.3mf
```

The projects use the printer settings in
`wordclock/cad/bambu_a1_project_settings.config` (Bambu Lab A1, 0,4 mm
nozzle, 0,20 mm Standard, Bambu PLA Basic), exported by Bambu Studio.

To see the whole clock in 3D, write a preview file and open it in the
OpenSCAD GUI. Press `F6` to render, drag to rotate, and use the Customizer
(`explode`, `show_frame`, `cap_height`) to pull the layers apart or
assemble them.

```bash
uv run wordclock-cad --preview --lang catalan
open -a OpenSCAD build/preview/preview_catalan.scad   # assembled clock
open -a OpenSCAD build/preview/pieces_catalan.scad    # every tile, labelled
```

To change a dimension (frame size, grid height, letter size, camera
position), edit the parameters at the top of `wordclock/cad/wordclock.scad`
and render again.

---

## 6. Printing on the Bambu Lab A1

### 6.1 Face (one tile at a time)

The face tiles are modelled mirrored so they print **face down** on the
textured PEI plate, which gives the front a matte finish. Print them in
opaque black, one tile per plate.

| Setting | Value |
|---------|-------|
| Layer height | 0,2 mm |
| Infill | 100% |
| Supports | none |

### 6.2 Light grid

Print each grid tile with the back plate on the bed, in white PLA. The
notches for the strip and the wiring are short bridges and need no
supports.

| Setting | Value |
|---------|-------|
| Layer height | 0,2 mm |
| Wall loops | 3 (the 1,2 mm walls are solid) |
| Infill | 15% |
| Supports | none |

### 6.3 Pi tray

Print it flat, with the standoffs pointing up. No supports are needed.

The camera bracket is part of `grid_r2c1`: its plate prints as a short
bridge between two side walls, with the standoffs growing up from it.

---

## 7. Joining the tiles

The face and the grid tiles both lock together with dovetail tabs. Tiles
have tabs on their right and bottom edges and sockets on their left and top
edges. The joints sit where four cells meet, so they never touch a letter
or a strip.

```
┌────────┬──────────┬────────┐
│  r0c0  ▶   r0c1   ▶  r0c2  │   ▶ / ▼  dovetail tab into the
├───▼────┼────▼─────┼───▼────┤          neighbour's socket
│  r1c0  ▶   r1c1   ▶  r1c2  │
├───▼────┼────▼─────┼───▼────┤
│  r2c0  ▶   r2c1   ▶  r2c2  │
└────────┴──────────┴────────┘
```

### 7.1 Light grid: dovetails and M3 bolts

Every seam of the grid is a double wall with M3 holes 4 mm above the back
plate, two per tile edge, in the corners of the cells. They sit low and to
the side, so they cast no shadow on the letters and do not touch the strip.

1. Lay the nine grid tiles open side up and press the tabs into the
   sockets, row by row.
2. Push an M3 × 8 mm bolt through each seam hole and tighten a nut on the
   other side (24 bolts in total).

### 7.2 Face: dovetails only, no glue

Bolts on the face would show from the front, and the grid walls rest right
behind it, so the face tiles are held by the dovetails alone. No glue is
used, so the face stays interchangeable.

1. Lay the nine face tiles face down on a flat table and press the tabs
   into the sockets, row by row.
2. Lift the panel with both hands flat underneath. The dovetails stop the
   tiles from sliding apart, but they can pop out if the panel bends.

The frame clamps the face against the glazing and the bolted grid presses
it from behind, so the tiles cannot move once the frame is closed. If the
joints are too loose or too tight, change `joint_gap` (0,15 mm) and print
the test corner again.

---

## 8. LED strips

### 8.1 What to buy

| Item | Specification | Quantity |
|------|---------------|----------|
| LED strip | WS2812B, 144 LEDs/metre, 5V, 10 mm wide, IP30 (no silicone) | 8 reels of 1 m |
| Wire | 3-core, 22 AWG, for the row ends | ~2 m |
| Power wire | 2-core, 18 AWG, for the power injection | ~2 m |

Each row has 16 cells × 4 LEDs = 64 LEDs (44,4 cm). A 1 m reel is made of
two 0,5 m segments of 72 LEDs: cut one row from each segment so no row
contains the factory solder joint. 8 reels give exactly 16 rows.

### 8.2 Fitting the strips

1. Cut 16 rows of 64 LEDs, always on the copper cut marks.
2. Stick each row on the back plate of the grid, along the centre of the
   row of cells, passing under the walls through the notches. The first LED
   of each row sits right after the left (or right) outer cell wall.
3. Connect the rows in a snake: row 0 left → right, row 1 right → left, and
   so on. The row ends sit in the hollow side margins of the grid, where
   there is room for the 3-wire jumpers.
4. Inject 5V and GND at rows 0, 4, 8 and 12. With 1 024 LEDs, a single feed
   point is not enough.

```
row 0  ●●●●|●●●●|●●●● ... ●●●●  →  LEDs    0 ..   63
row 1  ●●●●|●●●●|●●●● ... ●●●●  ←  LEDs   64 ..  127
row 2  ●●●●|●●●●|●●●● ... ●●●●  →  LEDs  128 ..  191
...
row 15                          ←  LEDs  960 .. 1023
        └── one cell = 4 LEDs
```

---

## 9. Raspberry Pi, camera and button

Everything lives inside the frame. Only the power cable leaves the clock.

```
 front view (face removed)                  side section

┌──────────────────────────────┐            glazing
│                              │            │face
│      light grid + strips     │            ││paper
│                              │            │││ grid  │ gap │
│                              │            │││       │ Pi  │ back
├──────────────────────────────┤            │││       │tray │ board
│     bottom margin   (◉)      │ ← camera   │◉│       │     │
└──────────────●───────────────┘ ← button in the bottom rail
```

| Component | Placement |
|-----------|-----------|
| Raspberry Pi Zero 2 W | On the printed tray, bolted to the back board behind the grid |
| 74AHCT125 board | On the free area of the same tray |
| Camera Module 3 | On the bracket of grid tile `r2c1`, right behind the 6 mm pinhole in the bottom margin of the face |
| Push button | 7–12 mm panel-mount momentary button, in a hole drilled through the bottom rail of the frame, under the hollow bottom margin of the grid |
| Power input | Panel-mount DC jack rated for 10 A, through the back board |

1. Screw the camera onto the bracket of `grid_r2c1` with M2 screws, lens
   facing the face and the cable edge towards the bottom of the frame.
2. Route the camera cable (Pi Zero version, 15 cm) through the slot in the
   bracket and the open back of the bottom margin to the Pi.
3. Bolt the Pi tray to the back board with M3 countersunk bolts, Pi facing
   the grid. Solder the wires to the Pi directly, without a pin header, to
   keep it under 10 mm.
4. Drill the button hole in the bottom rail and wire the button between
   GPIO 3 and GND (GPIO 3 also wakes the Pi from halt).

The Pi Zero 2 W is not soldered to a header and the gap behind the grid is
10 mm, so check the height of the tray with the Pi on it before closing the
frame.

---

## 10. Build checklist

- [ ] 4 × 4 test corner printed and checked for fit, letters and light bleed
- [ ] Nine face tiles printed for each language and fitted together
- [ ] Nine grid tiles printed in white, fitted together and bolted (24 × M3)
- [ ] Tracing paper cut to 45,5 × 45,5 cm (covers the matrix, not the camera)
- [ ] 16 strip rows cut, stuck and connected in snake order
- [ ] Power injected at rows 0, 4, 8 and 12
- [ ] Camera screwed to the grid bracket and aligned with the pinhole
- [ ] Pi tray bolted, Pi and 74AHCT125 wired
- [ ] Button fitted in the bottom rail
- [ ] Colour order checked with a test pattern
- [ ] Stack fits in the frame with the back board closed
