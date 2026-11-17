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
| 2 | Female DC jack adapter 5,5 × 2,1 mm with screw terminals (the CCTV kind) | Nose through the right wall, 11 cm up, body clipped in a cradle |
| 3 | 2 × WAGO 221-413 lever connectors | Share the 5 V and the ground |
| 4 | CSI ribbon cable, 15 pins, 30 cm | The camera is about 25 cm from the Pi: the 15 cm cable that comes with most OV5647 boards is too short |
| 5 | USB microphone, small (dongle size), optional | Behind the microphone rivet; set `mic = true` in the model first |
| 6 | 330 Ω resistor | In series with the LED data line |
| 7 | Short micro-USB cable to cut (power only) | Display power, see section 6 |
| 8 | Female-female jumper wires; 90° ones for the Arduino | Pi pins 2, 6 and 12; Arduino headers |
| 9 | 7 × M5 bolts and nuts: 3 × M5 × 25 mm (vertical seam), 4 × M5 × 16 mm (horizontal seam) | Join the shell tiles |
| 10 | 2 × M5 wall screws with plugs, heads up to 10 mm | Hang the box |
| 11 | 4 × M3 × 8 mm pan head (ISO 7045) | Display, from the back into its frame |
| 12 | 4 × M2.5 × 6 mm self-tapping | Raspberry Pi |
| 13 | 4 × M2 × 6 mm self-tapping | Camera |
| 14 | 4 × M3 × 6 mm self-tapping (optional) | Arduino Uno |
| 15 | 12 × M3 × 12 mm countersunk (ISO 10642), black if you can find them | Face, one into each post |
| 16 | 16 neodymium magnets, 5 × 2 mm | 8 in the front of the face, 8 in the letters cover |
| 17 | Tracing paper | Diffuser, cut to the grid |

The jack cradle is drawn for an adapter with an 11 mm round nose, 12 mm
long, and a 13,5 × 11,5 × 23 mm body. These vary between sellers: measure
yours with a caliper and set `jack_nose` and `jack_body` at the top of the
model before printing.

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
per plate, each with its filament colour already set. Everything you see
is black, so the box reads as one object; only the grid is white, so the
cells reflect the light:

| Project | Pieces | Filament | Settings | Orientation |
|---------|--------|----------|----------|-------------|
| `box_shell.3mf` | 4 shell tiles | Black PLA | 3 walls, 15 % infill | Back on the bed |
| `box_grid.3mf` | 2 grid halves | White PLA | 3 walls, 15 % infill | Upside down: wall tops on the bed |
| `box_face.3mf` | 4 face tiles | Black PLA | 100 % infill | Front up, so the rivet dimples print open |
| `box_cover.3mf` | 2 letters cover halves | Black PLA | 100 % infill | Front on the bed |
| `box_legs.3mf` | 2 legs | Black PLA | 100 % infill | Flat |

### 3.1 Fit test first

Before the whole box, print one plate of small pieces cut from the real
parts. It takes a fraction of the filament and shows whether the fits work
with your printer and filament:

```bash
uv run wordclock-cad --box --test    # box_test_black.3mf, box_test_white.3mf and box_test_jack.3mf
```

| Piece | What to check |
|-------|---------------|
| `seam_left` + `seam_right` | The dovetail slides in without forcing and holds; an M5 × 25 bolt goes through both blocks and the nut sits in its hex pocket |
| `pi_corner` | The Raspberry Pi sits on the two posts with M2.5 screws; the microSD card comes out through the slot |
| `face_band_left` + `face_band_right` | The face dovetail; the camera sees through its rivet; the plain rivets look the same |
| `face_corner` | Set it into `pi_corner`: it sits flush with the walls on the corner post, an M3 × 12 countersunk screw goes into the post with its head flush, and without the screw a fingernail lifts it out again |
| `grid_corner` | The strip passes under the walls through the notches; the lug sits on a 3 mm pin; the light of one LED fills the cell |
| `cover_letters` | Two letters, with tracing paper behind, lit by one LED; a magnet in its pocket |
| `jack_cradle` | Also alone in `box_test_jack.3mf`. The jack nose goes through the wall hole flush with the outside, the body clips between the rails under their lips, the plug goes in without pushing the jack back. Too tight or loose: change `jack_fit`, or `jack_nose` and `jack_body` |

