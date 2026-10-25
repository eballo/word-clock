// Mini LED matrix: 10 x 6 cells over a WS2812B strip with 30 LEDs/metre.
//
// A quick build before the word clock: one LED per cell, 33.3 mm pitch, the
// 2 m Tremex strip cut into 6 rows of 10 and wired in a snake. All sizes are
// in millimetres, in "front view" coordinates: x to the right, y up, row 0
// at the top. The panel is 37.7 cm wide, so every layer is split into a left
// and a right half for the 25 cm bed of the Bambu Lab A1.
//
// Three layers click together, no glue:
//   tray  flat back plate with a rim: the strip is stuck and soldered on it
//         with nothing in the way
//   grid  the cell walls only; bridges at the top click into the tray rim
//   face  one window per cell and decorative rivets around the border, one
//         of them a window for the camera; its skirt clicks onto the rim
//
// Another rivet is a printed button cap that presses a tactile switch.
//
//   openscad -o grid_left.stl -D 'part="grid"' -D 'half=0' matrix.scad
//
// A compact box slides onto the back. Its base is cut at an angle, so the
// matrix stands on a table leaning back, and keyholes in its back hang it on
// a wall. It hides the Raspberry Pi and the wiring; only the power cable
// comes out.
//
// Prefer `uv run wordclock-cad --matrix`, which renders every part.

/* [Part selection] */
// tray | grid | face | box | button | assembly | standing | none (library use)
part = "assembly";
// 0 = left half, 1 = right half
half = 0;
// Gap between the face and the grid in the assembly view (0 = assembled)
explode = 0;

/* [Matrix] */
cols = 10;
rows = 6;
// WS2812B strip, 30 LEDs/metre: one LED per cell
pitch = 1000 / 30;
// Column where the halves meet
split_col = 5;

/* [Light grid] */
wall_t = 1.2;
// Height of the walls between the back plate and the paper. Taller walls
// spread the light of a single LED more evenly over its cell.
grid_h = 22;
back_t = 2;
// Tray rim, the outer wall of the matrix
outer_t = 2;
// Space between the matrix and the rim. The side margins take the wires
// that join the rows, with room for a soldering iron; the bottom margin
// takes the strip input wires to the box, and is wider for the camera
// board, close to the box.
margin = 22;
margin_bottom = 28;
// Notch at the bottom of every wall the strip passes under
strip_w = 13;
strip_notch_h = 3;
// Shallow grooves in the tray along both edges of every strip, to line the
// strip up before the grid is on
guide_w = 0.8;
guide_depth = 0.4;
// Holes in the back plate for the strip input wires and the camera cable,
// in the bottom margin behind the box, one on each side of the seam. The
// wires run along the margins, hidden behind the face border.
cable_hole = [20, 12];
cable_hole_dx = 25;

/* [Click fit] */
// Bridges from the grid across the margin, at the top of the walls, end in
// a bump that clicks into a hole in the tray rim. The face skirt clicks
// into the same holes from outside, and then holds the rim in.
bridge_w = 6;
bridge_h = 5;
bump_d = 2.4;
grid_bump = 1;
face_bump = 0.6;
click_hole_d = 2.6;
rim_gap = 0.3;

/* [Seam bolts] */
// M3 bolts that join the two tray halves, in blocks in the top and bottom
// margins
bolt_d = 3.4;
bolt_block = 6;
bolt_block_h = 10;

/* [Front face] */
// Black face with one square window per cell, printed front side down
face_t = 2;
// Width of the bars between the windows
bar_w = 3;
window_r = 1.5;
// Skirt that hugs the tray rim and clicks onto it
skirt_t = 1.6;
skirt_h = 6;
fit = 0.2;
// Rivets: round recesses around the border, about rivet_pitch apart
rivet_d = 6;
rivet_depth = 1;
rivet_pitch = 21;
// Paper diffuser between the face and the grid, cut to the grid
paper_t = 0.3;

/* [Camera] */
// OV5647 camera board in the bottom margin, its lens behind one of the
// bottom rivets, which is a through window, next to the cable hole to the
// box. Sizes of the Raspberry Pi Camera v1.3: measure your board and adjust.
cam_board = [25, 24];
cam_holes = [[2, 2], [23, 2], [2, 14.5], [23, 14.5]];
// Lens centre on the board, from its lower left corner as mounted, and the
// height of the lens above the board
cam_lens = [12.5, 9.5];
cam_lens_h = 6;
cam_board_t = 1;
cam_hole_d = 2.2;
cam_post_d = 4.5;
// Bottom rivet with the camera, counted from the left
cam_rivet = 6;

