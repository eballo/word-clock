// Word clock enclosure for an IKEA SANNAHED 50x50 cm frame.
//
// All sizes are in millimetres. The model is built in "front view"
// coordinates: x to the right and y up, as seen by someone looking at the
// clock. Row 0 is the top row of the letter grid.
//
// The LEDs are a WS2812B strip with 144 LEDs/metre. Every cell sits over 4
// LEDs, so the cell pitch is 4 x 6.94 = 27.78 mm. The strips lie on the back
// plate of the light grid and pass under the walls through small notches.
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
// face | grid | camholder | pitray | assembly | none (library use)
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
// Space between the back of the grid and the frame back board, for the
// Raspberry Pi and the wiring
back_gap = 10;

/* [Matrix] */
cells = 16;
// WS2812B strip, 144 LEDs/metre
led_pitch = 1000 / 144;
leds_per_cell = 4;
// Extra margin below the matrix (taken from the top) for the hidden camera
bottom_extra = 16;

/* [Front face] */
// Opaque black panel with stencil letter holes
face_t = 2.4;
font = "Karla:style=Bold Stencil";
// Cap height of the letters
cap_height = 15;
// Font metrics as a ratio of the font size: capitals, accent top, descender
cap_ratio = 0.901;
accent_ratio = 1.25;
descent_ratio = 0.25;

/* [Joints] */
// Dovetail tabs that lock neighbouring tiles together (face and grid)
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
grid_h = 25;
back_t = 2;
// Notch at the bottom of every wall the strip passes under
strip_w = 12;
strip_notch_h = 3;
// Ribs in the hollow border, with a notch at the back for the wiring
rib_notch_h = 8;

/* [Camera] */
// Raspberry Pi Camera Module 3: 25 x 24 mm board, M2 holes on 21 x 12.5 mm
cam_board = [25, 24];
cam_holes = [21, 12.5];
// Distance from the top edge of the board to the top holes and to the lens
cam_hole_top = 2;
cam_lens_top = 9.5;
cam_lens_d = 10;
// Height of the lens housing above the front of the board
cam_lens_h = 6.5;
// Hole in the face in front of the lens
cam_hole_d = 6;
holder_t = 1.5;

/* [Raspberry Pi tray] */
// Raspberry Pi Zero 2 W: 65 x 30 mm, holes on a 58 x 23 mm rectangle
pi_size = [65, 30];
pi_holes = [58, 23];
tray_size = [110, 42];
tray_t = 2;
pi_standoff_h = 3;

/* [Letters] */
rows = [
    "ITISASCTIMEQHXQ ",
];

$fn = 48;

panel_size = inner_size - clearance;
pitch = led_pitch * leds_per_cell;
matrix_size = cells * pitch;
border_x = (panel_size - matrix_size) / 2;
border_top = border_x - bottom_extra / 2;
border_bottom = border_x + bottom_extra / 2;
font_size = cap_height / cap_ratio;
// Baseline below the cell centre that centres accents and descenders
baseline = -(accent_ratio - descent_ratio) * font_size / 2;

assert(border_top >= 2 * wall_t, "Matrix does not fit: reduce cells or bottom_extra");

// Position of grid line k (k = 0..cells), the line between cell k-1 and k.
function line_x(k) = border_x + k * pitch;
function line_y(k) = panel_size - border_top - k * pitch;

// Tile edges in front-view coordinates. Outer edges include the border.
function tile_x0(t) = t[0] == 0 ? 0 : line_x(t[0]);
function tile_x1(t) = t[1] == cells ? panel_size : line_x(t[1]);
function tile_y1(t) = t[2] == 0 ? panel_size : line_y(t[2]);
function tile_y0(t) = t[3] == cells ? 0 : line_y(t[3]);

function cell_x(c) = line_x(c) + pitch / 2;
function cell_y(r) = line_y(r) - pitch / 2;

