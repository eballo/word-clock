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
| Letter cap height | 18 mm |
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
├──────────────────────────┤  face      1,6 mm  black, letter holes
├──────────────────────────┤  diffuser  0,6 mm  white
│ │    │    │    │    │    │  light grid 20 mm walls, white
├──┬─┴──┬─┴──┬─┴──┬─┴──┬─┴─┤  back plate 2 mm, 12 mm pixel holes
   ▼    ▼    ▼    ▼    ▼      bullet pixels and wiring
┌──────────────────────────┐  SANNAHED back board
└──────────────────────────┘
            │
     Raspberry Pi box (outside, on the back board)
```

| Layer | Thickness | Colour |
|-------|-----------|--------|
| Face | 1,6 mm | Opaque black PLA/PETG |
| Letter fill (optional) | 1,6 mm | White PLA |
| Diffuser | 0,6 mm | White PLA |
| Light grid + back plate | 22 mm | White PLA (reflects light) |
| Pixels behind the back plate | ~15 mm | — |

Measure the depth of the frame rebate before printing. The stack needs
about 40 mm between the glazing and the back board.

---

## 3. Printed parts

| File | Qty | Depends on language | Purpose |
|------|-----|---------------------|---------|
| `<lang>/face_rXcY.stl` | 4 | yes | Black face with letter holes |
| `<lang>/letters_rXcY.stl` | 4 | yes | White letter fill, flush with the face (needs AMS lite) |
| `<lang>/diffuser_rXcY.stl` | 4 | yes | White backing that diffuses light and holds the letter islands (O, A, D, …) |
| `common/grid_rXcY.stl` | 4 | no | Light grid that isolates each cell and holds the pixels |
| `common/pibox.stl` | 1 | no | Box for the Raspberry Pi Zero 2 W and the 74AHCT125 |
| `common/pilid.stl` | 1 | no | Ventilated lid for the box |

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

## 4. Rendering the STL files

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
(`explode`, `show_frame`) to pull the layers apart or assemble them.

```bash
uv run wordclock-cad --preview --lang catalan
open -a OpenSCAD build/preview/preview_catalan.scad
```

To change a dimension (pitch, frame size,
grid height, letter size), edit the parameters at the top of
`wordclock/cad/wordclock.scad` and render again.

---

## 5. Printing on the Bambu Lab A1

### 5.1 Face (one tile at a time)

The face tiles are modelled mirrored so they print **face down** on the
textured PEI plate, which gives the front a matte finish.

**With AMS lite:** import `face`, `letters` and `diffuser` of the same tile
together and answer **Yes** when Bambu Studio asks to load them as one
object with multiple parts. Assign black to `face` and white to `letters`
and `diffuser`.

**Without AMS:** import `face` and `diffuser` only. In the layer slider, add
a filament change at the first layer of the diffuser (1,6 mm). The letters
stay open in the black layers and the white layer bridges over them.

| Setting | Value |
|---------|-------|
| Layer height | 0,2 mm |
| First layer | 0,2 mm |
| Infill | 100% |
| Supports | none |

### 5.2 Light grid

Print each grid tile with the back plate on the bed, in white PLA.

| Setting | Value |
|---------|-------|
| Layer height | 0,2 mm |
| Wall loops | 3 (the 1,2 mm walls are solid) |
| Infill | 15% |
| Supports | none |

### 5.3 Raspberry Pi box

Print the box upright and the lid upside down (vents on the bed). No
supports are needed.

---

## 6. Joining the tiles

The grid tiles have a full wall on every shared edge, so each seam is a
double wall with two M3 holes 4 mm above the back plate.

1. Lay two grid tiles side by side, open side up.
2. Push an M3 × 8 mm bolt through each seam hole and tighten a nut on the
   other side.
3. Repeat until the four tiles form one 48,4 × 48,4 cm grid.

The face tiles are not bolted. The frame clamps them between the glazing
and the grid.

---

## 7. Fitting the pixels

1. Push one 12 mm bullet pixel into each back plate hole from behind,
   following the snake order: row 0 left → right, row 1 right → left, and
   so on.
2. Fold the spare wire between pixels flat behind the back plate.
3. Inject 5V at row 0 and row 8 (see [02 — Hardware](02-hardware.md)).

> **Note:** Many 12 mm bullet pixels use the WS2811 chip with RGB colour
> order instead of GRB. Check the colours with a test pattern before
> closing the frame.

---

## 8. Raspberry Pi

The Raspberry Pi Zero 2 W and the 74AHCT125 board go in the printed box,
screwed onto the outside of the SANNAHED back board.

| Feature | Value |
|---------|-------|
| Inner size | 72 × 60 × 20 mm |
| Pi mounting | 4 standoffs, M2.5 self-tapping screws |
| Box mounting | 2 countersunk M3 screws through the back board |
| Cable exits | Side slot (5V input), floor slot (LED cable) |

Drill a 20 × 10 mm hole in the back board under the floor slot to route the
3-wire LED cable to row 0. The box adds about 24 mm behind the frame, so
stick two 24 mm felt pads to the bottom corners of the back board to keep
the frame hanging straight.

The box is optional: the Pi can also stay outside the frame, with only the
3-wire cable entering through the back board.

---

## 9. Build checklist

- [ ] Frame rebate depth measured (about 40 mm needed)
- [ ] 4 × 4 test corner printed and checked for fit, letters and light bleed
- [ ] Four face tiles printed for each language
- [ ] Four grid tiles printed in white and bolted together
- [ ] 256 bullet pixels fitted in snake order
- [ ] Power injected at row 0 and row 8
- [ ] Colour order checked with a test pattern
- [ ] Pi box printed, wired and screwed to the back board
- [ ] Stack fits in the frame with the back board closed