/* [Button] */
// 6 x 6 mm tactile switch on a pillar in the bottom margin, behind the
// bottom rivet that mirrors the camera. That rivet is a printed cap: press
// it and it presses the switch. Measure your switch and adjust.
btn_body = 6;
// From the base of the switch body to the top of its plunger
btn_h = 5;
// Legs on the two sides along x, 6.5 mm apart: the pillar is narrower, so
// they hang free for soldering.
btn_pillar = [5, 6];
btn_side_h = 1.5;
btn_cap_d = 5.6;
btn_flange_d = 9;
btn_flange_t = 1;
btn_stem_d = 3;
btn_stem_l = 3;
btn_gap = 0.2;

/* [Stand box] */
// Box at the bottom of the back, centred on the seam. On a table its
// slanted base and the bottom edge of the tray rest on the table; on a wall
// it hangs from two screws through keyholes in its back.
box_w = 120;
box_h = 107;
// The matrix leans back by this angle when it stands on the table
tilt = 15;
// Depth from the back plate of the tray to the back of the box. It sets the
// depth of the base on the table, and so how stable the matrix stands.
box_d = 40;
box_wall = 2.4;
box_floor = 2.4;
// Slide lock: four pins with wide heads go through keyhole slots in the
// back plate on the row lines [lower, upper], then the box slides down and
// the heads hold it against the back plate. Each slot crosses under its row
// wall through a low tunnel, so the heads stay between the strips. Gravity
// keeps the box locked, on a table and on a wall.
pin_lines = [5, 4];
pin_neck_d = 4;
pin_head_d = 8;
// Cone under the head that pulls the box tight as it slides down, and the
// flat cap on top
pin_cone_h = 2;
pin_cap_h = 1;
// Column that carries the pin from the floor of the box
pin_column_d = 10;
// Distance the box slides down to lock
pin_slide = 10;
// Play around the pin in the slot, and between the cone and the back plate
pin_fit = 0.2;
// Raspberry Pi 3B / 4B: 85 x 56 mm board, holes on 58 x 49 mm, 3.5 mm from
// the long edge with the micro-USB and HDMI ports. The board lies across
// the box between the pin columns: ports up towards a window in the top
// wall, microSD card towards a slot in the right wall.
rpi_board = [85, 56];
rpi_holes = [[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]];
rpi_thick = 1.6;
// Standoffs, tall enough for the snap hook to flex
rpi_standoff_h = 10;
rpi_standoff_d = 6;
// Short pegs on the standoffs that go into the board holes (2.7 mm)
rpi_peg_d = 2.3;
rpi_peg_h = 2;
// Gap between the port edge of the board and the top wall
rpi_gap = 1;
// Height of the USB and Ethernet stack above the board
rpi_ports_h = 17;
// Click mount, no screws: the port edge goes under two lips on the top
// wall, then the other edge is pushed down until a snap hook clicks over it.
// The lips and the hook sit where the board edges have no parts.
lip_over = 1.5;
lip_spans = [[0.5, 4], [62, 80]];
hook_span = [65, 80];
hook_t = 1.8;
hook_over = 1.2;
// Window in the top wall for the micro-USB and HDMI plugs, from the end of
// the board with the microSD card, and its height around the ports
port_window = [5, 46];
port_window_h = 15;
// Slot in the right wall to reach the microSD card, [length, height]
sd_slot = [16, 8];
// Keyholes in the back for two wall screws, heads up to 8 mm
wall_keyhole_dx = 60;
wall_head_d = 8.6;
wall_neck_d = 4.6;
wall_slide = 8;
// Panel-mount 5.5 x 2.1 mm DC jack in the left wall, low (DC-022: 11 mm
// thread). On a table and on a wall, its cable leaves from the side.
jack_d = 11.4;
// Ventilation slots in the back under the Raspberry Pi and in the left wall
vent = [3, 20];

$fn = 32;

panel_w = cols * pitch + 2 * margin;
panel_h = rows * pitch + margin + margin_bottom;
rim_h = back_t + grid_h + paper_t;
seam_x = line_x(split_col);
skirt_out = fit + skirt_t;

