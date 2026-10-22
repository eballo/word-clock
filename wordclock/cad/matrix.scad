// Mini LED matrix: 10 x 6 cells over a WS2812B strip with 30 LEDs/metre.
//
// A quick build before the word clock: one LED per cell, 33.3 mm pitch, the
// 2 m Tremex strip cut into 6 rows of 10 and wired in a snake. All sizes are
// in millimetres, in "front view" coordinates: x to the right, y up, row 0
// at the top. The panel is 35.7 cm wide, so the grid and the face are split
// into a left and a right half for the 25 cm bed of the Bambu Lab A1.
//
//   openscad -o grid_left.stl -D 'part="grid"' -D 'half=0' matrix.scad
//
// A box screwed on the back is also the stand: its base is cut at an angle,
// so the matrix stands on a table leaning back. It hides the Raspberry Pi
// and the wiring; only the power cable comes out.
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
// Space between the matrix and the outer wall, for the wires that join the
// rows at the ends
margin = 12;
// Notch at the bottom of every wall the strip passes under
strip_w = 13;
strip_notch_h = 3;
// Hole in the back plate for the data and power wires, next to row 0
cable_hole = [7, 14];

/* [Seam bolts] */
// M3 bolts that join the two grid halves: one in the top margin, one in the
// bottom margin and one on the middle row wall
bolt_d = 3.4;
bolt_block = 6;
boss_h = 10;

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
// The box corners are screwed into bosses of the grid, on the grid line
// crossings [col_start, col_end, row_start, row_end]: 4 x 4 cells in the
// middle of the matrix, across the seam. The box reaches down to the bottom
// edge of the panel.
box_lines = [3, 7, 1, 5];
// How far the box reaches past the screw centres (sides and top)
box_overhang = 5;
// The matrix leans back by this angle when it stands on the table
tilt = 15;
// Depth from the back plate of the grid to the back of the box. It sets the
// depth of the base on the table, and so how stable the matrix stands.
box_d = 40;
box_wall = 2.4;
box_floor = 2.4;
// Corner columns with M3 screws from the back of the box. The screw head
// sits in a counterbore, so an M3 x 12 mm self-tapping screw goes through
// the rim and 6 mm into the grid boss.
box_column_d = 10;
box_screw_d = 3.4;
box_head_d = 6.5;
// Material left under the screw head, at the rim of the box
box_screw_grip = 6;
// Bosses on the grid back plate that take the screws (cell corners)
grid_boss_d = 7;
grid_boss_h = 5;
grid_pilot_d = 2.6;
// Raspberry Pi 3B / 4B: 85 x 56 mm board, M2.5 holes on 58 x 49 mm,
// 3.5 mm from the edge with the micro-USB and HDMI ports
rpi_board = [85, 56];
rpi_holes = [[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]];
rpi_standoff_h = 5;
rpi_standoff_d = 6;
rpi_pilot_d = 2.2;
// Height of the USB and Ethernet stack above the board
rpi_ports_h = 17;
// Panel-mount 5.5 x 2.1 mm DC jack in the back of the box, the only cable
// that comes out (DC-022: 11 mm hole)
jack_d = 11;
// Slot in the rim for the strip wires coming from the hole next to row 0
wire_slot = [12, 8];
// Ventilation slots in the back under the Raspberry Pi and in the top wall
vent = [3, 30];

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

// Bolt positions along the seam: top margin, middle row line, bottom margin.
bolt_ys = [panel_h - margin / 2, line_y(rows / 2), margin / 2];
function bolt_z(y) = y == line_y(rows / 2) ? back_t + boss_h - bolt_block / 2 : back_t + grid_h / 2;

module seam_blocks(h) {
    side = h == 0 ? -bolt_block : 0;
    // Margin blocks span the full height, from the matrix to the outer wall.
    for (y = [bolt_ys[0], bolt_ys[2]])
        translate([seam_x + side, y - (margin - outer_t) / 2, 0])
            cube([bolt_block, margin - outer_t, back_t + grid_h]);
    // Boss on the middle row wall, low enough to leave the cells clear.
    translate([seam_x + side, line_y(rows / 2) - bolt_block / 2, 0]) cube([bolt_block, bolt_block, back_t + boss_h]);
}

module seam_holes() {
    for (y = bolt_ys)
        translate([seam_x - bolt_block - 1, y, bolt_z(y)]) rotate([0, 90, 0]) cylinder(d = bolt_d, h = 2 * bolt_block + 2);
}

// Strip notches under every column wall, at the centre of each row.
module strip_notches(h) {
    cols_in_half = h == 0 ? [0:split_col] : [split_col:cols];
    for (k = cols_in_half, r = [0:rows - 1])
        translate([line_x(k) - wall_t - 1, cell_y(r) - strip_w / 2, back_t - 0.01])
            cube([2 * wall_t + 2, strip_w, strip_notch_h + 0.01]);
}

