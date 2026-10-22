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
// face | grid | spacer | recess | screenfront | screenback | screenhanger | pitray | assembly | pieces |
// none (library use)
part = "grid";
// Cell range [col_start, col_end, row_start, row_end), end exclusive
tile = [0, 5, 0, 5];
// Grid lines where the panel is split into tiles (same for rows and columns).
// 3 x 3 tiles keep every part under 17.5 cm for a 25 cm printer bed.
splits = [0, 5, 11, 16];

/* [Assembly view] */
// Show the optional spacer and recess rings that can hold the panel in the
// frame
show_rings = false;
// Gap between layers in the assembly view (0 = assembled)
explode = 0;
// Show the SANNAHED frame around the panel
show_frame = true;

/* [Frame] */
// Inside of the frame where the panel sits (49 x 49 cm: the 50 x 50 cm back
// board sits behind a 5 mm inner border)
inner_size = 490;
// Total play between the panel and the frame (both sides together)
clearance = 1.0;
// Inside depth of the frame with its back board in place, from the back
// board to the front lip
frame_depth = 45;
// How far the face sits behind the front lip. A black ring of this depth
// fills the gap between the lip and the face margins.
recess = 5;
// Width of that ring, from the panel edge inwards (less than the margin)
recess_w = 8;
// The frame's plastic front sheet, behind the front lip (0 = not used)
front_sheet_t = 0;

/* [Matrix] */
cells = 16;
// WS2812B strip, 144 LEDs/metre
led_pitch = 1000 / 144;
leds_per_cell = 4;
// Extra margin below the matrix, taken from the top. Set it to 16 when the
// camera hides in the clock (clock_camera = true).
bottom_extra = 0;

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

/* [Spacer] */
// Ring between the grid and the frame back board. It leaves room for the
// wiring and keeps the whole stack pressed against the front lip.
spacer_w = 25;
// Play so the back board still closes
spacer_fit = 0.2;
// Cable grooves across the ring, on the grid side
spacer_groove = [14, 5];

/* [Magnets] */
// Neodymium disc magnets that hold the face on the grid, in the margins of
// the outer tiles: one on the back of the face, one on a post of the grid.
magnets = true;
magnet_d = 5;
magnet_h = 2;
// Extra diameter of the pocket, for a press fit
magnet_fit = 0.2;
// Boss on the back of the face that keeps the magnet hidden from the front
magnet_boss_h = 2;
magnet_post_d = 9;

/* [Light grid] */
wall_t = 1.2;
// M3 bolts through the seam walls, in the cell corners, above the strip
bolt_d = 3.4;
bolt_z = 9;
// Distance from the grid line, along the seam
bolt_offset = 5;
// Height of the walls between the back plate and the face
grid_h = 25;
back_t = 2;
// Notch at the bottom of every wall the strip passes under
strip_w = 14;
strip_notch_h = 3;
// Ribs in the hollow border, with a notch at the back for the wiring
rib_notch_h = 8;

/* [Camera] */
// Camera behind a pinhole in the clock face (true) or in the screen module
// under the clock (false)
clock_camera = false;
// Camera board: 25 x 24 mm, M2 holes on 21 x 12.5 mm (Camera Module 1.3,
// 2 and 3, and most OV5647 boards)
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
// Bracket in the grid that holds the camera behind the pinhole
holder_t = 1.5;
cam_standoff_h = 4;

