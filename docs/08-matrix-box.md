# 08 — Matrix Box

## Overview

The mini matrix of [07 — Mini Matrix](07-mini-matrix.md) in one flat box:
the 10 × 6 LED grid on top, the 7" Raspberry Pi Touch Display v1 under it,
the Raspberry Pi 3B beside the display, the camera and a USB microphone
hidden behind two rivets of a decorative row, and room for an Arduino Uno.
There is no button: the touch screen does its job. The box hangs flat on a
wall from two keyholes, and two triangle legs hook into the back to stand
it on a table. A letters cover sits on the grid with magnets, to try the
word clock face before building the big clock. This doc covers the parts,
printing on the Bambu Lab A1, the wiring and the assembly.

---

## 1. Sizes

```
 ┌──────────────────────── 37,7 cm ─────────────────────────┐
 │                  ○ keyhole        ○ keyhole              │
 │      ┌──────────── LED grid 10 × 6, 3,33 cm ──────────┐  │
 │      │                                                │  │
 │      │              letters cover on top              │  │  38,3 cm
 │      └────────────────────────────────────────────────┘  │
 │  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ print split ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄  │
 │   ○  ○  ○  ○  ○  ◉mic  ┆  ◉cam  ○  ○  ○  ○  ○  ○          │  rivet row
 │  ┌─────┐     ┌──────── display 19,3 × 11,1 ───┐  ┌─────┐  │
 │  │ Pi  │     │                                │  │ Uno │  │
 │  └─────┘     └────────────────────────────────┘  └─────┘  │
 └───────────────────────────┆──────────────────────────────┘
                     print split
```

| Measurement | Value |
|-------------|-------|
| Box | 37,7 × 38,3 × 3,63 cm |
| Grid | 10 × 6 cells, 3,33 cm pitch, 30 mm walls |
| Display window | 19,3 × 11,1 cm, the glass flush with the face |
| Room above the Pi ports | 8,7 mm |
| Room under the display driver board | 15,3 mm, for the DSI ribbon |
| Printed tiles | Shell and face 18,9 × 15,5 cm (bottom) and 18,9 × 22,8 cm (top); grid and cover halves 16,7 × 21,5 and 17,6 × 21,8 cm |

---

## 2. Parts to buy

| # | Part | Use |
|---|------|-----|
| 1 | 5 V 4 A power supply, 5,5 × 2,1 mm plug | LEDs (limited to 1,5 A in software), Pi and display |
| 2 | Panel-mount DC jack 5,5 × 2,1 mm (DC-022) | In the bottom wall |
| 3 | 2 × WAGO 221-413 lever connectors | Share the 5 V and the ground |
| 4 | CSI ribbon cable, 30 cm | The camera is about 25 cm from the Pi |
| 5 | USB microphone, small (dongle size) | Behind the microphone rivet |
| 6 | 330 Ω resistor | In series with the LED data line |
| 7 | 7 × M5 bolts and nuts: 3 × M5 × 25 mm (vertical seam), 4 × M5 × 16 mm (horizontal seam) | Join the shell tiles |
| 8 | 2 × M5 wall screws with plugs, heads up to 10 mm | Hang the box |
| 9 | 4 × M3 × 6 mm countersunk | Display, from the back into its frame |
| 10 | 4 × M2.5 × 6 mm self-tapping | Raspberry Pi |
| 11 | 4 × M2 × 6 mm self-tapping | Camera |
| 12 | 4 × M3 × 8 mm self-tapping (optional) | Arduino Uno |
| 13 | 40 neodymium magnets, 5 × 2 mm | 12 + 12 for the face, 8 + 8 for the letters cover |
| 14 | Tracing paper | Diffuser, cut to the grid |

M5 is used wherever the printed parts are bolted. The display (M3), the
Raspberry Pi (M2.5), the camera (M2) and the Arduino (M3) keep the screws
their holes were made for.

---

## 3. Print

```bash
uv run wordclock-cad --box    # STL files in build/stl/box/, projects in build/bambu/
```

The command checks that every piece is one solid body and fits the 256 mm
bed with 3 mm to spare, and writes five Bambu Studio projects, one piece
per plate:

| Project | Pieces | Filament | Settings | Orientation |
|---------|--------|----------|----------|-------------|
| `box_shell.3mf` | 4 shell tiles | White or grey PLA | 3 walls, 15 % infill | Back on the bed |
| `box_grid.3mf` | 2 grid halves | White PLA | 3 walls, 15 % infill | Upside down: wall tops on the bed |
| `box_face.3mf` | 4 face tiles | Black PLA | 100 % infill | Front on the bed |
| `box_cover.3mf` | 2 letters cover halves | Black PLA | 100 % infill | Front on the bed |
| `box_legs.3mf` | 2 legs | Black PLA | 100 % infill | Flat |

### 3.1 Fit test first

Before the whole box, print one plate of small pieces cut from the real
parts. It takes a fraction of the filament and shows whether the fits work
with your printer and filament:

```bash
uv run wordclock-cad --box --test    # build/bambu/box_test.3mf, one plate
```

| Piece | What to check |
|-------|---------------|
| `seam_left` + `seam_right` | The dovetail slides in without forcing and holds; an M5 × 25 bolt goes through both blocks and the nut sits in its hex pocket |
| `pi_corner` | The Raspberry Pi sits on the two posts with M2.5 screws; the microSD card comes out through the slot; the DC jack fits its hole; a magnet presses into a post |
| `face_band_left` + `face_band_right` | The face dovetail; the camera and the microphone see through their rivets; the plain rivets look the same |
| `face_corner` | A magnet presses into the pocket and holds against a post magnet |
| `grid_corner` | The strip passes under the walls through the notches; the lug sits on a 3 mm pin; the light of one LED fills the cell |
| `cover_letters` | Two letters, with tracing paper behind, lit by one LED; a magnet in its pocket |

