# 05 — Enclosure (IKEA SANNAHED)

## Overview

The clock is built inside an IKEA SANNAHED 50 × 50 cm frame. The LEDs are a
WS2812B strip with 144 LEDs/metre, four LEDs under every letter. Every
printed part is made on a Bambu Lab A1 (25 × 25 cm bed), split into 3 × 3 tiles,
and generated from one parametric OpenSCAD model with `uv run wordclock-cad`.
A screen module under the clock holds the Raspberry Pi Touch Display, the
Raspberry Pi (3B or 4B) and the camera. This doc covers the dimensions, the printed parts, how to render and
print them, and how everything stacks inside the frame.

---

## 1. Dimensions

The panel fills the inner opening of the frame. Every cell sits over four
LEDs of the strip, so the cell pitch is 4 × 6,94 mm = 27,78 mm, with the
same margin on every side.

```
            SANNAHED frame, 50 × 50 cm
┌───────────────────────────────────────────┐
│  inside 49 × 49 cm, 45 mm deep            │
│ ┌───────────────────────────────────────┐ │
│ │        margin 2,23 cm                 │ │
│ │ ┌───────────────────────────────────┐ │ │
│ │ │ 16 × 16 cells, 2,78 cm pitch      │ │ │
│ │ │ matrix 44,4 × 44,4 cm             │ │ │
│ │ └───────────────────────────────────┘ │ │  2,23 cm
│ │        margin 2,23 cm                 │ │
│ └───────────────────────────────────────┘ │
│   panel 48,9 × 48,9 cm (1 mm clearance)   │
└───────────────────────────────────────────┘
```

| Measurement | Value |
|-------------|-------|
| Frame (outer) | 50 × 50 cm |
| Frame inside | 49 × 49 cm, 45 mm deep from the back board to the front lip; the 50 × 50 cm back board sits behind a 5 mm inner border |
| Front opening | ~46,8 cm (1,6 cm front border): about 1,2 cm of black margin shows around the letters |
| Face recess | 5 mm behind the front lip, held by a black ring |
| Panel size | 48,9 × 48,9 cm |
| Cell pitch | 2,78 cm (4 LEDs of a 144 LEDs/metre strip) |
| LED matrix | 44,4 × 44,4 cm |
| Margins | 2,23 cm on every side (about 1,1 cm hidden behind the front border) |
| Letter cap height | 15 mm (Karla Bold Stencil) |

---

## 2. Layer stack

```
   viewer
     │
     ▼
┌──────────────────────────┐  SANNAHED front lip (plastic sheet not used)
│▓▓                      ▓▓│  recess ring 4,8 mm, black, along the edges
├──────────────────────────┤  face        2,4 mm  black, stencil letter holes
├──────────────────────────┤  paper       tracing paper, diffuses the light
│ │    │    │    │    │    │  light grid  25 mm walls, white
│▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬│  LED strip on the back plate (2 mm)
├──┬────────────────────┬──┤
│▓▓│       wiring       │▓▓│  spacer ring 10,1 mm (▓), wiring in the middle
└──┴────────────────────┴──┘  SANNAHED back board
```

| Layer | Thickness | Colour / material |
|-------|-----------|-------------------|
| Recess ring | 4,8 mm | Opaque black PLA |
| Face | 2,4 mm | Opaque black PLA/PETG |
| Paper diffuser | ~0,1 mm | Tracing paper, 90 g/m² |
| Light grid + back plate | 27 mm | White PLA (reflects light) |
| Spacer ring (wiring inside) | 10,1 mm | White or black PLA |
| **Total** | **45 mm** (0,4 mm of play) | |