/* [Screen module] */
// Raspberry Pi Touch Display v1 (2015), from the official mechanical drawing
lcd_glass = [192.96, 110.76];
lcd_t = 6;
// LCD active area and its distance from the top edge of the glass
lcd_area = [154.08, 85.92];
lcd_area_top = 11.41;
// Metal back frame and its offset from the bottom-left corner of the glass
lcd_frame = [164.9, 100.6];
lcd_frame_pos = [12.54, 3.53];
// M3 mounting holes on the back frame, from its bottom-left corner
lcd_m3 = [[20, 20], [146.2, 20], [20, 85.65], [146.2, 85.65]];
// Play around the glass
lcd_fit = 0.4;
screen_wall = 3;
screen_bezel = 2;
// Space above the glass for the camera and below it for the screws
screen_top_zone = 28;
screen_bottom_zone = 10;
// Depth behind the bezel: display, Raspberry Pi 4B on its standoffs, cables
screen_depth = 38;
screen_back_t = 4;
// Hole in the bezel in front of the camera lens
screen_cam_hole_d = 8;
// Panel-mount push button on the right side
screen_button_d = 12;
// The module hooks on two studs through the keyholes of its back cover, so it
// lifts off without tools. true: the studs are on a hanger plate bolted
// through the frame back board (one wall hook for everything). false: the
// studs are two screws in the wall.
screen_hang = true;
// Gap between the bottom edge of the frame and the top of the module
screen_gap = 15;
// Height and width of the hanger above the module, behind the frame
screen_tab = 70;
screen_tab_w = 140;
screen_hanger_t = 5;
// Keyholes: the module drops this far onto the studs
keyhole_drop = 10;
// Hole in the back cover bosses: 4.0 for M3 heat-set inserts, 2.6 for
// self-tapping screws. Inserts survive opening the module many times.
screen_insert_d = 4.0;

/* [Raspberry Pi Zero tray (optional)] */
// Only for a build without the screen module: a Raspberry Pi Zero 2 W behind
// the grid. 65 x 30 mm board, holes on a 58 x 23 mm rectangle.
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
// Space between the back of the grid and the frame back board, for the
// wiring and the spacer
back_gap = frame_depth - front_sheet_t - recess - face_t - paper_t - back_t - grid_h;
assert(recess == 0 || recess_w < border_x - 2, "recess_w must leave the letters clear");
assert(back_gap >= 8, "Not enough depth behind the grid for the wiring: lower grid_h");
pitch = led_pitch * leds_per_cell;
matrix_size = cells * pitch;
border_x = (panel_size - matrix_size) / 2;
border_top = border_x - bottom_extra / 2;
border_bottom = border_x + bottom_extra / 2;
font_size = cap_height / cap_ratio;
// Baseline below the cell centre that centres accents and descenders
baseline = -(accent_ratio - descent_ratio) * font_size / 2;

assert(border_top >= 2 * wall_t, "Matrix does not fit: reduce cells or bottom_extra");
assert(!clock_camera || border_bottom >= cam_board[1] + 3, "clock_camera needs bottom_extra = 16");

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
        if (clock_camera) translate([cam_x, cam_lens_y]) circle(d = cam_hole_d);
    }
}

// Middle cell of a tile range, for magnets that keep clear of the ribs.
function mid_cell(a, b) = floor((a + b - 1) / 2);

// Magnet positions in the margins along the outer edges of a tile.
function magnet_positions(t) = !magnets ? [] : concat(
    t[2] == 0 ? [[cell_x(mid_cell(t[0], t[1])), panel_size - border_top / 2]] : [],
    t[3] == cells && !in_cam_zone(cell_x(mid_cell(t[0], t[1])))
        ? [[cell_x(mid_cell(t[0], t[1])), border_bottom / 2]] : [],
    t[0] == 0 ? [[border_x / 2, cell_y(mid_cell(t[2], t[3]))]] : [],
    t[1] == cells ? [[panel_size - border_x / 2, cell_y(mid_cell(t[2], t[3]))]] : []
);

module magnet_pocket(top) {
    translate([0, 0, top - magnet_h - 0.1]) cylinder(d = magnet_d + magnet_fit, h = magnet_h + 1);
}

// Face in body coordinates (front at z = 0), with the magnet bosses on its
// back.
module face_body(t) {
    difference() {
        union() {
            linear_extrude(face_t) face_2d(t);
            for (p = magnet_positions(t))
                translate([p[0], p[1], face_t]) cylinder(d = magnet_post_d, h = magnet_boss_h);
        }
        for (p = magnet_positions(t))
            translate([p[0], p[1], 0]) magnet_pocket(face_t + magnet_boss_h);
    }
}