// Camera, centred in the bottom margin, board top edge against the matrix.
cam_x = panel_size / 2;
cam_board_top = line_y(cells) - wall_t / 2 - 0.5;
cam_lens_y = cam_board_top - cam_lens_top;
// Area of the bottom border kept free of ribs and walls for the camera
cam_zone = cam_board[0] + 10;

module tile_rect(t) {
    translate([tile_x0(t), tile_y0(t)])
        square([tile_x1(t) - tile_x0(t), tile_y1(t) - tile_y0(t)]);
}

// --- Joints -----------------------------------------------------------------

// Dovetail pointing +x from a seam at x = 0, centred on y = 0.
module dovetail(grow = 0) {
    offset(delta = grow)
        polygon([[-1, -tab_neck / 2], [tab_depth, -tab_head / 2], [tab_depth, tab_head / 2], [-1, tab_neck / 2]]);
}

// Joints sit on every other grid line along a seam, where four cell
// corners meet and there is no letter and no strip.
function joint_lines(start, end) = [for (k = [start + 2:2:end - 2]) k];

// Tabs on the right and bottom edges, sockets on the left and top edges.
module joints(t, grow, tabs) {
    if (tabs ? t[1] != cells : t[0] != 0)
        for (k = joint_lines(t[2], t[3]))
            translate([line_x(tabs ? t[1] : t[0]), line_y(k)]) dovetail(grow);
    if (tabs ? t[3] != cells : t[2] != 0)
        for (k = joint_lines(t[0], t[1]))
            translate([line_x(k), line_y(tabs ? t[3] : t[2])]) rotate(-90) dovetail(grow);
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

module face_2d(t) {
    difference() {
        union() {
            tile_rect(t);
            joints(t, 0, tabs = true);
        }
        joints(t, joint_gap, tabs = false);
        letters_2d(grown_tile(t));
        translate([cam_x, cam_lens_y]) circle(d = cam_hole_d);
    }
}

// Parts printed face-down are mirrored so that the text reads correctly
// once the printed tile is flipped over.
module face(t) {
    mirror([1, 0, 0]) linear_extrude(face_t) face_2d(t);
}

// --- Light grid -----------------------------------------------------------

// Cell area of a tile, extended over the outer cell walls.
function cells_x0(t) = t[0] == 0 ? line_x(0) - wall_t / 2 : tile_x0(t);
function cells_x1(t) = t[1] == cells ? line_x(cells) + wall_t / 2 : tile_x1(t);
function cells_y0(t) = t[3] == cells ? line_y(cells) - wall_t / 2 : tile_y0(t);
function cells_y1(t) = t[2] == 0 ? line_y(0) + wall_t / 2 : tile_y1(t);

// Wall on grid line k from y0 to y1 (or x0 to x1). Seam walls stay inside
// their tile, so a seam is a double wall.
module vwall(t, k, y0, y1) {
    x = k == t[0] && t[0] != 0 ? line_x(k)
        : k == t[1] && t[1] != cells ? line_x(k) - wall_t
        : line_x(k) - wall_t / 2;
    translate([x, y0]) square([wall_t, y1 - y0]);
}

module hwall(t, k, x0, x1) {
    y = k == t[2] && t[2] != 0 ? line_y(k) - wall_t
        : k == t[3] && t[3] != cells ? line_y(k)
        : line_y(k) - wall_t / 2;
    translate([x0, y]) square([x1 - x0, wall_t]);
}

// Walls around and between the cells.
module cell_walls_2d(t) {
    for (k = [t[0]:t[1]]) vwall(t, k, cells_y0(t), cells_y1(t));
    for (k = [t[2]:t[3]]) hwall(t, k, cells_x0(t), cells_x1(t));
}

function in_cam_zone(x) = abs(x - cam_x) < cam_zone / 2;

// Perimeter wall, plus seam walls through the border. The bottom border
// keeps the camera zone free.
module border_walls_2d(t) {
    x0 = tile_x0(t);
    x1 = tile_x1(t);
    y0 = tile_y0(t);
    y1 = tile_y1(t);
    if (t[0] == 0) translate([x0, y0]) square([wall_t, y1 - y0]);
    if (t[1] == cells) translate([x1 - wall_t, y0]) square([wall_t, y1 - y0]);
    if (t[2] == 0) translate([x0, y1 - wall_t]) square([x1 - x0, wall_t]);
    if (t[3] == cells) translate([x0, y0]) square([x1 - x0, wall_t]);