// Screw points of the stand box, on grid line crossings.
function box_screws() = [for (c = [box_lines[0], box_lines[1]], r = [box_lines[2], box_lines[3]]) [line_x(c), line_y(r)]];

module grid(h) {
    difference() {
        intersection() {
            union() {
                cube([panel_w, panel_h, back_t]);
                translate([0, 0, back_t]) linear_extrude(grid_h) walls_2d(h);
                seam_blocks(h);
                for (p = box_screws()) translate([p[0], p[1], 0]) cylinder(d = grid_boss_d, h = back_t + grid_boss_h);
            }
            translate([0, 0, -1]) linear_extrude(back_t + grid_h + 2) half_rect(h);
        }
        strip_notches(h);
        seam_holes();
        for (p = box_screws()) translate([p[0], p[1], -1]) cylinder(d = grid_pilot_d, h = back_t + grid_boss_h);
        if (h == 0)
            translate([(outer_t + line_x(0)) / 2 - cable_hole[0] / 2, cell_y(0) - cable_hole[1] / 2, -1])
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

box_x0 = line_x(box_lines[0]) - box_overhang;
box_x1 = line_x(box_lines[1]) + box_overhang;
box_y0 = 0;
box_y1 = line_y(box_lines[2]) + box_overhang;

// Raspberry Pi on the right, above the bottom screws, component side
// towards the grid. The space below it takes the power plug and the wiring.
rpi_x0 = box_x1 - box_wall - 4 - rpi_board[0];
rpi_y0 = line_y(box_lines[3]) + box_column_d / 2 + 2;
rpi_top = -box_d + box_floor + rpi_standoff_h + 1.6;

assert(rpi_top + rpi_ports_h < -2, "Box too shallow for the Raspberry Pi: raise box_d");

module box_outline(grow = 0) {
    translate([box_x0 - grow, box_y0 - grow]) square([box_x1 - box_x0 + 2 * grow, box_y1 - box_y0 + 2 * grow]);
}

// Everything above the table plane, raised by `lift` along y.
module above_table(lift = 0) {
    z0 = -box_d - 1;
    translate([box_x0 - 1, 0, 0]) rotate([90, 0, 90]) linear_extrude(box_x1 - box_x0 + 2)
        polygon([[table_y(1) + lift, 1], [table_y(z0) + lift, z0], [panel_h, z0], [panel_h, 1]]);
}

module box_shell() {
    intersection() {
        union() {
            difference() {
                translate([0, 0, -box_d]) linear_extrude(box_d) box_outline();
                intersection() {
                    translate([0, 0, -box_d + box_floor]) linear_extrude(box_d) box_outline(-box_wall);
                    above_table(box_wall / cos(tilt));
                }
            }
            for (p = box_screws()) translate([p[0], p[1], -box_d]) cylinder(d = box_column_d, h = box_d);
            for (hole = rpi_holes)
                translate([rpi_x0 + hole[0], rpi_y0 + hole[1], -box_d]) cylinder(d = rpi_standoff_d, h = box_floor + rpi_standoff_h);
        }
        above_table();
    }
}

module box() {
    mid_x = (box_x0 + box_x1) / 2;
    difference() {
        box_shell();
        // Corner screws, heads sunk from the back
        for (p = box_screws()) translate([p[0], p[1], -box_d - 1]) {
            cylinder(d = box_screw_d, h = box_d + 2);
            cylinder(d = box_head_d, h = box_d + 1 - box_screw_grip);
        }
        for (hole = rpi_holes) translate([rpi_x0 + hole[0], rpi_y0 + hole[1], -box_d + 1]) cylinder(d = rpi_pilot_d, h = box_d);
        // DC jack in the back, low and left of the Raspberry Pi
        translate([(box_x0 + rpi_x0) / 2, line_y(box_lines[3]) - box_column_d, -box_d - 1]) cylinder(d = jack_d, h = box_floor + 2);
        // Strip wires come in through the rim, next to the top-left corner
        translate([box_x0 + box_column_d + 2, box_y1 - box_wall - 1, -wire_slot[1]]) cube([wire_slot[0], box_wall + 2, wire_slot[1] + 1]);
        // Vents in the back under the Raspberry Pi and in the top wall
        for (i = [0:5])
            translate([rpi_x0 + 12 + i * 10, rpi_y0 + rpi_board[1] / 2 - vent[1] / 2, -box_d - 1]) cube([vent[0], vent[1], box_floor + 2]);
        for (i = [-3:3]) translate([mid_x + i * 10 - vent[0] / 2, box_y1 - box_wall - 1, -box_d + box_floor + 4]) cube([vent[0], box_wall + 2, 14]);
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
