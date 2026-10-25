// Mini LED matrix: 10 x 6 cells over a WS2812B strip with 30 LEDs/metre.
//
// A quick build before the word clock: one LED per cell, 33.3 mm pitch, the
// 2 m Tremex strip cut into 6 rows of 10 and wired in a snake. All sizes are
// in millimetres, in "front view" coordinates: x to the right, y up, row 0
// at the top. The panel is 37.7 cm wide, so the grid and the face are split
// into a left and a right half for the 25 cm bed of the Bambu Lab A1.
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
// grid | face | box | assembly | standing | none (library use)
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
outer_t = 2;
// Space between the matrix and the outer wall. The side margins take the
// wires that join the rows, with room for a soldering iron; the bottom
// margin takes the strip input wires to the box.
margin = 22;
// Notch at the bottom of every wall the strip passes under
strip_w = 13;
strip_notch_h = 3;
// Holes in the back plate for the strip input wires, in the bottom margin
// behind the box, one on each side of the seam. The wires run from the
// start of row 0 along the margins, hidden behind the face border.
cable_hole = [20, 12];
cable_hole_dx = 25;

/* [Seam bolts] */
// M3 bolts that join the two grid halves: one in the top margin and one in
// the bottom margin, where the bolt heads and nuts can be reached
bolt_d = 3.4;
bolt_block = 6;

/* [Front face] */
// Black face with one square window per cell, printed front side down
face_t = 2;
// Width of the bars between the windows
bar_w = 3;
window_r = 1.5;
// Skirt that hugs the grid outer wall and holds the face in place
skirt_t = 1.6;
skirt_h = 6;
fit = 0.2;
// Paper diffuser between the face and the grid (assembly view only)
paper_t = 0.3;

/* [Stand box] */
// Box at the bottom of the back, centred on the seam. On a table its
// slanted base and the bottom edge of the grid rest on the table; on a wall
// it hangs from two screws through keyholes in its back.
box_w = 120;
box_h = 101;
// The matrix leans back by this angle when it stands on the table
tilt = 15;
// Depth from the back plate of the grid to the back of the box. It sets the
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
panel_h = rows * pitch + 2 * margin;
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
    difference() {
        square([panel_w, panel_h]);
        translate([outer_t, outer_t]) square([panel_w - 2 * outer_t, panel_h - 2 * outer_t]);
    }
    cols_in_half = h == 0 ? [0:split_col] : [split_col:cols];
    for (k = cols_in_half) column_wall(k, h);
    for (k = [0:rows]) row_wall(k, h);
}

// Bolt positions along the seam: top margin and bottom margin.
bolt_ys = [panel_h - margin / 2, margin / 2];
bolt_z = back_t + grid_h / 2;

module seam_blocks(h) {
    side = h == 0 ? -bolt_block : 0;
    // Margin blocks span the full height, from the matrix to the outer wall.
    for (y = bolt_ys)
        translate([seam_x + side, y - (margin - outer_t) / 2, 0])
            cube([bolt_block, margin - outer_t, back_t + grid_h]);
}

module seam_holes() {
    for (y = bolt_ys)
        translate([seam_x - bolt_block - 1, y, bolt_z]) rotate([0, 90, 0]) cylinder(d = bolt_d, h = 2 * bolt_block + 2);
}

// Strip notches under every column wall, at the centre of each row.
module strip_notches(h) {
    cols_in_half = h == 0 ? [0:split_col] : [split_col:cols];
    for (k = cols_in_half, r = [0:rows - 1])
        translate([line_x(k) - wall_t - 1, cell_y(r) - strip_w / 2, back_t - 0.01])
            cube([2 * wall_t + 2, strip_w, strip_notch_h + 0.01]);
}

// Margin channel between the outer wall and the last row wall, [y_min, y_max].
bottom_channel = [outer_t, line_y(rows) - wall_t / 2];

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

module grid(h) {
    difference() {
        intersection() {
            union() {
                cube([panel_w, panel_h, back_t]);
                translate([0, 0, back_t]) linear_extrude(grid_h) walls_2d(h);
                seam_blocks(h);
            }
            translate([0, 0, -1]) linear_extrude(back_t + grid_h + 2) half_rect(h);
        }
        strip_notches(h);
        seam_holes();
        for (p = box_pins()) translate(p) pin_slot();
        for (x = pin_xs, k = pin_lines) translate([x, line_y(k)]) pin_tunnel();
        for (dx = [-cable_hole_dx, cable_hole_dx])
            translate([seam_x + dx - cable_hole[0] / 2, (bottom_channel[0] + bottom_channel[1] - cable_hole[1]) / 2, -1])
                cube([cable_hole[0], cable_hole[1], back_t + 2]);
    }
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
    linear_extrude(face_t) difference() {
        half_rect(h, skirt_out);
        windows_2d(h);
    }
    translate([0, 0, face_t]) linear_extrude(skirt_h) intersection() {
        difference() {
            translate([-skirt_out, -skirt_out]) square([panel_w + 2 * skirt_out, panel_h + 2 * skirt_out]);
            translate([-fit, -fit]) square([panel_w + 2 * fit, panel_h + 2 * fit]);
        }
        half_rect(h, skirt_out);
    }
}

// Printed front side down, so it is mirrored to read correctly once flipped.
module face(h) {
    mirror([1, 0, 0]) face_body(h);
}

// --- Stand box --------------------------------------------------------------

// The box sits behind the grid, from z = -box_d (its back) to z = 0 (the
// back plate), in front-view coordinates. On the table, the bottom edge of
// the grid back plate (y = 0, z = 0) and the slanted base of the box lie on
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
        color("white") grid(h);
        top = back_t + grid_h;
        color("ivory", 0.6) translate([0, 0, top + explode / 2]) cube([panel_w, panel_h, paper_t]);
        // The face body has its front at z = 0: flip it onto the grid.
        color("#222") translate([0, 0, top + paper_t + face_t + explode]) mirror([0, 0, 1]) face_body(h);
    }
    color("#333") translate([0, 0, -explode]) box();
}

module standing_assembly() {
    rotate([90 - tilt, 0, 0]) assembly();
}

if (part == "grid") grid(half);
else if (part == "face") face(half);
else if (part == "box") box_print();
else if (part == "assembly") assembly();
else if (part == "standing") standing_assembly();
