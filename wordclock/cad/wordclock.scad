// Word clock enclosure for an IKEA SANNAHED 50x50 cm frame.
//
// All sizes are in millimetres. The model is built in "front view"
// coordinates: x to the right and y up, as seen by someone looking at the
// clock. Row 0 is the top row of the letter grid.
//
// Render a single part from the command line, for example:
//   openscad -o face.stl -D 'part="face"' -D 'tile=[0,8,0,8]' \
//            -D 'rows=["ITISA...", ...]' wordclock.scad
//
// Prefer `uv run wordclock-cad`, which renders every part and tile.

// Karla Bold Stencil (SIL OFL 1.1): every letter is a single through-hole
// with bridges, so the face prints in one piece without loose islands.
use <fonts/KarlaBoldStencil.ttf>

/* [Part selection] */
// face | grid | pibox | pilid | pihanger | assembly | none (library use)
part = "grid";
// Cell range [col_start, col_end, row_start, row_end), end exclusive
tile = [0, 8, 0, 8];

/* [Assembly view] */
// Gap between layers in the assembly view (0 = assembled)
explode = 40;
// Show the SANNAHED frame around the panel
show_frame = true;

/* [Frame] */
// Inner opening of the frame, where the panel sits
inner_size = 485;
// Total play between the panel and the frame (both sides together)
clearance = 1.0;

/* [Matrix] */
cells = 16;
// Distance between LED centres (cell size)
pitch = 30;

/* [Front face] */
// Opaque black panel with stencil letter holes
face_t = 2.4;
font = "Karla:style=Bold Stencil";
// Cap height of the letters
cap_height = 16;
// Font metrics as a ratio of the font size: capitals, accent top, descender
cap_ratio = 0.901;
accent_ratio = 1.25;
descent_ratio = 0.25;

/* [Face joints] */
// Dovetail tabs that lock neighbouring face tiles together
tab_depth = 4;
tab_neck = 5;
tab_head = 8;
// Play between a tab and its socket
joint_gap = 0.15;
// Paper diffuser between the face and the grid (assembly view only)
paper_t = 0.3;

/* [Light grid] */
wall_t = 1.2;
// Height of the walls between the back plate and the face
grid_h = 20;
back_t = 2;
// Hole for 12 mm bullet pixels. Set to 0 for a solid back plate.
led_hole_d = 12;
// M3 bolt holes that join neighbouring tiles
bolt_d = 3.4;
bolt_z = 4;

/* [Raspberry Pi box] */
// Raspberry Pi Zero 2 W: 65 x 30 mm, holes on a 58 x 23 mm rectangle
pi_size = [65, 30];
pi_holes = [58, 23];
// Inside of the box that hangs under the frame: width, depth, height
box_inner = [100, 46, 30];
box_wall = 2;
// Plate that rises behind the frame and is bolted to the back board
hanger_h = 45;
hanger_t = 3;
// Panel-mount momentary push button on the front
button_d = 12;
// Panel-mount DC jack on the left side (check it is rated for 6 A)
dc_jack_d = 8;

/* [Camera] */
// Raspberry Pi Camera Module 3: 25 x 24 mm board, M2 holes on 21 x 12.5 mm
cam_board = [25, 24];
cam_holes = [21, 12.5];
// Distance from the top edge of the board to the top holes and to the lens
cam_hole_top = 2;
cam_lens_top = 9.5;
cam_lens_d = 10;
// Gap between the inside of the front wall and the camera board
cam_standoff_h = 4;
// Height of the lens centre above the bottom of the box
cam_lens_z = 17;

/* [Letters] */
rows = [
    "ITISASCTIMEQHXQ ",
];

$fn = 48;

panel_size = inner_size - clearance;
border = (panel_size - cells * pitch) / 2;
font_size = cap_height / cap_ratio;
// Baseline below the cell centre that centres accents and descenders
baseline = -(accent_ratio - descent_ratio) * font_size / 2;

assert(border >= 0, "Matrix does not fit: reduce pitch or cells");

// Position of the line between cell k-1 and cell k (k = 0..cells).
function line_pos(k) = border + k * pitch;

// Tile edges in front-view coordinates. Outer edges include the border.
function tile_x0(t) = t[0] == 0 ? 0 : line_pos(t[0]);
function tile_x1(t) = t[1] == cells ? panel_size : line_pos(t[1]);
function tile_y1(t) = t[2] == 0 ? panel_size : panel_size - line_pos(t[2]);
function tile_y0(t) = t[3] == cells ? 0 : panel_size - line_pos(t[3]);