    seams_x = [for (k = [t[0], t[1]]) if (k != 0 && k != cells) k];
    seams_y = [for (k = [t[2], t[3]]) if (k != 0 && k != cells) k];
    if (t[2] == 0) for (k = seams_x) vwall(t, k, cells_y1(t), y1);
    if (t[3] == cells) for (k = seams_x) if (!in_cam_zone(line_x(k))) vwall(t, k, y0, cells_y0(t));
    if (t[0] == 0) for (k = seams_y) hwall(t, k, x0, cells_x0(t));
    if (t[1] == cells) for (k = seams_y) hwall(t, k, cells_x1(t), x1);
}

// Rib of the given footprint, with a notch at the back for the wiring.
module rib(size, along_x) {
    difference() {
        cube([size[0], size[1], back_t + grid_h]);
        if (along_x) translate([2, -1, -1]) cube([size[0] - 4, size[1] + 2, rib_notch_h + 1]);
        else translate([-1, 2, -1]) cube([size[0] + 2, size[1] - 4, rib_notch_h + 1]);
    }
}

// Ribs on every other grid line join the perimeter to the cells.
module ribs(t) {
    rows_k = [for (k = [t[2] + 1:t[3] - 1]) if (k % 2 == 0) k];
    cols_k = [for (k = [t[0] + 1:t[1] - 1]) if (k % 2 == 0) k];
    if (t[0] == 0)
        for (k = rows_k) translate([0, line_y(k) - wall_t / 2, 0]) rib([cells_x0(t), wall_t], true);
    if (t[1] == cells)
        for (k = rows_k) translate([cells_x1(t), line_y(k) - wall_t / 2, 0]) rib([panel_size - cells_x1(t), wall_t], true);
    if (t[2] == 0)
        for (k = cols_k) translate([line_x(k) - wall_t / 2, cells_y1(t), 0]) rib([wall_t, panel_size - cells_y1(t)], false);
    if (t[3] == cells)
        for (k = cols_k) if (!in_cam_zone(line_x(k))) translate([line_x(k) - wall_t / 2, 0, 0]) rib([wall_t, cells_y0(t)], false);
}

// Notches where the strips pass under the vertical walls.
module strip_notches(t) {
    for (k = [t[0]:t[1]], r = [t[2]:t[3] - 1])
        translate([line_x(k) - 3, cell_y(r) - strip_w / 2, back_t - 0.01]) cube([6, strip_w, strip_notch_h]);
}

// Printed back plate down, open side (towards the face) up. The border is
// open at the back, so the wiring can reach the strip ends and the camera.
module grid(t) {
    difference() {
        union() {
            linear_extrude(back_t) {
                translate([cells_x0(t), cells_y0(t)]) square([cells_x1(t) - cells_x0(t), cells_y1(t) - cells_y0(t)]);
                joints(t, 0, tabs = true);
            }
            linear_extrude(back_t + grid_h) {
                cell_walls_2d(t);
                border_walls_2d(t);
            }
            ribs(t);
        }
        strip_notches(t);
        // Sockets go through the plate and the bottom of the walls above them
        translate([0, 0, -1]) linear_extrude(back_t + 1.2) joints(t, joint_gap, tabs = false);
    }
}

// --- Camera holder ------------------------------------------------------------

// Plate glued to the back of the face, centred on the pinhole. The camera
// board screws onto the standoffs with the lens through the plate.
// Holder coordinates: the lens is at the origin, the face side is z = 0 and
// the standoffs point to +z.
module camholder() {
    w = cam_board[0] + 6;
    h = cam_board[1];
    standoff = cam_lens_h - holder_t;
    holes = [
        for (dx = [-cam_holes[0] / 2, cam_holes[0] / 2], dy = [0, -cam_holes[1]])
            [dx, cam_lens_top - cam_hole_top + dy]
    ];
    difference() {
        union() {
            translate([-w / 2, cam_lens_top - h, 0]) cube([w, h, holder_t]);
            for (p = holes) translate([p[0], p[1], 0]) cylinder(d = 4.5, h = holder_t + standoff);
        }
        translate([0, 0, -1]) cylinder(d = cam_lens_d, h = holder_t + 2);
        for (p = holes) translate([p[0], p[1], -1]) cylinder(d = 1.8, h = holder_t + standoff + 2);
    }
}

// --- Raspberry Pi tray --------------------------------------------------------

// Tray bolted to the frame back board, behind the grid. The Pi faces the
// grid; the free area on the right holds the 74AHCT125 board.
module pitray() {
    pi_origin = [4, (tray_size[1] - pi_size[1]) / 2];
    difference() {
        linear_extrude(tray_t) offset(3) offset(-3) square(tray_size);
        // Countersunk holes for M3 bolts through the back board
        for (x = [tray_size[0] - 8, tray_size[0] - 30], y = [8, tray_size[1] - 8])
            translate([x, y, -1]) {
                cylinder(d = 3.4, h = tray_t + 2);
                translate([0, 0, tray_t + 1 - 1.6]) cylinder(d1 = 3.4, d2 = 6.6, h = 1.61);
            }
        // Zip-tie slots for the cables
        for (y = [tray_size[1] / 2 - 8, tray_size[1] / 2 + 5])
            translate([tray_size[0] - 22, y, -1]) cube([4, 3, tray_t + 2]);
    }
    for (dx = [0, pi_holes[0]], dy = [0, pi_holes[1]])
        translate([pi_origin[0] + 3.5 + dx, pi_origin[1] + 3.5 + dy, tray_t])
            difference() {
                cylinder(d = 5.5, h = pi_standoff_h);
                cylinder(d = 2.2, h = pi_standoff_h + 1);
            }
}

// --- Assembly view ----------------------------------------------------------

// Whole clock seen from the front (+z), with the layers pulled apart by
// `explode`. For viewing only: use the individual parts for printing.
module assembly() {
    tiles = [[0, 8, 0, 8], [8, 16, 0, 8], [0, 8, 8, 16], [8, 16, 8, 16]];
    grid_top = back_t + grid_h;
    paper_z = grid_top + explode / 2;
    face_z = grid_top + explode;

