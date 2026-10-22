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
// Prefer `uv run wordclock-cad --matrix`, which renders every part.

/* [Part selection] */
// grid | face | assembly | none (library use)
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

// --- Assembly ---------------------------------------------------------------

module assembly() {
    for (h = [0, 1]) {
        color("white") grid(h);
        top = back_t + grid_h;
        color("ivory", 0.6) translate([0, 0, top + explode / 2]) cube([panel_w, panel_h, paper_t]);
        // The face body has its front at z = 0: flip it onto the grid.
        color("#222") translate([0, 0, top + paper_t + face_t + explode]) mirror([0, 0, 1]) face_body(h);
    }
}

if (part == "grid") grid(half);
else if (part == "face") face(half);
else if (part == "assembly") assembly();