function cell_x(c) = line_pos(c) + pitch / 2;
function cell_y(r) = panel_size - line_pos(r) - pitch / 2;

module tile_rect(t) {
    translate([tile_x0(t), tile_y0(t)])
        square([tile_x1(t) - tile_x0(t), tile_y1(t) - tile_y0(t)]);
}

// --- Front face -----------------------------------------------------------

module letters_2d(t) {
    for (r = [t[2]:t[3] - 1], c = [t[0]:t[1] - 1]) {
        ch = rows[r][c];
        if (ch != " ")
            translate([cell_x(c), cell_y(r) + baseline])
                text(ch, size = font_size, font = font, halign = "center", valign = "baseline");
    }
}

// The tile plus one cell around it, so tabs never cover a neighbour letter.
function grown_tile(t) = [max(0, t[0] - 1), min(cells, t[1] + 1), max(0, t[2] - 1), min(cells, t[3] + 1)];

// Dovetail pointing +x from a seam at x = 0, centred on y = 0.
module dovetail(grow = 0) {
    offset(delta = grow)
        polygon([[-1, -tab_neck / 2], [tab_depth, -tab_head / 2], [tab_depth, tab_head / 2], [-1, tab_neck / 2]]);
}

// Joints sit on every other grid line along a seam, where four cell
// corners meet and there is no letter.
function joint_lines(start, end) = [for (k = [start + 2:2:end - 2]) k];

// Tabs on the right and bottom edges, sockets on the left and top edges.
module joints(t, grow, tabs) {
    if (tabs ? t[1] != cells : t[0] != 0)
        for (k = joint_lines(t[2], t[3]))
            translate([line_pos(tabs ? t[1] : t[0]), panel_size - line_pos(k)]) dovetail(grow);
    if (tabs ? t[3] != cells : t[2] != 0)
        for (k = joint_lines(t[0], t[1]))
            translate([line_pos(k), panel_size - line_pos(tabs ? t[3] : t[2])]) rotate(-90) dovetail(grow);
}

module face_2d(t) {
    difference() {
        union() {
            tile_rect(t);
            joints(t, 0, tabs = true);
        }
        joints(t, joint_gap, tabs = false);
        letters_2d(grown_tile(t));
    }
}

// Parts printed face-down are mirrored so that the text reads correctly
// once the printed tile is flipped over.
module face(t) {
    mirror([1, 0, 0]) linear_extrude(face_t) face_2d(t);
}

// --- Light grid -----------------------------------------------------------

// Walls inside one tile. Outer edges are solid up to the first cell wall.
// Edges shared with another tile get a full wall, so the seam is a double
// wall that can be bolted together.
module grid_walls_2d(t) {
    x0 = tile_x0(t);
    x1 = tile_x1(t);
    y0 = tile_y0(t);
    y1 = tile_y1(t);
    outer = border + wall_t / 2;
    left = t[0] == 0 ? outer : wall_t;
    right = t[1] == cells ? outer : wall_t;
    top = t[2] == 0 ? outer : wall_t;
    bottom = t[3] == cells ? outer : wall_t;

    translate([x0, y0]) square([left, y1 - y0]);
    translate([x1 - right, y0]) square([right, y1 - y0]);
    translate([x0, y1 - top]) square([x1 - x0, top]);
    translate([x0, y0]) square([x1 - x0, bottom]);

    for (k = [t[0] + 1:t[1] - 1])
        translate([line_pos(k) - wall_t / 2, y0]) square([wall_t, y1 - y0]);
    for (k = [t[2] + 1:t[3] - 1])
        translate([x0, panel_size - line_pos(k) - wall_t / 2]) square([x1 - x0, wall_t]);
}

// Bolt holes through the seam walls, two per shared edge.
module seam_bolts(t) {
    z = back_t + bolt_z;
    len = 2 * wall_t + 2;
    bolt_rows = [t[2] + 1, t[3] - 2];
    bolt_cols = [t[0] + 1, t[1] - 2];

    for (r = bolt_rows) {
        if (t[0] != 0)
            translate([tile_x0(t), cell_y(r), z]) rotate([0, 90, 0]) cylinder(d = bolt_d, h = len, center = true);
        if (t[1] != cells)
            translate([tile_x1(t), cell_y(r), z]) rotate([0, 90, 0]) cylinder(d = bolt_d, h = len, center = true);
    }
    for (c = bolt_cols) {
        if (t[2] != 0)
            translate([cell_x(c), tile_y1(t), z]) rotate([90, 0, 0]) cylinder(d = bolt_d, h = len, center = true);
        if (t[3] != cells)
            translate([cell_x(c), tile_y0(t), z]) rotate([90, 0, 0]) cylinder(d = bolt_d, h = len, center = true);
    }
}