The face sits 5 mm behind the front lip, which gives the clock some
depth. The black recess ring fills those 10 mm along the edges, and the
spacer ring fills what is left behind the grid, so the back board presses
the whole stack against the front lip and nothing rattles. Both come from
`frame_depth` (45 mm), `recess` (5 mm) and `front_sheet_t` (0 mm: the
frame's plastic sheet is not used). Change them and render again.

---

## 3. Printed parts

| File | Qty | Depends on language | Purpose |
|------|-----|---------------------|---------|
| `<lang>/face_rXcY.stl` | 9 | yes | Black face with stencil letter holes |
| `common/grid_rXcY.stl` | 9 | no | Light grid that isolates each cell and holds the LED strips |
| `common/spacer.stl` | 4 | no | Quarter of the spacer ring behind the grid (print it four times) |
| `common/recess.stl` | 4 | no | Quarter of the black recess ring in front of the face (print it four times, in black) |
| `common/screenfront.stl` | 1 | no | Screen module: bezel and walls, camera above the screen |
| `common/screenback.stl` | 1 | no | Screen module: back cover with keyholes |
| `common/screenhanger.stl` | 1 | no | Screen module: hanger plate bolted to the frame |
| `optional/pitray.stl` | — | no | Only with `--optional`: Raspberry Pi Zero 2 W tray for a build without the screen module (section 9.3) |

Only the face depends on the language. To change the language of the
clock, open the back board, lift out the grid, swap the face panel and put
the grid back. Nothing is glued to the face.

Tiles are named by row and column: `r0c0` is top-left, `r2c2` is
bottom-right, as seen from the front. The panel is split after columns and
rows 5 and 11 (5 + 6 + 5 cells). All seams fall on a cell wall, never
through a letter.

```
┌────────┬──────────┬────────┐
│  r0c0  │   r0c1   │  r0c2  │   largest tile 17,1 × 17,1 cm
├────────┼──────────┼────────┤   (with tabs)
│  r1c0  │   r1c1   │  r1c2  │
├────────┼──────────┼────────┤
│  r2c0  │   r2c1   │  r2c2  │
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

After rendering, the tool checks that every STL file is a single solid
body and stops with an error if a part has loose pieces.

STL files are written to `build/stl/`, and Bambu Studio projects for the
Bambu Lab A1 to `build/bambu/`, with one part per plate:

| Project | Plates | Settings per part |
|---------|--------|-------------------|
| `face_<lang>.3mf` | 9 face tiles of one language | 100% infill |
| `grid.3mf` | 9 grid tiles + 4 spacer + 4 recess pieces + screen module | 3 walls, 15% infill |
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

### 6.3 Screen module

Print the front face down on the textured plate, in black, so the bezel
matches the clock face. The camera standoffs and the screw bosses grow up
from the bezel. Print the back cover with its outer face down and the
columns pointing up, and the hanger with its wall side down and the stud
sleeves pointing up. No supports are needed.

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

The frame clamps the face against its front lip and the bolted grid presses
it from behind, so the tiles cannot move once the frame is closed. If the
joints are too loose or too tight, change `joint_gap` (0,15 mm) and print
the test corner again.

---

### 7.3 Spacer ring

Four identical L-shaped pieces make a 25 mm wide ring along the edges,
behind the grid. Each piece runs from a corner to the middle of two edges,
and its dovetail tab locks into the next piece's socket. Grooves across
the ring, on the grid side, let cables pass from the margins to the middle.

1. Lay the four pieces on the back board, grooves up, and press the
   dovetails together.
2. Put the grid on top, then the paper, then the face, and close the frame.

The black recess ring in front of the face is made the same way: four
identical L pieces, 8 mm wide and 4,8 mm deep, between the front lip and
the face margins. Print them in black so they match the face.

### 7.3 Magnets between the face and the grid

The face and the grid hold together with neodymium disc magnets, 5 × 2 mm,
so the face stays aligned while you handle the clock and comes off in one
move to change the language. Each outer tile has one magnet pair per outer
edge, in the margin: a boss on the back of the face (so the magnet is
hidden from the front) and a post in the hollow margin of the grid, tied
to the perimeter wall and the cells by a rib. The
centre tile has no margin and is held by its dovetails.

| Item | Value |
|------|-------|
| Magnets | 5 × 2 mm neodymium discs, 12 per face set + 12 in the grid |
| Pockets | 5,2 mm, press fit; a drop of CA glue inside the pocket is fine |
| Positions | Middle cell of each outer tile edge, clear of the ribs |

Set the polarity once: put a magnet on every grid post, stick a second
magnet on top of each one, then press the face onto them so each face
pocket takes the magnet with the right pole. Mark the outer side of the
spare face sets the same way, so every language face attracts the grid.

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

## 9. Screen module

The Raspberry Pi (3B or 4B), the camera and the button live in a printed case under
the clock, around the official Raspberry Pi Touch Display (v1, 7", 800 ×
480). The touch screen controls the clock (settings, reminders, photo
booth preview, games), and the camera sits above it, where people look.

The module hangs from the frame, so the whole clock needs a single wall
hook. A hanger plate stays bolted through the frame back board, and the
module hooks on its two studs through the keyholes of its back cover. It
lifts off without tools, so the Raspberry Pi and the display are easy to
reach.

```
  wall
    │   ┌──────────────────────────┐
    │   │                          │  ← SANNAHED frame, on its own hook
    │   │        word clock        │
    │  ┌┤                          │
    │  │└──────────────────────────┘  ← hanger: 4 × M3 bolts through the back board
    │  │ hanger plate (stays on the frame)
    │  │ ○      ○   ← 2 studs
    │  │ ┌────────────┐
    │  └─┤     ◉      │  ← camera
    │    │ ┌────────┐ │
    │    │ │ screen │ ●  ← push button (right side)
    │    │ └────────┘ │
    │    └────────────┘  ← power and USB cables at the bottom
```

| Feature | Value |
|---------|-------|
| Outer size | 199,8 × 155,6 × 44 mm, plus the 5 mm hanger behind it |
| Display | Raspberry Pi Touch Display v1, glass 192,96 × 110,76 mm |
| Raspberry Pi | Raspberry Pi 3B or 4B on the display's M2,5 standoffs (58 × 49 mm); both have the same footprint and DSI connector |
| Camera | Camera board 25 × 24 mm (Camera Module 1.3/2/3 or OV5647), 4 M2 standoffs, 8 mm lens hole |
| Display retention | 4 columns on the back cover press the display against the bezel at its M3 holes |
| Back cover | 4 countersunk M3 screws into M3 heat-set inserts in the corner bosses |
| Hanger | 140 × 122 mm, 4 countersunk M3 bolts through the frame back board, nuts inside the frame clear of the spacer ring |
| Studs | 2 × M3 × 10 mm bolts with washers on printed sleeves, 120 mm apart |
| Keyholes | 11 mm wide end, 6 mm slot, 10 mm drop |
| Push button | 12 mm panel-mount momentary button on the right side |
| Cable exits | 60 × 14 mm at the bottom (power, USB), 18 × 10 mm at the top (LED cable) |

### 9.1 First assembly

1. Press four M3 heat-set inserts into the corner bosses of the front with
   a soldering iron.
2. Screw the camera onto the standoffs behind the bezel with M2 screws,
   lens through the hole.
3. Lay the display face down in the bezel. The stops above and below the
   glass keep it centred.
4. Mount the Raspberry Pi 3B or 4B on the display's standoffs and connect the
   display cable, the camera cable and the GPIO wires (LED data through the
   74AHCT125, button, buzzer).
5. Close the back cover with four M3 screws. Its columns hold the display.
6. Put the two stud bolts through the hanger sleeves, with a washer under
   each head and the nut in the hex pocket on the wall side.
7. Hold the hanger centred under the frame, 15 mm of gap between the frame
   and the module top, with its plate against the back board. Drill the
   four holes through the back board and bolt the hanger from the wall
   side, nuts inside the frame. The hanger stays there for good.
8. Drill an 8 mm hole up through the bottom rail of the frame, above the
   top cable exit of the module. Pass the LED cable into the frame and end
   it with a JST SM 3-pin connector just outside the module.

### 9.2 Taking the module off

1. Unplug the power cable and the JST connector of the LED cable.
2. Lift the module 10 mm and pull it towards you: the keyholes slide off
   the studs.
3. Lay it face down on a soft cloth and remove the four back cover screws.
   The Raspberry Pi is now on top, with every port and the SD card in
   reach. The display stays in the bezel.

To put it back, close the cover, hook the keyholes over the studs, let the
module drop, and plug the two cables in again.

The hanger sits between the back board and the wall, so the bottom of the
frame stands 5 mm off the wall. Stick two 5 mm felt pads to the top
corners of the back board so the frame hangs straight.

Software updates do not need any of this: the Raspberry Pi is reachable
over the network (`ssh wordclock.local`).

The LED cable comes from below, so wire the strip so that data enters at
the bottom row and set the start corner in the software configuration.
Keep the 74AHCT125 close to the Pi and the data wire under 1 m, with GND
running next to it.

> **Note:** The camera hole and standoffs follow the official camera boards.
> Other 5 MP (OV5647) boards can differ: check yours against the model
> (`cam_board`, `cam_holes`, `cam_lens_top`) before printing.

If the frame back board sits deeper than the frame's back edge, add a
spacer under the hanger so it stays flat. With `screen_hang = false` there
is no hanger: the keyholes hang on two screws in the wall, 120 mm apart.

The clock can still hide the camera in its own bottom margin instead: set
`clock_camera = true` and `bottom_extra = 16` in the model. The face then
gets a 6 mm pinhole and grid tile `r2c1` a camera bracket.

### 9.3 Alternative: Raspberry Pi Zero 2 W inside the frame

The clock keeps a 10 mm gap behind the grid, so a Raspberry Pi Zero 2 W can
live inside the frame instead of the screen module. The Pi Zero 2 W has no
DSI connector, so this build has no touch display.

| Step | Work |
|------|------|
| Remove the module and the hanger | 4 bolts; the holes in the back board stay hidden |
| Fit the Pi Zero 2 W and the 74AHCT125 | On the optional tray (`uv run wordclock-cad --optional`), bolted to the back board behind the grid |
| Power input | Panel-mount DC jack through the back board |
| Button | 12 mm button in a hole drilled through the bottom rail of the frame |
| Data input | Set the strip's start corner in the software configuration |
| Camera (optional) | `clock_camera = true` and `bottom_extra = 16`, then reprint the face and grid tiles |

---

## 10. Build checklist

- [ ] 4 × 4 test corner printed and checked for fit, letters and light bleed
- [ ] Nine face tiles printed for each language and fitted together
- [ ] Four spacer pieces printed and fitted into a ring on the back board
- [ ] Four recess pieces printed in black and fitted behind the front lip
- [ ] Nine grid tiles printed in white, fitted together and bolted (24 × M3)
- [ ] Magnets pressed into the grid posts and the face bosses, polarity checked
- [ ] Tracing paper cut to 45,5 × 45,5 cm
- [ ] 16 strip rows cut, stuck and connected in snake order
- [ ] Power injected at rows 0, 4, 8 and 12
- [ ] Screen module printed, display and Raspberry Pi fitted
- [ ] Camera screwed behind the bezel and aligned with its hole
- [ ] Button fitted in the side of the screen module
- [ ] Hanger bolted to the frame, module hooked on its studs
- [ ] LED cable through the bottom rail, with a JST connector at the module
- [ ] Colour order checked with a test pattern
- [ ] Stack fits in the frame with the back board closed