// Position of grid line k: the line between cell k-1 and k.
function line_x(k) = margin + k * pitch;
function line_y(k) = panel_h - margin - k * pitch;
function cell_x(c) = line_x(c) + pitch / 2;
function cell_y(r) = line_y(r) - pitch / 2;

// Horizontal extent of a half, with `grow` added on its outer side.
function half_x0(h, grow = 0) = h == 0 ? -grow : seam_x;
function half_x1(h, grow = 0) = h == 0 ? seam_x : panel_w + grow;

module half_rect(h, grow = 0) {
    translate([half_x0(h, grow), -grow]) square([half_x1(h, grow) - half_x0(h, grow), panel_h + 2 * grow]);
}

// Margin channels between the rim and the grid frame, as [y_min, y_max].
top_channel = [line_y(0) + wall_t / 2, panel_h - outer_t];
bottom_channel = [outer_t, line_y(rows) - wall_t / 2];

// --- Click points ------------------------------------------------------------

// Click points of half h: [point on the outer face of the rim, outward
// direction]. Two on each side, on the grid lines next to the corners.
function clicks(h) = h == 0
    ? [[[0, line_y(1)], [-1, 0]], [[0, line_y(rows - 1)], [-1, 0]], [[line_x(1), panel_h], [0, 1]], [[line_x(1), 0], [0, -1]]]
    : [[[panel_w, line_y(1)], [1, 0]], [[panel_w, line_y(rows - 1)], [1, 0]], [[line_x(cols - 1), panel_h], [0, 1]], [[line_x(cols - 1), 0], [0, -1]]];

click_z = back_t + grid_h - bridge_h / 2;

// Place children at a click point, local +x pointing out of the rim.
module at_click(c) {
    translate(c[0]) rotate([0, 0, atan2(c[1][1], c[1][0])]) children();
}

// Distance from the outer face of the rim to the grid frame at a click.
function click_margin(c) = c[1][1] < 0 ? margin_bottom : margin;

// --- Camera -----------------------------------------------------------------

// Rivet centres: rows in the top and bottom margins, columns in the side
// margins, sharing the corners. The bottom row is level with the camera lens.
rivet_x0 = margin / 2;
rivet_x1 = panel_w - margin / 2;
rivet_nx = round((rivet_x1 - rivet_x0) / rivet_pitch);
cam_y0 = bottom_channel[0] + 0.4;
rivet_bottom = cam_y0 + cam_lens[1];
rivet_top = panel_h - margin / 2;
rivet_ny = round((rivet_top - rivet_bottom) / rivet_pitch);
function rivet_x(i) = rivet_x0 + i * (rivet_x1 - rivet_x0) / rivet_nx;
function rivet_y(j) = rivet_bottom + j * (rivet_top - rivet_bottom) / rivet_ny;
function rivets() = concat(
    [for (i = [0:rivet_nx]) [rivet_x(i), rivet_top]],
    [for (i = [0:rivet_nx]) [rivet_x(i), rivet_bottom]],
    [for (x = [rivet_x0, rivet_x1], j = [1:rivet_ny - 1]) [x, rivet_y(j)]]
);
cam_lens_xy = [rivet_x(cam_rivet), rivet_bottom];
cam_x0 = cam_lens_xy[0] - cam_lens[0];
// Board back, on posts that bring the lens up to the back of the face.
cam_z = rim_h - cam_lens_h - cam_board_t;

assert(cam_y0 + cam_board[1] < bottom_channel[1] - 0.2, "Camera board too tall for the bottom margin: raise margin_bottom");
assert(
    cam_x0 + cam_board[0] < seam_x - cable_hole_dx - cable_hole[0] / 2 - 1,
    "Camera board over the cable hole: change cam_rivet"
);

// Button behind the bottom rivet that mirrors the camera, its cap flush with
// the other rivets.
btn_xy = [rivet_x(rivet_nx - cam_rivet), rivet_bottom];
btn_cap_front = rim_h + face_t - rivet_depth;
btn_flange_z = rim_h - btn_flange_t;
btn_base = btn_flange_z - btn_stem_l - btn_gap - btn_h;

assert(
    btn_xy[0] - btn_flange_d / 2 > seam_x + cable_hole_dx + cable_hole[0] / 2 + 1,
    "Button over the cable hole: change cam_rivet"
);