// Parts printed face-down are mirrored so that the text reads correctly
// once the printed tile is flipped over.
module face(t) {
    mirror([1, 0, 0]) face_body(t);
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

function in_cam_zone(x) = clock_camera && abs(x - cam_x) < cam_zone / 2;

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
module rib(size, along_x, h = back_t + grid_h) {
    difference() {
        cube([size[0], size[1], h]);
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

// Two M3 bolts per seam segment, next to the first and last grid line,
// clear of the strip and away from the letters.
function bolt_lines(start, end) = [start + 1, end - 1];

module seam_bolts(t) {
    z = back_t + bolt_z;
    len = 2 * wall_t + 2;
    for (seam = [t[0], t[1]]) if (seam != 0 && seam != cells)
        for (k = bolt_lines(t[2], t[3]))
            translate([line_x(seam), line_y(k) - bolt_offset, z]) rotate([0, 90, 0]) cylinder(d = bolt_d, h = len, center = true);
    for (seam = [t[2], t[3]]) if (seam != 0 && seam != cells)
        for (k = bolt_lines(t[0], t[1]))
            translate([line_x(k) + bolt_offset, line_y(seam), z]) rotate([90, 0, 0]) cylinder(d = bolt_d, h = len, center = true);
}

// Ribs through the magnet posts, from the perimeter wall to the cells, so
// the posts are part of the grid. As low as the posts, to clear the face
// bosses.
module magnet_ribs(t) {
    h = back_t + grid_h - magnet_boss_h;
    for (p = magnet_positions(t)) {
        if (p[1] > line_y(0))
            translate([p[0] - wall_t / 2, cells_y1(t), 0]) rib([wall_t, panel_size - cells_y1(t)], false, h);
        else if (p[1] < line_y(cells))
            translate([p[0] - wall_t / 2, 0, 0]) rib([wall_t, cells_y0(t)], false, h);
        else if (p[0] < line_x(0))
            translate([0, p[1] - wall_t / 2, 0]) rib([cells_x0(t), wall_t], true, h);
        else
            translate([cells_x1(t), p[1] - wall_t / 2, 0]) rib([panel_size - cells_x1(t), wall_t], true, h);
    }
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
            cam_bracket(t);
            // Magnet posts, their tops leave room for the face bosses
            for (p = magnet_positions(t))
                translate([p[0], p[1], 0]) cylinder(d = magnet_post_d, h = back_t + grid_h - magnet_boss_h);
            magnet_ribs(t);
        }
        for (p = magnet_positions(t))
            translate([p[0], p[1], 0]) magnet_pocket(back_t + grid_h - magnet_boss_h);
        strip_notches(t);
        seam_bolts(t);
        // Sockets go through the plate and the bottom of the walls above them
        translate([0, 0, -1]) linear_extrude(back_t + 1.2) joints(t, joint_gap, tabs = false);
    }
}

// --- Spacer ---------------------------------------------------------------

// One quarter of the spacer ring: an L along two edges of the panel, from a
// corner to the middle of each edge. Four identical pieces make the ring;
// each one's tab locks into the next one's socket.
// One quarter of a ring of width w along the panel edges. The dovetail
// shrinks with narrow rings so it never cuts through the arm.
module ring_quarter_2d(w) {
    c = panel_size / 2;
    k = min(1, w / (2 * tab_head));
    difference() {
        union() {
            square([c, w]);
            square([w, c]);
            translate([c, w / 2]) scale(k) dovetail(0);
        }
        translate([w / 2, c]) rotate(-90) offset(delta = joint_gap) scale(k) dovetail(0);
    }
}

module spacer_2d() {
    ring_quarter_2d(spacer_w);
}

// Printed flat, back board side down, cable grooves on top.
module spacer() {
    h = back_gap - spacer_fit;
    c = panel_size / 2;
    difference() {
        linear_extrude(h) spacer_2d();
        for (pos = [c / 3, 2 * c / 3]) {
            translate([pos - spacer_groove[0] / 2, -1, h - spacer_groove[1]]) cube([spacer_groove[0], spacer_w + 2, spacer_groove[1] + 1]);
            translate([-1, pos - spacer_groove[0] / 2, h - spacer_groove[1]]) cube([spacer_w + 2, spacer_groove[0], spacer_groove[1] + 1]);
        }
    }
}

// The four pieces around the panel, behind the grid (assembly view).
module spacer_ring() {
    c = panel_size / 2;
    for (a = [0, 90, 180, 270])
        translate([c, c, -back_gap]) rotate(a) translate([-c, -c, 0]) spacer();
}

// One quarter of the black recess ring between the front lip and the face.
// Printed flat; print it four times, in black.
module recess_piece() {
    linear_extrude(recess - spacer_fit) ring_quarter_2d(recess_w);
}

// The four pieces in front of the face (assembly view).
module recess_ring(z) {
    c = panel_size / 2;
    for (a = [0, 90, 180, 270])
        translate([c, c, z]) rotate(a) translate([-c, -c, 0]) recess_piece();
}

// --- Camera bracket ---------------------------------------------------------

// The camera belongs to the grid, not to the face, so the face can be
// swapped without touching it. The bracket sits in the bottom margin of the
// grid tile under the pinhole: two side walls and a plate (printed as a
// bridge) with standoffs pointing to the face. The camera board screws on
// with the lens facing the face, just behind the pinhole.
function cam_bracket_w() = cam_board[0] + 6;

module cam_bracket(t) {
    w = cam_bracket_w();
    y0 = wall_t;
    y1 = line_y(cells) - wall_t / 2;
    lens_top = back_t + grid_h - 0.5;
    board_back = lens_top - cam_lens_h - 1;
    plate_top = board_back - cam_standoff_h;
    holes = [
        for (dx = [-cam_holes[0] / 2, cam_holes[0] / 2], dy = [0, -cam_holes[1]])
            [cam_x + dx, cam_lens_y + cam_lens_top - cam_hole_top + dy]
    ];
    if (clock_camera && t[3] == cells && cam_x > tile_x0(t) + w && cam_x < tile_x1(t) - w) {
        // Side walls
        for (x = [cam_x - w / 2 - wall_t, cam_x + w / 2])
            translate([x, y0, 0]) cube([wall_t, y1 - y0, back_t + grid_h]);
        difference() {
            translate([cam_x - w / 2, y0, plate_top - holder_t]) cube([w, y1 - y0, holder_t]);
            // Slot for the camera ribbon cable, at the bottom edge of the board
            translate([cam_x - 9, y0 - 1, plate_top - holder_t - 1]) cube([18, 6, holder_t + 2]);
        }
        for (p = holes)
            translate([p[0], p[1], plate_top])
                difference() {
                    cylinder(d = 4.5, h = cam_standoff_h);
                    translate([0, 0, -1]) cylinder(d = 1.8, h = cam_standoff_h + 2);
                }
    }
}

// --- Screen module ----------------------------------------------------------

// A case under the clock for the Raspberry Pi Touch Display v1, the
// Raspberry Pi 4B screwed to the back of the display, and the camera above
// the screen. Body coordinates: x and y as seen from the front, z the depth
// behind the front face (0 = front, growing towards the wall). Seen from the
// front this is a mirror image, so every printed part is mirrored back.
function screen_outer() = [
    lcd_glass[0] + 2 * (lcd_fit + screen_wall),
    lcd_glass[1] + 2 * (lcd_fit + screen_wall) + screen_top_zone + screen_bottom_zone,
];
function screen_total_depth() = screen_bezel + screen_depth + screen_back_t;
// Bottom-left corner of the glass
function glass_origin() = [screen_wall + lcd_fit, screen_wall + lcd_fit + screen_bottom_zone];
function screen_cam_pos() = [
    screen_outer()[0] / 2,
    glass_origin()[1] + lcd_glass[1] + lcd_fit + screen_top_zone / 2 + 2,
];
// Back cover screws, in the corners of the top and bottom zones
function screen_screws() = let(o = screen_outer(), m = screen_wall + 4) [
    [m, m], [o[0] - m, m], [m, o[1] - m], [o[0] - m, o[1] - m],
];
function lcd_m3_pos() = [
    for (h = lcd_m3) glass_origin() + lcd_frame_pos + h
];

module screen_outline(o) {
    offset(4) offset(-4) square(o);
}

module screen_front_body() {
    o = screen_outer();
    g = glass_origin();
    d = screen_bezel + screen_depth;
    cam = screen_cam_pos();
    area_pos = [g[0] + (lcd_glass[0] - lcd_area[0]) / 2, g[1] + lcd_glass[1] - lcd_area_top - lcd_area[1]];
    cam_holes_pos = [
        for (dx = [-cam_holes[0] / 2, cam_holes[0] / 2], dy = [0, -cam_holes[1]])
            [cam[0] + dx, cam[1] + cam_lens_top - cam_hole_top + dy]
    ];
    difference() {
        union() {
            difference() {
                linear_extrude(d) screen_outline(o);
                translate([screen_wall, screen_wall, screen_bezel])
                    cube([o[0] - 2 * screen_wall, o[1] - 2 * screen_wall, d]);
            }
            // Screw bosses for the back cover
            for (p = screen_screws())
                translate([p[0], p[1], 0]) cylinder(d = 8, h = d);
            // Stops that keep the glass from sliding up or down
            for (x = [g[0] + 10, g[0] + lcd_glass[0] - 40])
                for (y = [g[1] - lcd_fit - 1.5, g[1] + lcd_glass[1] + lcd_fit])
                    translate([x, y, screen_bezel]) cube([30, 1.5, lcd_t]);
            // Camera standoffs on the back of the bezel
            for (p = cam_holes_pos)
                translate([p[0], p[1], screen_bezel]) cylinder(d = 4.5, h = cam_lens_h);
        }
        // Window over the active area
        translate([area_pos[0] - 0.5, area_pos[1] - 0.5, -1])
            cube([lcd_area[0] + 1, lcd_area[1] + 1, screen_bezel + 2]);
        translate([cam[0], cam[1], -1]) cylinder(d = screen_cam_hole_d, h = screen_bezel + 2);
        for (p = cam_holes_pos)
            translate([p[0], p[1], screen_bezel - 1]) cylinder(d = 1.8, h = cam_lens_h + 2);
        for (p = screen_screws())
            translate([p[0], p[1], d - 8]) cylinder(d = screen_insert_d, h = 9);
        // Cable exits: power and USB at the bottom, LED cable at the top
        translate([o[0] / 2 - 30, -1, d - 16]) cube([60, screen_wall + 2, 14]);
        translate([o[0] / 2 + 40, o[1] - screen_wall - 1, d - 12]) cube([18, screen_wall + 2, 10]);
        // Push button on the right side (seen from the front)
        translate([o[0] - screen_wall - 1, o[1] / 2, screen_bezel + lcd_t + 14])
            rotate([0, 90, 0]) cylinder(d = screen_button_d, h = screen_wall + 2);
        // Vents along the top
        for (i = [0:5])
            translate([20 + i * 9, o[1] - screen_wall - 1, d - 22]) cube([4, screen_wall + 2, 16]);
    }
}

// M3 bolts through the hanger and the frame back board, clear of the
// frame's bottom rail.
function screen_tab_bolts() = let(o = screen_outer(), top = o[1] + screen_gap) [
    for (dx = [-50, 50], y = [top + 35, top + screen_tab - 10]) [o[0] / 2 + dx, y]
];

// Keyholes in the back cover (centre of the wide end) and the studs they hang
// on once the module has dropped into place.
function screen_keyholes() = let(o = screen_outer()) [
    for (dx = [-60, 60]) [o[0] / 2 + dx, o[1] - 22]
];
function screen_studs() = [
    for (k = screen_keyholes()) [k[0], k[1] + keyhole_drop]
];

// Back cover with columns that press the display against the bezel, vents
// over the Raspberry Pi, and two keyholes to hang it on its studs.
module screen_back_body() {
    o = screen_outer();
    d = screen_bezel + screen_depth;
    column = d - (screen_bezel + lcd_t);
    difference() {
        union() {
            translate([0, 0, d]) linear_extrude(screen_back_t) screen_outline(o);
            for (p = lcd_m3_pos())
                translate([p[0], p[1], screen_bezel + lcd_t]) cylinder(d = 9, h = column);
        }
        for (p = lcd_m3_pos())
            translate([p[0], p[1], 0]) cylinder(d = 3.4, h = d + screen_back_t + 1);
        // Countersunk screws into the bosses
        for (p = screen_screws())
            translate([p[0], p[1], d - 1]) {
                cylinder(d = 3.4, h = screen_back_t + 2);
                translate([0, 0, screen_back_t + 1 - 1.8]) cylinder(d1 = 3.4, d2 = 7, h = 1.81);
            }
        // Keyholes: wide end for the washer, slot for the stud
        for (k = screen_keyholes())
            translate([k[0], k[1], d - 1]) {
                cylinder(d = 11, h = screen_back_t + 2);
                translate([-3, 0, 0]) cube([6, keyhole_drop, screen_back_t + 2]);
                translate([0, keyhole_drop, 0]) cylinder(d = 6, h = screen_back_t + 2);
            }
        // Vents over the Raspberry Pi
        for (i = [0:7])
            translate([o[0] / 2 - 45, glass_origin()[1] + 25 + i * 8, d - 1]) cube([90, 3, screen_back_t + 2]);
    }
}

// Hanger plate bolted through the frame back board. Two sleeves carry M3
// bolts with washers that the module hangs on; the bolt nuts sit in hex
// pockets on the wall side. Body coordinates, behind the back cover.
module screen_hanger_body() {
    o = screen_outer();
    z = screen_total_depth();
    y0 = screen_keyholes()[0][1] - 15;
    y1 = o[1] + screen_gap + screen_tab;
    sleeve = screen_back_t + 0.6;
    difference() {
        union() {
            translate([o[0] / 2 - screen_tab_w / 2, y0, z])
                linear_extrude(screen_hanger_t) offset(4) offset(-4) square([screen_tab_w, y1 - y0]);
            for (p = screen_studs())
                translate([p[0], p[1], z - sleeve]) cylinder(d = 5.6, h = sleeve);
        }
        for (p = screen_studs())
            translate([p[0], p[1], z - sleeve - 1]) {
                cylinder(d = 3.4, h = sleeve + screen_hanger_t + 2);
                translate([0, 0, sleeve + 1 + screen_hanger_t - 2.5]) cylinder(d = 6.4, h = 3, $fn = 6);
            }
        // Countersunk on the wall side, nuts inside the frame
        for (p = screen_tab_bolts())
            translate([p[0], p[1], z - 1]) {
                cylinder(d = 3.4, h = screen_hanger_t + 2);
                translate([0, 0, screen_hanger_t + 1 - 1.8]) cylinder(d1 = 3.4, d2 = 7, h = 1.81);
            }
    }
}

// Printed face down on the textured plate.
module screenfront() {
    mirror([1, 0, 0]) screen_front_body();
}

// Printed outer face down, columns up.
module screenback() {
    d = screen_bezel + screen_depth;
    translate([0, 0, d + screen_back_t]) rotate([0, 180, 0]) mirror([1, 0, 0]) screen_back_body();
}

// Printed wall side down, sleeves up.
module screenhanger() {
    translate([0, 0, screen_total_depth() + screen_hanger_t]) rotate([0, 180, 0]) mirror([1, 0, 0]) screen_hanger_body();
}

// The module in front-view coordinates (z towards the viewer, front face at
// z = 0), for the assembly view.
module screen_module() {
    mirror([0, 0, 1]) {
        color("#1a1a1a") screen_front_body();
        color("dimgray") screen_back_body();
        if (screen_hang) color("gray") screen_hanger_body();
        color("#0b1a2a") translate([glass_origin()[0], glass_origin()[1], screen_bezel]) cube([lcd_glass[0], lcd_glass[1], 0.7]);
    }
}

// --- Raspberry Pi Zero tray (optional) -------------------------------------

// Tray bolted to the frame back board, behind the grid, for a build without
// the screen module. The Pi faces the grid; the free area on the right holds
// the 74AHCT125 board.
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
    tiles = [for (i = [0:len(splits) - 2], j = [0:len(splits) - 2]) [splits[j], splits[j + 1], splits[i], splits[i + 1]]];
    grid_top = back_t + grid_h;
    paper_z = grid_top + explode / 2;
    face_z = grid_top + explode;