// Printed back plate down, open side (towards the face) up.
module grid(t) {
    difference() {
        union() {
            linear_extrude(back_t) tile_rect(t);
            translate([0, 0, back_t]) linear_extrude(grid_h) grid_walls_2d(t);
        }
        if (led_hole_d > 0)
            for (r = [t[2]:t[3] - 1], c = [t[0]:t[1] - 1])
                translate([cell_x(c), cell_y(r), -1]) cylinder(d = led_hole_d, h = back_t + 2);
        seam_bolts(t);
    }
}

// --- Raspberry Pi box -----------------------------------------------------

// The box hangs under the bottom edge of the frame. Box coordinates: x is the
// width, y the depth (y = 0 at the back, against the wall) and z the height
// (z = 0 at the open bottom, closed by the lid). Seen from the front, x runs
// from right to left.

module rounded_box(size, r = 3) {
    linear_extrude(size[2])
        offset(r) offset(-r) square([size[0], size[1]]);
}

function box_outer() = [box_inner[0] + 2 * box_wall, box_inner[1] + 2 * box_wall, box_inner[2] + box_wall];

// Corner bosses for the M3 screws that hold the lid.
function lid_screws() = [[box_wall + 5, box_wall + box_inner[1] - 5], [box_wall + box_inner[0] - 5, box_wall + box_inner[1] - 5]];

// M3 bolts that join the hanger plate to the back wall of the box.
function hanger_box_bolts() = [[20, box_outer()[2] / 2], [box_outer()[0] - 20, box_outer()[2] / 2]];

// Camera hole positions on the front wall, as [x, z].
function cam_holes_xz() = [
    for (dx = [-cam_holes[0] / 2, cam_holes[0] / 2], dz = [0, -cam_holes[1]])
        [box_outer()[0] / 2 + dx, cam_lens_z + cam_lens_top - cam_hole_top + dz]
];

module countersunk_m3(depth) {
    translate([0, 0, -1]) cylinder(d = 3.4, h = depth + 2);
    translate([0, 0, depth - 1.6]) cylinder(d1 = 3.4, d2 = 6.6, h = 1.61);
}

// Box body, printed upside down (top on the bed) so that the camera
// standoffs grow sideways from the front wall.
module pibox_body() {
    outer = box_outer();
    front = outer[1] - box_wall;
    difference() {
        rounded_box(outer);
        translate([box_wall, box_wall, -1]) rounded_box([box_inner[0], box_inner[1], box_inner[2] + 1], 1);
        // Camera lens, centred on the front
        translate([outer[0] / 2, front - 1, cam_lens_z]) rotate([-90, 0, 0]) cylinder(d = cam_lens_d, h = box_wall + 2);
        // Push button on the front, to the right of the camera
        translate([20, front - 1, outer[2] / 2]) rotate([-90, 0, 0]) cylinder(d = button_d, h = box_wall + 2);
        // DC jack on the left side
        translate([outer[0] - box_wall - 1, outer[1] / 2 + 6, outer[2] / 2]) rotate([0, 90, 0]) cylinder(d = dc_jack_d, h = box_wall + 2);
        // Cable exit in the top, at the back, up into the frame
        translate([outer[0] / 2 - 10, box_wall, outer[2] - box_wall - 1]) cube([20, 8, box_wall + 2]);
        // Bolt holes for the hanger plate
        for (p = hanger_box_bolts())
            translate([p[0], -1, p[1]]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = box_wall + 2);
    }
    // Bosses for the lid screws (M3 self-tapping)
    for (p = lid_screws())
        translate([p[0], p[1], 0])
            difference() {
                cylinder(d = 7, h = outer[2] - box_wall);
                translate([0, 0, -1]) cylinder(d = 2.6, h = 15);
            }
    // Standoffs for the camera board (M2 self-tapping)
    for (p = cam_holes_xz())
        translate([p[0], front - cam_standoff_h, p[1]]) rotate([-90, 0, 0])
            difference() {
                cylinder(d = 4.5, h = cam_standoff_h);
                translate([0, 0, -1]) cylinder(d = 1.8, h = cam_standoff_h + 2);
            }
}

// Bottom lid that carries the Raspberry Pi. Printed flat, outside face down.
module pibox_lid() {
    outer = box_outer();
    tol = 0.3;
    lip = 3;
    standoff_h = 4;
    pi_origin = [box_wall + box_inner[0] - pi_size[0] - 4, box_wall + 3];