// Pillar for the switch, with low sides along x that keep it in place.
module btn_pillar() {
    translate([btn_xy[0], btn_xy[1], 0]) {
        translate([-btn_pillar[0] / 2, -btn_pillar[1] / 2, 0]) cube([btn_pillar[0], btn_pillar[1], btn_base]);
        for (side = [-1, 1])
            translate([-btn_pillar[0] / 2, side > 0 ? btn_body / 2 + 0.2 : -btn_body / 2 - 1.4, 0])
                cube([btn_pillar[0], 1.2, btn_base + btn_side_h]);
    }
}

// Button cap in place: front in the rivet window, flange behind the face,
// stem down to the switch.
module button() {
    translate([btn_xy[0], btn_xy[1], 0]) {
        translate([0, 0, rim_h]) cylinder(d = btn_cap_d, h = btn_cap_front - rim_h);
        translate([0, 0, btn_flange_z]) cylinder(d = btn_flange_d, h = btn_flange_t);
        translate([0, 0, btn_flange_z - btn_stem_l]) cylinder(d = btn_stem_d, h = btn_stem_l + 0.01);
    }
}

// Printed front down.
module button_print() {
    translate([0, 0, btn_cap_front]) mirror([0, 0, 1]) translate([-btn_xy[0], -btn_xy[1], 0]) button();
}

module cam_posts() {
    for (hole = cam_holes) translate([cam_x0 + hole[0], cam_y0 + hole[1], 0]) {
        cylinder(d = cam_post_d, h = cam_z);
        cylinder(d = cam_hole_d - 0.2, h = cam_z + cam_board_t + 1);
    }
}

// --- Tray -------------------------------------------------------------------

// Bolt positions along the seam: middle of the top and bottom channels.
bolt_ys = [(top_channel[0] + top_channel[1]) / 2, (bottom_channel[0] + bottom_channel[1]) / 2];
bolt_z = back_t + bolt_block_h / 2;

module seam_blocks(h) {
    side = h == 0 ? -bolt_block : 0;
    for (channel = [top_channel, bottom_channel])
        translate([seam_x + side, channel[0] + rim_gap, 0])
            cube([bolt_block, channel[1] - channel[0] - rim_gap, back_t + bolt_block_h]);
}

module seam_holes() {
    for (y = bolt_ys)
        translate([seam_x - bolt_block - 1, y, bolt_z]) rotate([0, 90, 0]) cylinder(d = bolt_d, h = 2 * bolt_block + 2);
}

module rim_2d() {
    difference() {
        square([panel_w, panel_h]);
        translate([outer_t, outer_t]) square([panel_w - 2 * outer_t, panel_h - 2 * outer_t]);
    }
}

module tray(h) {
    difference() {
        intersection() {
            union() {
                cube([panel_w, panel_h, back_t]);
                linear_extrude(rim_h) rim_2d();
                seam_blocks(h);
                cam_posts();
                btn_pillar();
            }
            translate([0, 0, -1]) linear_extrude(rim_h + 2) half_rect(h);
        }
        seam_holes();
        for (r = [0:rows - 1], side = [-1, 1])
            translate([line_x(0), cell_y(r) + side * strip_w / 2 - guide_w / 2, back_t - guide_depth])
                cube([cols * pitch, guide_w, guide_depth + 1]);
        for (p = box_pins()) translate(p) pin_slot();
        for (dx = [-cable_hole_dx, cable_hole_dx])
            translate([seam_x + dx - cable_hole[0] / 2, (bottom_channel[0] + bottom_channel[1] - cable_hole[1]) / 2, -1])
                cube([cable_hole[0], cable_hole[1], back_t + 2]);
        for (c = clicks(h))
            at_click(c) translate([-outer_t - 1, 0, click_z]) rotate([0, 90, 0]) cylinder(d = click_hole_d, h = outer_t + 2);
    }
}

// --- Light grid -------------------------------------------------------------

// Wall on vertical line k, cut back to the seam side of half h.
module column_wall(k, h) {
    x = line_x(k);
    x0 = k == split_col ? (h == 0 ? x - wall_t : x) : x - wall_t / 2;
    translate([x0, line_y(rows) - wall_t / 2]) square([wall_t, rows * pitch + wall_t]);
}

module row_wall(k, h) {
    x0 = h == 0 ? line_x(0) - wall_t / 2 : seam_x;
    x1 = h == 0 ? seam_x : line_x(cols) + wall_t / 2;
    translate([x0, line_y(k) - wall_t / 2]) square([x1 - x0, wall_t]);
}

