# 05 — Enclosure (IKEA SANNAHED)

## Overview

The clock is built inside an IKEA SANNAHED 50 × 50 cm frame. Every part is
3D-printed on a Bambu Lab A1 (256 × 256 mm bed), split into tiles, and
generated from one parametric OpenSCAD model with `uv run wordclock-cad`.
This doc covers the dimensions, the printed parts, how to render and print
them, and how they stack inside the frame.

---

## 1. Dimensions

The panel and the light grid fill the inner opening of the frame. With
48,5 cm available, the 16 cells use a 3,0 cm pitch.

```
            SANNAHED frame, 50 × 50 cm
┌───────────────────────────────────────────┐
│  inner opening 48,5 × 48,5 cm             │
│ ┌───────────────────────────────────────┐ │
│ │ panel 48,4 × 48,4 cm (1 mm clearance) │ │
│ │ ┌───────────────────────────────────┐ │ │
│ │ │ 16 × 16 cells, 3,0 cm pitch       │ │ │
│ │ │ matrix 48,0 × 48,0 cm             │ │ │
│ │ └───────────────────────────────────┘ │ │
│ │  2 mm border on each side             │ │
│ └───────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

| Measurement | Value |
|-------------|-------|
| Frame (outer) | 50 × 50 cm |
| Frame inner opening | 48,5 × 48,5 cm |
| Panel size | 48,4 × 48,4 cm |
| Cell pitch | 3,0 cm |
| LED matrix | 48,0 × 48,0 cm |
| Letter cap height | 16 mm (Karla Bold Stencil) |
| Tile size (2 × 2 split) | 24,2 × 24,2 cm |

> **Note:** A 30 LEDs/metre strip has a fixed 3,33 cm pitch, so 16 LEDs
> need 53,3 cm and do not fit. The grid holds individual 12 mm WS2811/WS2812B
> bullet pixels instead, which can sit at any pitch.

---

## 2. Layer stack

```
   viewer
     │
     ▼
┌──────────────────────────┐  SANNAHED front glazing
├──────────────────────────┤  face      2,4 mm  black, stencil letter holes
├──────────────────────────┤  paper     tracing paper, diffuses the light
│ │    │    │    │    │    │  light grid 20 mm walls, white
├──┬─┴──┬─┴──┬─┴──┬─┴──┬─┴─┤  back plate 2 mm, 12 mm pixel holes
   ▼    ▼    ▼    ▼    ▼      bullet pixels and wiring
┌──────────────────────────┐  SANNAHED back board
└──────────────────────────┘
```

The Raspberry Pi box hangs under the bottom edge of the frame (see
section 9), so the frame stays flat against the wall.

| Layer | Thickness | Colour |
|-------|-----------|--------|
| Face | 2,4 mm | Opaque black PLA/PETG |
| Paper diffuser | ~0,1 mm | Tracing paper, 48,4 × 48,4 cm |
| Light grid + back plate | 22 mm | White PLA (reflects light) |
| Pixels behind the back plate | ~15 mm | — |

Measure the depth of the frame rebate before printing. The stack needs
about 40 mm between the glazing and the back board.

---

## 3. Printed parts

| File | Qty | Depends on language | Purpose |
|------|-----|---------------------|---------|
| `<lang>/face_rXcY.stl` | 4 | yes | Black face with stencil letter holes |
| `common/grid_rXcY.stl` | 4 | no | Light grid that isolates each cell and holds the pixels |
| `common/pibox.stl` | 1 | no | Box that hangs under the frame, with push button and DC jack |
| `common/pilid.stl` | 1 | no | Bottom lid that carries the Raspberry Pi Zero 2 W |

Only the face depends on the language. To change the language of the
clock, swap the four face tiles and keep everything else.

Tiles are named by row and column: `r0c0` is top-left, `r1c1` is
bottom-right, as seen from the front. All seams fall on a cell wall, never
through a letter.

```
┌──────────┬──────────┐
│   r0c0   │   r0c1   │
├──────────┼──────────┤
│   r1c0   │   r1c1   │
└──────────┴──────────┘
```

---

## 4. Letters

The face uses **Karla Bold Stencil** (SIL Open Font License 1.1, bundled in
`wordclock/cad/fonts/`). Every letter is a single through-hole: the counters
of letters such as O, A, D or B are held by small bridges, so the face prints
in one material without loose islands. The paper behind the face diffuses
the light and hides the pixel.

| Parameter | Value |
|-----------|-------|
| Font | Karla Bold Stencil |
| Cap height | 16 mm |
| Accents | É, Í, Ó fit inside the cell |
| Face thickness | 2,4 mm |

---

## 5. Rendering the STL files

The model lives in `wordclock/cad/wordclock.scad`. It needs OpenSCAD 2025
or later (Manifold backend).

```bash
brew install --cask openscad@snapshot