If a fit is too tight or too loose, change `joint_gap`, `face_fit`, `magnet_fit` or
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
| Face tiles | Dovetails in the margins and the band. The face sits inside the shell walls, flush with them, on 12 posts, held by 12 M3 countersunk screws from the front, one into each post, three per tile, heads flush. No magnets |
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
| Display | Four 10 mm posts from the back plate up to the threaded M3 holes of its metal frame (126,2 × 65,65 mm apart). An M3 × 8 pan-head screw goes in from the wall side down a bore in each post and seats on a 4 mm shoulder, so it bites about 3 mm into the frame and never reaches the panel. The glass sits in the window of the face. The display is fixed to the box, not to the face, so the face comes off without touching it. Take off the four standoffs on its back that are meant for a Pi |
| Camera | OV5647 board, 25 × 24 mm with M2 holes 21 × 12,5 mm apart, on four posts with M2 × 6 screws, its ribbon connector down. The lens sits in a 12,5 mm pocket in the back of the face, 1 mm behind the front, so the 4 mm rivet hole does not crop the picture. Check the holes on yours before printing |
| Microphone | Optional, off by default. With `mic = true` the shell gets a cradle that holds it against the back of its rivet, and that rivet becomes a through hole: reprint the bottom-left shell tile and the bottom-left face tile (plate 1 of each project) |
| Raspberry Pi | Upright left of the display on four posts, M2.5, 14 mm from the left wall so a screwdriver passes the corner post. USB and Ethernet up; the microSD card down, reached through a slot in the bottom wall; the GPIO header along the left edge, pin 1 at the bottom |
| Arduino Uno | Upright right of the display on four 3 mm posts, USB-B up so the cable has room. Jumper wires in its headers need 90° plugs: straight ones reach the face |
| Power | DC jack adapter in a cradle at the right wall, 11 cm above the bottom edge, its screw terminals facing in. In the side wall the plug stays free both on the wall and on the legs, where the bottom edge rests on the table. Two WAGO connectors right of the Pi; the jack wires reach them under the display |
| Air | Slots in the bottom wall under the Pi and high in the left wall |

---

## 6. Wiring

```
   jack ──► WAGO 5 V ──┬──► Pi pin 2 (5 V)
            WAGO GND ──┼──► Pi pin 6 (GND)
                       ├──► display driver board micro-USB (cut cable)
                       └──► strip input 5 V / GND (left side, up to the bottom-left cell)

   Pi pin 12 (GPIO 18) ── 330 Ω ──► strip DIN
   Pi DSI  ═══ ribbon, under the display ═══► display driver board
   Pi CSI  ═══ 30 cm ribbon, up the left and across the band ═══► camera
   Pi USB  ──► microphone (optional)   Pi USB ──► Arduino Uno (power and data)
```

| From | To | Wire |
|------|----|------|
| DC jack | WAGO 5 V and GND, about 35 cm under the display | 0,75 mm² (18 AWG) |
| WAGO | Pi pins 2 and 6 | 0,5 mm², Dupont at the Pi end |
| WAGO | Strip input 5 V and GND | 0,75 mm² |
| WAGO | Display driver board, through a cut micro-USB cable (red 5 V, black GND) | Cable's own wires |
| Pi pin 12 (GPIO 18) | Strip DIN, through 330 Ω | 0,25 mm² |

Room for the plugs, checked in the model:

| Plug | Room |
|------|------|
| Jumper housings on the Pi header | 8,2 mm above them to bend the wires toward the WAGO connectors; the wires cross the bottom of the board |
| Display driver board | 15,3 mm under it: too little for straight jumpers on its 5 V pins (16,5 mm), so it takes its power through its micro-USB port |
| USB plugs on the Pi | About 40 mm above the ports, below the rivet row |
| Camera ribbon | From the CSI connector up over the USB ports, then across just above the display glass, into the bottom edge of the camera board |

The strip starts at the bottom-left cell, next to the Pi, so the input
wires are short. That is upside down and mirrored from the first matrix:
run the show with `--rotate --mirror`. The Pi is powered from its 5 V pins,
so there is no micro-USB plug in the way.

---

## 7. Assemble

1. Press the cover magnets in: 8 into the front of the face tiles, all
   with the same pole up, and 8 into the cover halves so they attract.
2. Slide the shell tiles together on their dovetails, then bolt the seams:
   3 × M5 × 25 down the middle, 4 × M5 × 16 across.
3. Fit the DC jack, the WAGO connectors, the Raspberry Pi, the camera, the
   microphone and the Arduino if used.
4. Lay the display face down on a towel, set the box on it so the posts
   meet the frame holes, and drive the four M3 × 8 screws in from the back
   down the bores; connect the DSI ribbon.
5. Stick the strip on the back plate in a snake, starting at the
   bottom-left cell, and solder the row joints in the side margins.
6. Wire everything as in section 6. Test with `wordclock-matrix wiring
   --rotate --mirror` before closing.
7. Set the grid halves on their pins, the strip passing under the walls
   through the notches. Lay the tracing paper on the grid.
8. Slide the face tiles together, set the face on the box with the glass
   in its window, and drive the twelve M3 × 12 countersunk screws into the
   posts until the heads sit flush; do not overtighten, they cut their own
   thread.
9. For the letters cover: set its two halves on the grid area of the face.

To open the box, take out the twelve face screws, put a fingernail or a
coin in one of the two notches in the top of the bottom wall and lift the
face out; everything inside is reachable without removing the display.

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
- [ ] Cover magnets pressed in, polarity checked
- [ ] Shell tiles joined with 7 × M5
- [ ] Jack, WAGO connectors, Pi and camera fitted
- [ ] Display screwed on from the back, DSI ribbon connected
- [ ] Strip stuck and soldered, starting at the bottom-left cell
- [ ] `wiring` scene with `--rotate --mirror` lights the 60 cells in order
- [ ] Grid halves on their pins, paper on, face on
- [ ] Camera checked through its rivet
- [ ] Hung on the wall or standing on its legs