    difference() {
        rounded_box([outer[0], outer[1], box_wall]);
        // Ventilation slots under the Raspberry Pi
        for (i = [0:3])
            translate([pi_origin[0] + 8, pi_origin[1] + 6 + i * 6, -1]) cube([pi_size[0] - 16, 2.5, box_wall + 2]);
        for (p = lid_screws())
            translate([p[0], p[1], 0]) mirror([0, 0, 1]) translate([0, 0, -box_wall]) countersunk_m3(box_wall);
    }
    // Lip that keeps the lid centred in the box, cut around the bosses
    translate([0, 0, box_wall])
        difference() {
            translate([box_wall + tol, box_wall + tol]) rounded_box([box_inner[0] - 2 * tol, box_inner[1] - 2 * tol, lip], 1);
            translate([box_wall + tol + 1.2, box_wall + tol + 1.2, -1]) rounded_box([box_inner[0] - 2 * tol - 2.4, box_inner[1] - 2 * tol - 2.4, lip + 2], 1);
            for (p = lid_screws()) translate([p[0], p[1], -1]) cylinder(d = 8, h = lip + 2);
        }
    // Standoffs for M2.5 self-tapping screws
    for (dx = [0, pi_holes[0]], dy = [0, pi_holes[1]])
        translate([pi_origin[0] + 3.5 + dx, pi_origin[1] + 3.5 + dy, box_wall])
            difference() {
                cylinder(d = 5.5, h = standoff_h);
                cylinder(d = 2.2, h = standoff_h + 1);
            }
}

// Plate behind the box that rises behind the frame. The lower holes bolt it
// to the box, the upper holes to the frame back board. All holes are
// countersunk on the wall side (y < 0).
module pibox_hanger() {
    outer = box_outer();
    translate([0, -hanger_t, 0])
        difference() {
            cube([outer[0], hanger_t, outer[2] + hanger_h]);
            for (p = concat(hanger_box_bolts(), [[15, outer[2] + hanger_h - 12], [outer[0] - 15, outer[2] + hanger_h - 12]]))
                translate([p[0], 0, p[1]]) rotate([-90, 0, 0]) countersunk_m3_from_back(hanger_t);
        }
}

// Countersunk M3 hole along +z with the countersink at z = 0.
module countersunk_m3_from_back(depth) {
    translate([0, 0, depth]) mirror([0, 0, 1]) countersunk_m3(depth);
}

module pibox() {
    translate([0, box_outer()[1], box_outer()[2]]) rotate([180, 0, 0]) pibox_body();
}

module pilid() {
    pibox_lid();
}

// Printed flat on the bed.
module pihanger() {
    rotate([90, 0, 0]) translate([0, hanger_t, 0]) pibox_hanger();
}

// --- Assembly view ----------------------------------------------------------

// Whole clock seen from the front (+z), with the layers pulled apart by
// `explode`. For viewing only: use the individual parts for printing.
module assembly() {
    tiles = [[0, 8, 0, 8], [8, 16, 0, 8], [0, 8, 8, 16], [8, 16, 8, 16]];
    grid_top = back_t + grid_h;
    paper_z = grid_top + explode / 2;
    face_z = grid_top + explode;

    color("ivory") translate([0, 0, paper_z]) cube([panel_size, panel_size, paper_t]);
    for (t = tiles) {
        color("white") grid(t);
        color("#1a1a1a") translate([0, 0, face_z]) linear_extrude(face_t) face_2d(t);
    }
    // Back board of the frame, behind the pixel tails
    back_z = -18;
    frame_wall = (500 - inner_size) / 2;
    frame_bottom = -clearance / 2 - frame_wall;
    // Box coordinates (x, depth, height) to front view (-x, height, depth)
    translate([panel_size / 2 + box_outer()[0] / 2, frame_bottom - box_outer()[2], back_z])
        multmatrix([[-1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]) {
            color("dimgray") pibox_body();
            color("gray") translate([0, 0, -explode / 2]) pibox_lid();
            color("gray") translate([0, -explode / 2, 0]) pibox_hanger();
        }
    if (show_frame) {
        color("burlywood", 0.35)
            translate([-clearance / 2 - frame_wall, -clearance / 2 - frame_wall, back_z])
                difference() {
                    cube([500, 500, 60]);
                    translate([frame_wall, frame_wall, -1]) cube([inner_size, inner_size, 62]);
                }
    }
}

// --- Part selector ----------------------------------------------------------

if (part == "face") face(tile);
else if (part == "grid") grid(tile);
else if (part == "pibox") pibox();
else if (part == "pilid") pilid();
else if (part == "pihanger") pihanger();
else if (part == "assembly") assembly();
else if (part != "none") assert(false, str("Unknown part: ", part));