module walls_2d(h) {
    cols_in_half = h == 0 ? [0:split_col] : [split_col:cols];
    for (k = cols_in_half) column_wall(k, h);
    for (k = [0:rows]) row_wall(k, h);
}

// Bridge across the margin at a click point, with its bump.
module bridge(c) {
    m = click_margin(c);
    at_click(c) {
        translate([-m, -bridge_w / 2, click_z - bridge_h / 2]) cube([m - outer_t - rim_gap, bridge_w, bridge_h]);
        translate([-outer_t - rim_gap - (bump_d / 2 - grid_bump), 0, click_z]) sphere(d = bump_d);
    }
}

// Strip notches under every column wall, at the centre of each row.
module strip_notches(h) {
    cols_in_half = h == 0 ? [0:split_col] : [split_col:cols];
    for (k = cols_in_half, r = [0:rows - 1])
        translate([line_x(k) - wall_t - 1, cell_y(r) - strip_w / 2, back_t - 0.01])
            cube([2 * wall_t + 2, strip_w, strip_notch_h + 0.01]);
}

// Sides of the stand box, used by the grid for the pin slots.
box_x0 = seam_x - box_w / 2;
box_x1 = seam_x + box_w / 2;

// Box pins near its side walls, on the row lines. Each pin locks half a
// slide below its row line and enters half a slide above it.
pin_xs = [
    box_x0 + box_wall + pin_column_d / 2 + 1,
    box_x1 - box_wall - pin_column_d / 2 - 1,
];
function box_pins() = [for (x = pin_xs, k = pin_lines) [x, line_y(k) - pin_slide / 2]];

assert(
    pin_slide / 2 + pin_head_d / 2 + pin_fit < pitch / 2 - strip_w / 2,
    "Pin heads would reach the strip: shorten pin_slide or the head"
);

// Keyhole slot in the back plate: wide entry at the top, narrow slot down
// to the locked position.
module pin_slot() {
    translate([0, pin_slide, -1]) cylinder(d = pin_head_d + 2 * pin_fit, h = back_t + 2);
    hull() for (dy = [0, pin_slide]) translate([0, dy, -1]) cylinder(d = pin_neck_d + 2 * pin_fit, h = back_t + 2);
}

// Pin on its column, from the floor of the box through the back plate.
module box_pin() {
    cone_z = back_t + pin_fit;
    translate([0, 0, -box_d]) cylinder(d = pin_column_d, h = box_d);
    cylinder(d = pin_neck_d, h = cone_z + 0.01);
    translate([0, 0, cone_z]) cylinder(d1 = pin_neck_d, d2 = pin_head_d, h = pin_cone_h);
    translate([0, 0, cone_z + pin_cone_h]) cylinder(d = pin_head_d, h = pin_cap_h);
}

// Tunnel at the foot of a row wall, for a pin head sliding across it.
module pin_tunnel() {
    translate([-pin_head_d / 2 - 1, -wall_t / 2 - 1, back_t - 0.01])
        cube([pin_head_d + 2, wall_t + 2, pin_fit + pin_cone_h + pin_cap_h + 0.6]);
}

// Grid in place: on the tray back plate, from z = back_t up.
module grid(h) {
    difference() {
        union() {
            translate([0, 0, back_t]) linear_extrude(grid_h) walls_2d(h);
            for (c = clicks(h)) bridge(c);
        }
        strip_notches(h);
        for (x = pin_xs, k = pin_lines) translate([x, line_y(k)]) pin_tunnel();
    }
}

// Printed upside down: the bridges lie on the bed.
module grid_print(h) {
    translate([0, panel_h, back_t + grid_h]) rotate([180, 0, 0]) grid(h);
}

// --- Front face -------------------------------------------------------------

module windows_2d(h) {
    cols_in_half = h == 0 ? [0:split_col - 1] : [split_col:cols - 1];
    size = pitch - bar_w;
    for (c = cols_in_half, r = [0:rows - 1])
        translate([cell_x(c), cell_y(r)])
            offset(r = window_r) square(size - 2 * window_r, center = true);
}