    for (t = tiles) {
        color("white") grid(t);
        color("#1a1a1a") translate([0, 0, face_z]) linear_extrude(face_t) face_2d(t);
    }
    // LED strips, one per row
    for (r = [0:cells - 1])
        color("seagreen") translate([line_x(0), cell_y(r) - 5, back_t]) cube([matrix_size, 10, 1.5]);
    color("ivory") translate([line_x(0), line_y(cells), paper_z]) cube([matrix_size, matrix_size, paper_t]);
    color("dimgray") translate([cam_x, cam_lens_y, face_z]) mirror([0, 0, 1]) camholder();
    color("gray") translate([cam_x - tray_size[0] / 2, line_y(cells) + 20, -back_gap - explode / 2]) pitray();

    if (show_frame) {
        frame_wall = (500 - inner_size) / 2;
        color("burlywood", 0.35)
            translate([-clearance / 2 - frame_wall, -clearance / 2 - frame_wall, -back_gap])
                difference() {
                    cube([500, 500, 50]);
                    translate([frame_wall, frame_wall, -1]) cube([inner_size, inner_size, 52]);
                }
    }
}

// --- Part selector ----------------------------------------------------------

if (part == "face") face(tile);
else if (part == "grid") grid(tile);
else if (part == "camholder") camholder();
else if (part == "pitray") pitray();
else if (part == "assembly") assembly();
else if (part != "none") assert(false, str("Unknown part: ", part));