If a fit is too tight or too loose, change `joint_gap`, `magnet_fit` or
`slot_fit` at the top of the model and print the test again.

To change a size, edit the parameters at the top of
`wordclock/cad/matrix_box.scad` and render again. The model also draws
assembly views for the OpenSCAD GUI: set `part` to `assembly`, `exploded`,
`inside`, `wall`, `table` or `letters`.

---

## 4. Joints

| Joint | How |
|-------|-----|
| Shell tiles | Dovetails in the 3 mm back plate, plus M5 bolts through blocks across the seams, in the margins: nut pockets on the bottom and left tiles |
| Face tiles | Dovetails in the margins and the band; the face sits on the shell with magnets, three per tile |
| Grid halves | Lugs at the foot of the frame over 3 mm pins in the back plate; the face holds them down through the paper |
| Letters cover | Two halves, four magnets each, into pockets in the front of the face |
| Legs | Two hooks each go through slots in the back plate and slide down |

```
   section through a shell seam block (bottom tile on the left)

           nut       M5 bolt
         ┌──⬡──────────────────┐
   ━━━━━━┷━━━━━━━━━━━━━━━━━━━━━┷━━━━━━  back plate, dovetail at the seam
         bottom tile │ top tile
```

---

## 5. Inside

| Part | Mount |
|------|-------|
| Display | Four posts from the back plate, M3 countersunk screws from the wall side into the threaded holes of its frame. It is fixed to the box, not to the face, so the face comes off without touching it |
| Camera | Four posts, M2; the lens against the back of the camera rivet, which is a through hole |
| Microphone | A cradle that holds it against the back of the microphone rivet |
| Raspberry Pi | Upright left of the display on four posts, M2.5. USB and Ethernet up; the microSD card down, reached through a slot in the bottom wall |
| Arduino Uno | Upright right of the display on four posts, USB-B up so the cable has room |
| Power | DC jack in the bottom wall, two WAGO connectors next to the Pi |
| Air | Slots in the bottom wall under the Pi and high in the left wall |

---

## 6. Wiring

```
   jack ──► WAGO 5 V ──┬──► Pi pin 2 (5 V)
            WAGO GND ──┼──► Pi pin 6 (GND)
                       ├──► display driver board 5 V / GND
                       └──► strip input 5 V / GND (left side, up to the bottom-left cell)

   Pi pin 12 (GPIO 18) ── 330 Ω ──► strip DIN
   Pi DSI  ═══ ribbon, under the display ═══► display driver board
   Pi CSI  ═══ 30 cm ribbon, up the left and across the band ═══► camera
   Pi USB  ──► microphone          Pi USB ──► Arduino Uno (power and data)
```

| From | To | Wire |
|------|----|------|
| DC jack | WAGO 5 V and GND | 0,75 mm² (18 AWG) |
| WAGO | Pi pins 2 and 6 | 0,5 mm², Dupont at the Pi end |
| WAGO | Strip input 5 V and GND | 0,75 mm² |
| WAGO | Display driver board 5 V and GND | 0,5 mm² |
| Pi pin 12 (GPIO 18) | Strip DIN, through 330 Ω | 0,25 mm² |

The strip starts at the bottom-left cell, next to the Pi, so the input
wires are short. That is upside down and mirrored from the first matrix:
run the show with `--rotate --mirror`. The Pi is powered from its 5 V pins,
so there is no micro-USB plug in the way.

---

## 7. Assemble

1. Press the face magnets into the 12 posts of the shell tiles, all with
   the same pole up, and the matching magnets into the back of the face
   tiles. Do the same for the cover: 8 in the front of the face, 8 in the
   cover halves.
2. Slide the shell tiles together on their dovetails, then bolt the seams:
   3 × M5 × 25 down the middle, 4 × M5 × 16 across.
3. Fit the DC jack, the WAGO connectors, the Raspberry Pi, the camera, the
   microphone and, if used, the Arduino.
4. Screw the display onto its posts from the back with the four M3
   countersunk screws; connect the DSI ribbon.
5. Stick the strip on the back plate in a snake, starting at the
   bottom-left cell, and solder the row joints in the side margins.
6. Wire everything as in section 6. Test with `wordclock-matrix wiring
   --rotate --mirror` before closing.
7. Set the grid halves on their pins, the strip passing under the walls
   through the notches. Lay the tracing paper on the grid.
8. Slide the face tiles together and set the face on the box: the magnets
   pull it into place and the glass sits in its window.
9. For the letters cover: set its two halves on the grid area of the face.

To open the box, pull the face off from one corner; everything inside is
reachable without removing the display.

---

## 8. Hang or stand

| Where | How |
|-------|-----|
| Wall | Two M5 screws 100 mm apart, heads about 3 mm proud of the wall; the box drops onto them through the keyholes |
| Table | Hook the two legs into the slots in the back and slide them down; the box leans back 15° |

---

## 9. Build checklist

- [ ] Fit test printed and checked (`uv run wordclock-cad --box --test`)
- [ ] Shell, grid, face, cover and legs printed (`uv run wordclock-cad --box`)
- [ ] Magnets pressed in, polarity checked on the face and the cover
- [ ] Shell tiles joined with 7 × M5
- [ ] Jack, WAGO connectors, Pi, camera and microphone fitted
- [ ] Display screwed on from the back, DSI ribbon connected
- [ ] Strip stuck and soldered, starting at the bottom-left cell
- [ ] `wiring` scene with `--rotate --mirror` lights the 60 cells in order
- [ ] Grid halves on their pins, paper on, face on
- [ ] Camera and microphone checked through their rivets
- [ ] Hung on the wall or standing on its legs