// Face in body coordinates: front at z = 0, skirt towards the back (+z).
module face_body(h) {
    // Depth of the click points behind the front of the face.
    click_zb = rim_h + face_t - click_z;
    intersection() {
        difference() {
            union() {
                linear_extrude(face_t) half_rect(h, skirt_out);
                translate([0, 0, face_t]) linear_extrude(skirt_h) difference() {
                    translate([-skirt_out, -skirt_out]) square([panel_w + 2 * skirt_out, panel_h + 2 * skirt_out]);
                    translate([-fit, -fit]) square([panel_w + 2 * fit, panel_h + 2 * fit]);
                }
                for (c = clicks(h)) at_click(c) translate([fit + bump_d / 2 - face_bump, 0, click_zb]) sphere(d = bump_d);
            }
            translate([0, 0, -1]) linear_extrude(face_t + 2) windows_2d(h);
            for (r = rivets()) translate([r[0], r[1], -1]) cylinder(d = rivet_d, h = rivet_depth + 1);
            for (xy = [cam_lens_xy, btn_xy]) translate([xy[0], xy[1], -1]) cylinder(d = rivet_d, h = face_t + 2);
        }
        translate([0, 0, -1]) linear_extrude(face_t + skirt_h + 2) half_rect(h, skirt_out);
    }
}

// Printed front side down, so it is mirrored to read correctly once flipped.
module face(h) {
    mirror([1, 0, 0]) face_body(h);
}

// --- Stand box --------------------------------------------------------------

// The box sits behind the grid, from z = -box_d (its back) to z = 0 (the
// back plate), in front-view coordinates. On the table, the bottom edge of
// the tray back plate (y = 0, z = 0) and the slanted base of the box lie on
// one plane: y = table_y(z).
function table_y(z) = -z * tan(tilt);

box_y0 = 0;
box_y1 = box_h;
floor_z = -box_d + box_floor;

// Raspberry Pi across the box, component side towards the grid: the port
// edge at the top, the microSD card end on the right, clear of the right
// pin columns, and the USB and Ethernet ports on the left.
rpi_y1 = box_y1 - box_wall - rpi_gap;
rpi_xsd = pin_xs[1] - pin_column_d / 2 - 3.5;
rpi_bottom = floor_z + rpi_standoff_h;
rpi_top = rpi_bottom + rpi_thick;

// Board point [along the 85 mm side from the microSD end, along the 56 mm
// side from the port edge] in front-view coordinates.
function rpi_at(p) = [rpi_xsd - p[0], rpi_y1 - p[1]];

assert(rpi_top + rpi_ports_h < -2, "Box too shallow for the Raspberry Pi: raise box_d");
assert(rpi_xsd - rpi_board[0] - 2 > pin_xs[0] + pin_column_d / 2, "Box too narrow for the Raspberry Pi: raise box_w");
assert(line_y(pin_lines[1]) + pin_slide / 2 + pin_head_d / 2 < box_y1 - box_wall, "Box too low for the upper pins: raise box_h");

module box_outline(grow = 0) {
    translate([box_x0 - grow, box_y0 - grow]) square([box_x1 - box_x0 + 2 * grow, box_y1 - box_y0 + 2 * grow]);
}

// Everything above the table plane, raised by `lift` along y.
module above_table(lift = 0) {
    z0 = -box_d - 1;
    // High enough to keep the pins that reach into the grid
    z1 = back_t + 10;
    translate([box_x0 - 1, 0, 0]) rotate([90, 0, 90]) linear_extrude(box_x1 - box_x0 + 2)
        polygon([[table_y(z1) + lift, z1], [table_y(z0) + lift, z0], [panel_h + 1, z0], [panel_h + 1, z1]]);
}

// Lip on the top wall that holds the port edge of the board, over the
// board span [from, to] along its 85 mm side.
module rpi_lip(span) {
    translate([rpi_xsd - span[1], rpi_y1 - lip_over, rpi_top + 0.2])
        cube([span[1] - span[0], box_y1 - box_wall - rpi_y1 + lip_over + 0.01, 2]);
}

// Snap hook on the bottom edge of the board: a flexible arm from the floor
// with a lip at the top and a ramp that pushes it out as the board goes in.
module rpi_hook() {
    y_in = rpi_y1 - rpi_board[1] - 0.3;
    z0 = rpi_top + 0.2;
    z1 = z0 + 1;
    z_top = z1 + 2.5;
    translate([rpi_xsd - hook_span[1], 0, 0]) rotate([90, 0, 90]) linear_extrude(hook_span[1] - hook_span[0])
        polygon([
            [y_in, floor_z - 0.01], [y_in - hook_t, floor_z - 0.01], [y_in - hook_t, z_top], [y_in, z_top],
            [y_in + hook_over + 0.3, z1], [y_in + hook_over + 0.3, z0], [y_in, z0],
        ]);
}