uv run wordclock-cad                     # every language, grid and Pi box
uv run wordclock-cad --lang catalan      # one language
uv run wordclock-cad --test --lang catalan   # 4 × 4 test corner only
```

Files are written to `build/stl/`.

To see the whole clock in 3D, write a preview file and open it in the
OpenSCAD GUI. Press `F5` to preview, drag to rotate, and use the Customizer
(`explode`, `show_frame`, `cap_height`) to pull the layers apart or assemble them.

```bash
uv run wordclock-cad --preview --lang catalan
open -a OpenSCAD build/preview/preview_catalan.scad
```

To change a dimension (pitch, frame size,
grid height, letter size), edit the parameters at the top of
`wordclock/cad/wordclock.scad` and render again.

---

## 6. Printing on the Bambu Lab A1

### 6.1 Face (one tile at a time)

The face tiles are modelled mirrored so they print **face down** on the
textured PEI plate, which gives the front a matte finish. Print them in
opaque black, one tile per plate (24,6 × 24,6 cm with the joint tabs).

| Setting | Value |
|---------|-------|
| Layer height | 0,2 mm |
| First layer | 0,2 mm |
| Infill | 100% |
| Supports | none |

### 6.2 Light grid

Print each grid tile with the back plate on the bed, in white PLA.

| Setting | Value |
|---------|-------|
| Layer height | 0,2 mm |
| Wall loops | 3 (the 1,2 mm walls are solid) |
| Infill | 15% |
| Supports | none |

### 6.3 Raspberry Pi box

Print the box on its back: the hanger plate and the back wall lie on the
bed, and the front wall bridges over the inside. Print the lid flat, outside
face down. No supports are needed.

---

## 7. Joining the tiles

### 7.1 Face

The face tiles lock together with dovetail tabs. Tiles have tabs on their
right and bottom edges and sockets on their left and top edges. The joints
sit where four cells meet, so they never touch a letter.

```
┌──────────┬──────────┐
│   r0c0   ▶   r0c1   │   ▶ / ▼  dovetail tab into the
├────▼─────┼────▼─────┤          neighbour's socket
│   r1c0   ▶   r1c1   │
└──────────┴──────────┘
```

1. Lay the four tiles face down on a flat table.
2. Press the tabs into the sockets, starting with `r0c0` and `r0c1`.
3. Optional: add a drop of CA glue on each joint for a rigid panel. Leave it
   unglued if you want to take the face apart again.

The frame clamps the face between the glazing and the grid, so the tiles
cannot move once the frame is closed.

### 7.2 Light grid

The grid tiles have a full wall on every shared edge, so each seam is a
double wall with two M3 holes 4 mm above the back plate.

1. Lay two grid tiles side by side, open side up.
2. Push an M3 × 8 mm bolt through each seam hole and tighten a nut on the
   other side.
3. Repeat until the four tiles form one 48,4 × 48,4 cm grid.

### 7.3 Paper diffuser

Cut one sheet of tracing paper (90 g/m²) to 48,4 × 48,4 cm and lay it on
the grid, under the face. A3 sheets are too small: use a roll or a 50 × 65 cm
sheet.

---

## 8. Fitting the pixels

1. Push one 12 mm bullet pixel into each back plate hole from behind,
   following the snake order: row 0 left → right, row 1 right → left, and
   so on.
2. Fold the spare wire between pixels flat behind the back plate.
3. Inject 5V at row 0 and row 8 (see [02 — Hardware](02-hardware.md)).

> **Note:** Many 12 mm bullet pixels use the WS2811 chip with RGB colour
> order instead of GRB. Check the colours with a test pattern before
> closing the frame.

---

## 9. Raspberry Pi

The Raspberry Pi Zero 2 W and the 74AHCT125 board go in a printed box that
hangs under the bottom edge of the frame. A plate on the back of the box
rises behind the frame and is bolted to the back board, so the box needs no
space inside the frame and the clock stays flat against the wall.

```
        ┌──────────────────────────────┐
        │                              │
        │         word clock           │  ← SANNAHED frame
        │                              │
        │   ┌──────────────────────┐   │  ← hanger plate (behind the frame,
        └───┼──────────────────────┼───┘     bolted to the back board)
            │  ○ DC        ( ● )   │      ← box: DC jack on the left side,
            └──────────────────────┘        push button on the front
                 lid underneath           ← Raspberry Pi mounted on the lid
```

| Feature | Value |
|---------|-------|
| Outer size | 94 × 50 × 28 mm (width × depth × height) |
| Hanger plate | 94 × 3 mm, 45 mm above the box, 2 countersunk M3 holes |
| Push button | 12 mm panel-mount momentary button, on the front |
| Power input | 5,5 × 2,1 mm panel-mount DC jack (8 mm hole), on the left side |
| Pi mounting | On the lid, 4 standoffs, M2.5 self-tapping screws |
| Lid | 2 countersunk M3 self-tapping screws from underneath |
| Cable exit | 20 × 8 mm slot in the top, at the back |

1. Hold the box under the frame, centred, with the hanger plate against the
   back of the frame. Mark the two holes on the back board.
2. Drill the back board and bolt the plate on with M3 bolts, the countersunk
   heads on the wall side and the nuts inside the frame.
3. Drill an 8 mm hole through the bottom rail of the frame, right above the
   cable slot, and pass the 3-wire LED cable up into the frame to row 0.
4. Mount the Raspberry Pi on the lid, wire the button between a GPIO pin and
   GND, and close the lid from underneath.

The SD card and the wiring stay reachable by removing the lid, without
taking the clock off the wall. The hanger plate adds 3 mm behind the bottom
of the frame: stick two 3 mm felt pads to the top corners so the frame
hangs straight.

---

## 10. Build checklist

- [ ] Frame rebate depth measured (about 40 mm needed)
- [ ] 4 × 4 test corner printed and checked for fit, letters and light bleed
- [ ] Four face tiles printed for each language and fitted together
- [ ] Four grid tiles printed in white and bolted together
- [ ] Tracing paper cut to 48,4 × 48,4 cm
- [ ] 256 bullet pixels fitted in snake order
- [ ] Power injected at row 0 and row 8
- [ ] Colour order checked with a test pattern
- [ ] Pi box printed, wired and bolted under the frame
- [ ] Stack fits in the frame with the back board closed