    for (t = tiles) {
        color("white") grid(t);
        color("#1a1a1a") translate([0, 0, face_z + face_t]) mirror([0, 0, 1]) face_body(t);
    }
    // LED strips, one per row
    for (r = [0:cells - 1])
        color("seagreen") translate([line_x(0), cell_y(r) - 5, back_t]) cube([matrix_size, 10, 1.5]);
    color("ivory") translate([line_x(0), line_y(cells), paper_z]) cube([matrix_size, matrix_size, paper_t]);
    if (show_rings) {
        color("gray") translate([0, 0, -explode / 2]) spacer_ring();
        if (recess > 0) color("#1a1a1a") recess_ring(face_z + face_t + explode / 2);
    }
    // Screen module centred under the frame, its back against the wall
    translate([panel_size / 2 - screen_outer()[0] / 2, -clearance / 2 - (500 - inner_size) / 2 - screen_gap - screen_outer()[1],
               -back_gap + screen_total_depth() + (screen_hang ? screen_hanger_t : 0)])
        screen_module();

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

// --- Pieces view ------------------------------------------------------------

// Every printed tile, pulled apart in place and labelled, as seen from the
// front: the face on the left, the light grid on the right and the Pi tray
// below. For viewing only: the STL files are the parts to print.
module pieces() {
    gap = 20;
    n = len(splits) - 1;
    spread = panel_size + (n - 1) * gap;
    tiles = [for (i = [0:n - 1], j = [0:n - 1]) [i, j, [splits[j], splits[j + 1], splits[i], splits[i + 1]]]];
    module label(txt, x, y, z) {
        color("crimson") translate([x, y, z]) linear_extrude(0.6) text(txt, size = 12, halign = "center", valign = "center");
    }
    for (p = tiles) {
        i = p[0];
        j = p[1];
        t = p[2];
        name = str("r", i, "c", j);
        cx = (tile_x0(t) + tile_x1(t)) / 2;
        cy = (tile_y0(t) + tile_y1(t)) / 2;
        translate([j * gap, -i * gap, 0]) {
            color("#1a1a1a") face_body(t);
            label(name, cx, tile_y0(t) - gap / 2, 0);
        }
        translate([spread + 3 * gap + j * gap, -i * gap, 0]) {
            color("white") grid(t);
            label(name, cx, cy, back_t + grid_h + 1);
        }
    }
    label("FACE (changes per language)", spread / 2, panel_size + 25, 0);
    label("LIGHT GRID (common)", 1.5 * spread + 3 * gap, panel_size + 25, 0);
    // Screen module parts, below the grid
    sy = -spread + panel_size - 2 * gap - screen_outer()[1] - 40;
    sx = spread + 3 * gap + spread / 2;
    color("#1a1a1a") translate([sx - screen_outer()[0] - 10, sy, 0]) screen_front_body();
    color("dimgray") translate([sx + 10, sy, 0]) screen_back_body();
    label("Screen front", sx - screen_outer()[0] / 2 - 10, sy - 15, 0);
    label("Screen back", sx + screen_outer()[0] / 2 + 10, sy - 15, 0);
}

// --- Part selector ----------------------------------------------------------

if (part == "face") face(tile);
else if (part == "grid") grid(tile);
else if (part == "spacer") spacer();
else if (part == "recess") recess_piece();
else if (part == "screenfront") screenfront();
else if (part == "screenback") screenback();
else if (part == "screenhanger") screenhanger();
else if (part == "pitray") pitray();
else if (part == "assembly") assembly();
else if (part == "pieces") pieces();
else if (part != "none") assert(false, str("Unknown part: ", part));