// Click mount: standoffs with pegs in the board holes, two lips and a hook.
module rpi_mount() {
    for (hole = rpi_holes) translate([each rpi_at(hole), floor_z - 0.01]) {
        cylinder(d = rpi_standoff_d, h = rpi_standoff_h + 0.01);
        cylinder(d1 = rpi_peg_d, d2 = rpi_peg_d - 0.4, h = rpi_standoff_h + rpi_thick + rpi_peg_h);
    }
    for (span = lip_spans) rpi_lip(span);
    rpi_hook();
}

module box_shell() {
    intersection() {
        union() {
            difference() {
                translate([0, 0, -box_d]) linear_extrude(box_d) box_outline();
                intersection() {
                    translate([0, 0, floor_z]) linear_extrude(box_d) box_outline(-box_wall);
                    above_table(box_wall / cos(tilt));
                }
            }
            for (p = box_pins()) translate(p) box_pin();
            rpi_mount();
        }
        above_table();
    }
}

// Keyhole for a wall screw: wide entry at the bottom, narrow slot up, so
// the box drops onto the screw head.
module wall_keyhole() {
    translate([0, 0, -box_d - 1]) {
        cylinder(d = wall_head_d, h = box_floor + 2);
        hull() for (dy = [0, wall_slide]) translate([0, dy, 0]) cylinder(d = wall_neck_d, h = box_floor + 2);
    }
}

module box() {
    mid_y = (box_y0 + box_y1) / 2;
    difference() {
        box_shell();
        // Window in the top wall for the micro-USB and HDMI plugs
        translate([rpi_xsd - port_window[1], box_y1 - box_wall - 1, rpi_top - 4])
            cube([port_window[1] - port_window[0], box_wall + 2, port_window_h]);
        // Slot in the right wall to reach the microSD card under the board
        translate([box_x1 - box_wall - 1, rpi_y1 - 28 - sd_slot[0] / 2, rpi_bottom - sd_slot[1] + 2])
            cube([box_wall + 2, sd_slot[0], sd_slot[1]]);
        // DC jack in the left wall, low
        translate([box_x0 - 1, 25, -box_d / 2]) rotate([0, 90, 0]) cylinder(d = jack_d, h = box_wall + 2);
        // Wall keyholes
        for (dx = [-wall_keyhole_dx / 2, wall_keyhole_dx / 2]) translate([seam_x + dx, rpi_y1 - 40, 0]) wall_keyhole();
        // Vents in the back under the Raspberry Pi and in the left wall
        for (dx = [-10, 0, 10])
            translate([seam_x + dx - vent[0] / 2, rpi_y1 - 38, -box_d - 1]) cube([vent[0], vent[1], box_floor + 2]);
        for (y = [mid_y + 10, mid_y + 16, mid_y + 22])
            translate([box_x0 - 1, y - vent[0] / 2, floor_z + 4]) cube([box_wall + 2, vent[0], 14]);
    }
}

// Printed with its back on the bed.
module box_print() {
    translate([0, 0, box_d]) box();
}

// --- Assembly ---------------------------------------------------------------

module assembly() {
    for (h = [0, 1]) {
        color("white") tray(h);
        color("white") translate([0, 0, explode / 3]) grid(h);
        top = back_t + grid_h;
        color("ivory", 0.6) translate([line_x(0), line_y(rows), top + explode * 2 / 3])
            cube([cols * pitch, rows * pitch, paper_t]);
        // The face body has its front at z = 0: flip it onto the tray.
        color("#222") translate([0, 0, rim_h + face_t + explode]) mirror([0, 0, 1]) face_body(h);
    }
    color("#333") translate([0, 0, -explode]) box();
    color("#222") translate([0, 0, explode]) button();
}

module standing_assembly() {
    rotate([90 - tilt, 0, 0]) assembly();
}

if (part == "tray") tray(half);
else if (part == "grid") grid_print(half);
else if (part == "face") face(half);
else if (part == "box") box_print();
else if (part == "button") button_print();
else if (part == "assembly") assembly();
else if (part == "standing") standing_assembly();
