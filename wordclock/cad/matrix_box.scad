// Mini matrix in one flat box: the 10 x 6 LED grid, the 7" Raspberry Pi
// Touch Display v1 under it, the Raspberry Pi 3B beside the display, the
// camera and a USB microphone hidden behind two rivets of a decorative row,
// and room for an Arduino Uno. It hangs flat on a wall from two keyholes;
// two triangle legs hook into the back to stand it on a table. A letters
// cover sits on the grid with magnets, to try the word clock face.
//
// Sizes in millimetres. Front-view coordinates: x to the right, y up, z out
// of the wall (0 = the wall, the front of the face at z = depth).
//
// The box is too big for the 256 mm bed of the Bambu Lab A1, so the shell
// and the face are printed in four tiles (split down the middle and across
// just below the grid), the grid and the letters cover in two halves.
//
//   openscad -o shell_0.stl -D 'part="shell"' -D 'piece=0' matrix_box.scad
//
// Prefer `uv run wordclock-cad --box`, which renders every part and writes
// the Bambu Studio projects.

/* [Part selection] */
// shell | grid | face | cover | leg | test | none, or a view: assembly | front |
// back | wall | table | inside | inside_3d | exploded | letters |
// letters_exploded | letters_table
part = "assembly";
// Shell and face: 0 bottom left, 1 bottom right, 2 top left, 3 top right.
// Grid and cover: 0 left, 1 right.
piece = 0;

/* [Matrix] (as in matrix.scad) */
cols = 10;
rows = 6;
pitch = 1000 / 30;
margin = 22;
// Walls between the strip and the paper: taller than the 22 mm of the
// first matrix, for the deeper box, and they spread the light more evenly
grid_h = 30;
wall_t = 1.2;
paper_t = 0.3;
// Notch at the bottom of every column wall for the strip, 13 mm wide
strip_w = 13;
strip_notch_h = 3;

/* [Box] */
shell_t = 2.4;
back_t = 3;
face_t = 3;
corner_r = 6;
// Margin below the display, and the band between the display and the grid
bottom_margin = 20;
band_h = 30;
// Windows and bars of the face over the cells
bar_w = 3;
window_r = 1.5;

/* [Joints] */
// Dovetails between tiles (back plate and face) and the play in the socket
tab_depth = 4;
tab_neck = 5;
tab_head = 8;
joint_gap = 0.15;
// M5 bolts across the seams, in blocks on the back plate
m5_d = 5.5;
m5_nut = 9.4;
seam_block = [10, 9, 12];
// Gap left between the tiles of the face and of the shell walls
seam_gap = 0.1;

/* [Display] (Touch Display v1, as in wordclock.scad) */
lcd_glass = [192.96, 110.76];
lcd_area = [154.08, 85.92];
lcd_area_top = 11.41;
lcd_frame = [164.9, 100.6];
lcd_frame_pos = [12.54, 3.53];
lcd_t = 6;
// Metal frame behind the glass with the four M3 holes, and the driver board
lcd_frame_h = 5;
lcd_back_h = 12;
lcd_m3 = [[20, 20], [146.2, 20], [20, 85.65], [146.2, 85.65]];
// Posts from the back plate up to the frame. An M3 x 8 pan-head screw goes
// in from the wall side down a bore and seats on a shoulder near the top,
// so it bites about 3 mm into the frame and never reaches the panel.
display_post_d = 10;
display_bore_d = 6.2;
display_shoulder = 4;
glass_fit = 0.3;

/* [Raspberry Pi 3B] */
// Upright left of the display: microSD card down (slot in the bottom wall),
// USB and Ethernet up, GPIO header on the right. M2.5 screws into the posts.
pi_board = [56, 85];
pi_holes = [[3.5, 3.5], [52.5, 3.5], [3.5, 61.5], [52.5, 61.5]];
pi_standoff = 4;
pi_board_t = 1.6;
pi_ports_h = 16;
// Gap from the inner walls: wide on the left so the corner face magnet post
// leaves room for a screwdriver; low so the microSD card stays reachable.
pi_gap = [14, 5];
sd_slot = [16, 5];

/* [Camera and microphone] */
// OV5647 board behind one rivet, M2 holes on 21 x 12.5 mm
cam_board = [25, 24];
cam_holes = [21, 12.5];
cam_hole_top = 2;
cam_lens_from_top = 9.5;
cam_lens_h = 6;
// The lens sits in a pocket in the back of the face, 1 mm behind the front,
// so the 4 mm rivet hole does not crop the picture
cam_pocket = [12.5, 2];
cam_post_d = 5;
// Optional USB microphone behind the rivet that mirrors the camera, in a
// cradle. Off: no cradle, and its rivet is a plain one like the rest.
mic = false;
mic_board = [16, 12, 6];
rivet_d = 4;
rivet_depth = 1;
rivet_pitch = 24;
rivet_drop = 2.5;

/* [Arduino Uno] */
// Upright right of the display, USB-B and power jack up, so the USB cable
// has room above it. Holes from the corner below the headers.
uno_board = [53.4, 68.6];
uno_holes = [[2.5, 54.6], [50.7, 53.3], [7.6, 2.5], [35.5, 2.5]];
uno_xy = [298, 22];
// Low, so 90° jumper wires in the headers clear the face
uno_standoff = 3;

/* [Power and wiring] */
// Female 5.5 x 2.1 mm DC jack adapter with screw terminals (the CCTV kind):
// its round nose goes through the bottom wall, flush outside, and its body
// clips into a cradle on the back plate. Measure yours and set the sizes.
jack_nose = [11, 12];        // diameter, length
jack_body = [13.5, 11.5, 23]; // width, height, length behind the nose
jack_fit = 0.3;
jack_x = 85;
// Two lever connectors (WAGO 221-413) that share the 5 V and the ground
wago = [20.2, 13.1, 8.3];
vent = [3, 18];

/* [Magnets] */
// 5 x 2 mm neodymium discs, only for the letters cover
magnet_d = 5;
magnet_h = 2;
magnet_fit = 0.2;

/* [Face screws] */
// The face sits inside the shell walls, flush with them, on 12 posts, and an
// M3 x 12 countersunk screw (ISO 10642) from the front goes into each post.
// Two notches in the bottom wall let a fingernail lift it out again.
face_post_d = 9;
face_fit = 0.2;
pry_notch = [14, 2];
face_screw_head = 6.9;
face_screw_hole = 3.4;
face_screw_pilot = 2.5;
face_screw_depth = 12;
pry_xs = [-30, 30];    // from the vertical seam

/* [Letters cover] */
// Top-left 6 x 10 corner of the Catalan word clock grid
letters = [
    "ÉSÓNTVORAH",
    "UNGDOSNTRE",
    "QUARTSSBKC",
    "IMENYSZCIN",
    "DED'LAPLES",
    "UNADUESTRE",
];
font = "Karla:style=Bold Stencil";
// Same cap height as the big clock, so the test shows the real letter size
cap_height = 15;
cap_ratio = 0.901;
accent_ratio = 1.25;
descent_ratio = 0.25;
cover_t = 2.4;
cover_border = 9;
cover_r = 4;

/* [Wall and table] */
// Keyholes in the top margin for two M5 wall screws
keyhole_dx = 100;
wall_head_d = 10.4;
wall_neck_d = 5.6;
wall_slide = 8;
// Centre of the wide entry, below the top wall
keyhole_from_top = 8.3;
// Triangle legs: two hooks on each go through slots in the back plate and
// slide down. The box rests on its bottom back edge and on the feet.
tilt = 15;
stand_y0 = 25;
stand_y1 = 125;
stand_reach = 100;
leg_t = 4;
stand_dx = 45;
hook = [20, 4];
hook_ys = [32, 97];
slot_fit = 0.3;

use <fonts/KarlaBoldStencil.ttf>

$fn = 40;

// --- Derived sizes ---------------------------------------------------------

box_w = cols * pitch + 2 * margin;
grid_w = cols * pitch;
grid_hh = rows * pitch;
glass_x = (box_w - lcd_glass[0]) / 2;
glass_y = bottom_margin;
glass_top = glass_y + lcd_glass[1];
// A little below the middle of the band, so the camera board and its top
// posts stay below the horizontal print split
rivet_y = glass_top + band_h / 2 - rivet_drop;
grid_y = glass_top + band_h;
box_h = grid_y + grid_hh + margin;
face_back = back_t + grid_h + paper_t;
depth = face_back + face_t;
glass_back = depth - lcd_t;
frame_back = glass_back - lcd_frame_h;
seam_x = box_w / 2;
// Across just below the grid, between the rivet row and the grid
split_y = grid_y - 6;

function line_x(k) = margin + k * pitch;
function line_y(k) = grid_y + grid_hh - k * pitch;
function cell_x(c) = line_x(c) + pitch / 2;
function cell_y(r) = line_y(r) - pitch / 2;

function rivets() = let(n = floor((box_w - 2 * margin) / rivet_pitch))
    [for (i = [0:n]) [margin + i * (box_w - 2 * margin) / n, rivet_y]];
// Camera behind the first rivet whose board clears the seam, microphone
// behind the mirrored rivet
cam_x = [for (p = rivets()) if (p[0] - cam_board[0] / 2 > seam_x + 2) p[0]][0];
mic_x = box_w - cam_x;
cam_x0 = cam_x - cam_board[0] / 2;
cam_y0 = rivet_y + cam_lens_from_top - cam_board[1];
cam_z = face_back + cam_pocket[1] - cam_lens_h - 1;
mic_z = face_back - mic_board[2] - 0.5;

pi_x = shell_t + pi_gap[0];
pi_y = shell_t + pi_gap[1];
pi_z = back_t + pi_standoff;
pi_top = pi_z + pi_board_t + pi_ports_h;
// The jack body, from the end of its nose to its screw terminals
jack_z = back_t + jack_body[1] / 2;
jack_y0 = jack_nose[1];
jack_y1 = jack_y0 + jack_body[2];
// WAGO connectors behind the jack, room to bend its wires in between
wago_xy = [pi_x + pi_board[0] + 6, jack_y1 + 10];
// Female jumper housings (14 mm) pushed onto the 2.5 mm header base
dupont_top = pi_z + pi_board_t + 2.5 + 14;

function display_holes() = [for (h = lcd_m3) [glass_x, glass_y] + lcd_frame_pos + h];

// Posts the face rests on: three per tile, clear of the seams, the
// keyholes, the DC jack and the wires (the strip turns in the side margins).
fm = shell_t + face_post_d / 2;
// One screw per post, nudged 0.6 mm away from the walls so the heads keep
// clear of the edge of the face
function edge_nudge(v, size) = v < fm + 1 ? 0.6 : v > size - fm - 1 ? -0.6 : 0;
function face_screws() = [for (p = face_posts()) p + [edge_nudge(p[0], box_w), edge_nudge(p[1], box_h)]];
function face_posts() = [
    [fm, fm], [box_w / 4 + 10, fm], [fm, rivet_y - 6],
    [box_w - fm, fm], [box_w * 3 / 4, fm], [box_w - fm, rivet_y - 6],
    [fm, box_h - fm], [box_w / 4, box_h - fm], [seam_x - 20, box_h - fm],
    [box_w - fm, box_h - fm], [box_w * 3 / 4, box_h - fm], [seam_x + 20, box_h - fm],
];

// Letters cover: two halves, four magnets each
font_size = cap_height / cap_ratio;
baseline = -(accent_ratio - descent_ratio) * font_size / 2;
cover_x0 = margin - cover_border;
cover_x1 = box_w - margin + cover_border;
cover_y0 = grid_y - cover_border;
cover_y1 = grid_y + grid_hh + cover_border;
cm = cover_border / 2;
function cover_magnets(h) = let(x0 = h == 0 ? cover_x0 + cm : seam_x + cm, x1 = h == 0 ? seam_x - cm : cover_x1 - cm)
    [[x0, grid_y - 2], [x1, grid_y - 2], [x0, cover_y1 - cm], [x1, cover_y1 - cm]];

// Seam joints: dovetails along the seams, M5 blocks in the margins
plate_tabs_v = [40, 100, 200, 260, 320];
plate_tabs_h = [30, 90, 150, 230, 290, 350];
face_tabs_v = [10, glass_top + 9, box_h - 11];
face_tabs_h = [50, 120, 250, 320];
seam_bolts_v = [11, 75, box_h - 11];
seam_bolts_h = [40, 120, 260, 340];

echo(str("Box ", box_w, " x ", box_h, " x ", depth, " mm"));
echo(str("Tiles: bottom ", split_y, " mm, top ", box_h - split_y, " mm high, ", seam_x, " mm wide"));
echo(str("Room above the Pi ports: ", face_back - pi_top, " mm"));
echo(str("Room under the display driver board: ", glass_back - lcd_back_h - back_t, " mm"));

assert(seam_x + tab_depth < 250 && box_h - split_y + tab_depth < 250, "A tile does not fit the A1 bed");
assert(face_back - pi_top >= 8, "Less than 8 mm above the Pi ports");
assert(glass_back - lcd_back_h - back_t >= 8, "No room for the ribbon under the display");
assert(pi_x + pi_board[0] < glass_x, "The Pi overlaps the display");
assert(norm([pi_x + pi_holes[0][0], pi_y + pi_holes[0][1]] - [fm, fm]) - face_post_d / 2 >= 8, "No screwdriver room between the Pi and the corner post");
assert(wago_xy[0] + wago[0] < glass_x + lcd_frame_pos[0], "The WAGO connectors sit under the display frame");
assert(rivet_y + rivet_d / 2 + 2 < split_y, "The split cuts the rivet row");
assert(split_y + tab_depth < grid_y + bar_w / 2 + window_r, "Face dovetails reach the windows");
assert(cover_y0 - rivet_y > rivet_d, "The letters cover hides the rivets");
assert(uno_xy[0] > glass_x + lcd_glass[0] + 6 && uno_xy[0] + uno_board[0] < box_w - shell_t - 6, "The Uno does not fit");
assert(cam_x0 > seam_x + 1, "The camera posts sit on the seam");
assert(cam_y0 + cam_board[1] - cam_hole_top + cam_post_d / 2 + 1 < split_y, "The camera posts sit on the horizontal seam");
assert(face_back - dupont_top >= 6, "No room to bend the jumper wires on the Pi header");
assert(jack_x - jack_body[0] / 2 - 2 > pi_x + pi_board[0] + 2.5, "The jack cradle hits the Pi power port");
assert(min([for (p = face_screws()) min(p[0], p[1], box_w - p[0], box_h - p[1])]) - shell_t - face_fit - face_screw_head / 2 >= 1.2, "The face screw heads reach the edge of the face");
assert(jack_x + jack_body[0] / 2 + 2 < box_w / 4 + 10 - face_post_d / 2, "The jack cradle hits a face magnet post");

// --- 2D helpers ----------------------------------------------------------

module rounded(size, r) {
    offset(r) offset(-r) square(size);
}

module outline_2d() {
    rounded([box_w, box_h], corner_r);
}

function tile_x0(t) = t % 2 == 0 ? -1 : seam_x;
function tile_x1(t) = t % 2 == 0 ? seam_x : box_w + 1;
function tile_y0(t) = t < 2 ? -1 : split_y;
function tile_y1(t) = t < 2 ? split_y : box_h + 1;

module tile_rect(t) {
    translate([tile_x0(t), tile_y0(t)]) square([tile_x1(t) - tile_x0(t), tile_y1(t) - tile_y0(t)]);
}

module dovetail(grow = 0) {
    offset(delta = grow) polygon([[-1, -tab_neck / 2], [tab_depth, -tab_head / 2], [tab_depth, tab_head / 2], [-1, tab_neck / 2]]);
}

// Tabs point right (+x) out of the left tiles and up (+y) out of the bottom
// tiles; the other tiles have the sockets.
module seam_joints(t, ys, xs, grow, tabs) {
    left = t % 2 == 0;
    bottom = t < 2;
    if (tabs ? left : !left) for (y = ys) if (y > tile_y0(t) + 6 && y < tile_y1(t) - 6) translate([seam_x, y]) dovetail(grow);
    if (tabs ? bottom : !bottom) for (x = xs) if (x > tile_x0(t) + 6 && x < tile_x1(t) - 6) translate([x, split_y]) rotate(90) dovetail(grow);
}

module tile_2d(t, ys, xs) {
    difference() {
        union() {
            intersection() {
                outline_2d();
                tile_rect(t);
            }
            seam_joints(t, ys, xs, 0, true);
        }
        seam_joints(t, ys, xs, joint_gap, false);
    }
}

// --- Shell ---------------------------------------------------------------

module keyhole() {
    translate([0, 0, -1]) {
        cylinder(d = wall_head_d, h = back_t + 2);
        hull() for (dy = [0, wall_slide]) translate([0, -dy, 0]) cylinder(d = wall_neck_d, h = back_t + 2);
    }
}

module leg_slots() {
    for (dx = [-stand_dx, stand_dx], y = hook_ys)
        translate([seam_x + dx - leg_t / 2 - slot_fit, y - hook[1] - slot_fit, -1])
            cube([leg_t + 2 * slot_fit, hook[0] + hook[1] + 2 * slot_fit, back_t + 2]);
}

// M5 seam block, half on each side of the seam: `normal` is the axis the
// bolt runs along. The left or bottom half has the hex pocket for the nut.
module seam_block(p, normal, near) {
    s = seam_block;
    // Across the bottom of the grid the far side only has room up to the
    // grid frame.
    far = normal == "y" ? grid_y - wall_t / 2 - 0.6 - split_y : s[0];
    len = near ? s[0] : far;
    translate([p[0], p[1], 0]) rotate([0, 0, normal == "x" ? 0 : 90]) difference() {
        translate([near ? -s[0] : 0, -s[1] / 2, 0]) cube([len, s[1], back_t + s[2]]);
        translate([0, 0, back_t + s[2] / 2]) rotate([0, 90, 0]) {
            cylinder(d = m5_d, h = 2 * s[0] + 2, center = true);
            if (near) translate([0, 0, -s[0] - 1]) cylinder(d = m5_nut, h = 5, $fn = 6);
        }
    }
}

module shell_posts() {
    // Display: M3 from the back into the frame, countersunk on the wall side
    for (h = display_holes()) translate([h[0], h[1], 0]) cylinder(d = display_post_d, h = frame_back);
    // Camera: M2 pilot holes
    for (dx = [0, cam_holes[0]], dy = [0, cam_holes[1]])
        translate([cam_x0 + (cam_board[0] - cam_holes[0]) / 2 + dx, cam_y0 + cam_board[1] - cam_hole_top - dy, 0])
            difference() {
                cylinder(d = cam_post_d, h = cam_z);
                translate([0, 0, cam_z - 6]) cylinder(d = 1.6, h = 7);
            }
    // Raspberry Pi: M2.5 pilot holes
    for (h = pi_holes) translate([pi_x + h[0], pi_y + h[1], 0]) difference() {
        cylinder(d = 6, h = pi_z);
        translate([0, 0, pi_z - 6]) cylinder(d = 2.2, h = 7);
    }
    // Arduino Uno: M3 pilot holes
    for (h = uno_holes) translate([uno_xy[0] + h[0], uno_xy[1] + h[1], 0]) difference() {
        cylinder(d = 6.5, h = back_t + uno_standoff);
        translate([0, 0, 1]) cylinder(d = 2.6, h = back_t + uno_standoff);
    }
    // Microphone cradle up to the back of the face
    if (mic) translate([mic_x - mic_board[0] / 2 - 2, rivet_y - mic_board[1] / 2 - 2, 0]) difference() {
        cube([mic_board[0] + 4, mic_board[1] + 4, mic_z + 3]);
        translate([2, 2, mic_z]) cube([mic_board[0], mic_board[1], 4]);
        // Cable exit
        translate([-1, 2 + mic_board[1] / 2 - 3, mic_z]) cube([4, 6, 4]);
    }
    // Face rests
    for (p = face_posts()) translate([p[0], p[1], 0]) cylinder(d = face_post_d, h = face_back);
    // Grid locating pins, under the lugs of the grid
    for (p = grid_pins()) translate([p[0], p[1], 0]) cylinder(d = 3, h = back_t + 4);
}

module shell_body() {
    difference() {
        union() {
            linear_extrude(back_t) outline_2d();
            linear_extrude(depth) difference() {
                outline_2d();
                offset(-shell_t) outline_2d();
            }
            shell_posts();
            jack_cradle();
        }
        for (dx = [-keyhole_dx / 2, keyhole_dx / 2]) translate([seam_x + dx, box_h - keyhole_from_top, 0]) keyhole();
        leg_slots();
        // Pilot holes for the face screws
        for (p = face_screws()) translate([p[0], p[1], face_back - face_screw_depth]) cylinder(d = face_screw_pilot, h = face_screw_depth + 1);
        // Notches to lift the face out
        for (dx = pry_xs) translate([seam_x + dx - pry_notch[0] / 2, -1, depth - pry_notch[1]]) cube([pry_notch[0], shell_t + 2, pry_notch[1] + 1]);
        // DC jack nose through the bottom wall
        translate([jack_x, -1, jack_z]) rotate([-90, 0, 0]) cylinder(d = jack_nose[0] + 2 * jack_fit, h = shell_t + 2);
        // microSD slot under the card
        translate([pi_x + pi_board[0] / 2 - sd_slot[0] / 2, -1, pi_z - 3]) cube([sd_slot[0], shell_t + 2, sd_slot[1]]);
        // Vents: bottom wall under the Pi, left wall high beside it
        // (bottom vents start above the microSD slot, so they do not merge)
        for (i = [0:3]) translate([pi_x + 4 + i * 9, -1, pi_z + sd_slot[1]]) cube([vent[0], shell_t + 2, vent[1]]);
        for (i = [0:3]) translate([-1, pi_y + 50 + i * 9, back_t + 6]) cube([shell_t + 2, vent[0], vent[1]]);
        // Display screws: a bore from the wall side, then the shoulder
        for (h = display_holes()) translate([h[0], h[1], -1]) {
            cylinder(d = 3.4, h = frame_back + 2);
            cylinder(d = display_bore_d, h = frame_back - display_shoulder + 1);
        }
    }
}

// One tile of the shell, printed with its back on the bed.
module shell(t) {
    difference() {
        union() {
            intersection() {
                shell_body();
                translate([0, 0, -1]) linear_extrude(depth + 2) offset(delta = -seam_gap / 2) tile_rect(t);
            }
            // Dovetail tabs of the back plate
            linear_extrude(back_t) intersection() {
                seam_joints(t, plate_tabs_v, plate_tabs_h, 0, true);
                offset(-shell_t) outline_2d();
            }
        }
        translate([0, 0, -1]) linear_extrude(back_t + 2) seam_joints(t, plate_tabs_v, plate_tabs_h, joint_gap, false);
    }
    // Seam blocks on this tile's side
    left = t % 2 == 0;
    bottom = t < 2;
    for (y = seam_bolts_v) if (y > tile_y0(t) && y < tile_y1(t)) seam_block([seam_x, y], "x", left);
    for (x = seam_bolts_h) if (x > tile_x0(t) && x < tile_x1(t)) seam_block([x, split_y], "y", bottom);
}

// --- Grid ----------------------------------------------------------------

// Lugs on the outside of the grid frame, top and bottom, over pins in the
// back plate: they keep each half in place under the face.
function grid_pins() = [for (c = [1, 3, 6, 8], side = [0, 1]) [cell_x(c), side == 0 ? grid_y - 4 : grid_y + grid_hh + 4]];

module column_wall(k, h) {
    x = line_x(k);
    x0 = k == 5 ? (h == 0 ? x - wall_t : x) : x - wall_t / 2;
    translate([x0, grid_y - wall_t / 2]) square([wall_t, grid_hh + wall_t]);
}

module walls_2d(h) {
    for (k = h == 0 ? [0:5] : [5:cols]) column_wall(k, h);
    for (k = [0:rows]) {
        x0 = h == 0 ? line_x(0) - wall_t / 2 : seam_x;
        x1 = h == 0 ? seam_x : line_x(cols) + wall_t / 2;
        translate([x0, line_y(k) - wall_t / 2]) square([x1 - x0, wall_t]);
    }
}

module grid_half(h) {
    difference() {
        union() {
            translate([0, 0, back_t]) linear_extrude(grid_h) walls_2d(h);
            for (p = grid_pins()) if ((p[0] < seam_x) == (h == 0)) {
                wall_y = p[1] < grid_y ? grid_y - wall_t / 2 : grid_y + grid_hh + wall_t / 2;
                // Block at the foot of the frame, with a 45 degree gusset up
                // the wall so it prints upside down without support
                translate([0, 0, back_t]) hull() {
                    translate([p[0], p[1], 0]) cylinder(d = 7, h = 5);
                    translate([p[0] - 3.5, min(wall_y, p[1]), 0]) cube([7, abs(wall_y - p[1]), 5]);
                    translate([p[0] - 3.5, wall_y - (p[1] < grid_y ? 0.01 : 0), 0]) cube([7, 0.01, 5 + abs(wall_y - p[1]) + 3.5]);
                }
            }
        }
        for (k = h == 0 ? [0:5] : [5:cols], r = [0:rows - 1])
            translate([line_x(k) - wall_t - 1, cell_y(r) - strip_w / 2, back_t - 0.01]) cube([2 * wall_t + 2, strip_w, strip_notch_h + 0.01]);
        for (p = grid_pins()) translate([p[0], p[1], back_t - 1]) cylinder(d = 3.4, h = 5.5);
    }
}

// Printed upside down, the top of the walls on the bed.
module grid(h) {
    translate([0, 0, back_t + grid_h]) mirror([0, 0, 1]) translate([0, 0, 0]) grid_half(h);
}

// --- Face ----------------------------------------------------------------

module windows_2d() {
    for (c = [0:cols - 1], r = [0:rows - 1])
        translate([line_x(c) + bar_w / 2, cell_y(r) - pitch / 2 + bar_w / 2]) rounded([pitch - bar_w, pitch - bar_w], window_r);
    translate([glass_x - glass_fit, glass_y - glass_fit]) square([lcd_glass[0] + 2 * glass_fit, lcd_glass[1] + 2 * glass_fit]);
}

// Face in place, front at z = depth.
module face_outline_2d() {
    offset(r = -(shell_t + face_fit)) outline_2d();
}

module face_body(t) {
    translate([0, 0, face_back]) difference() {
        linear_extrude(face_t) difference() {
            intersection() {
                offset(delta = -seam_gap / 2) tile_2d(t, face_tabs_v, face_tabs_h);
                face_outline_2d();
            }
            windows_2d();
        }
        for (p = rivets()) {
            through = abs(p[0] - cam_x) < 1 || (mic && abs(p[0] - mic_x) < 1);
            translate([p[0], p[1], through ? -1 : face_t - rivet_depth]) cylinder(d = rivet_d, h = face_t + 2);
        }
        translate([cam_x, rivet_y, -1]) cylinder(d = cam_pocket[0], h = cam_pocket[1] + 1);
        // Countersunk screw holes over the posts, heads flush with the front
        for (p = face_screws()) translate([p[0], p[1], 0]) {
            translate([0, 0, -1]) cylinder(d = face_screw_hole, h = face_t + 2);
            cs = (face_screw_head - face_screw_hole) / 2;
            translate([0, 0, face_t - cs]) cylinder(d1 = face_screw_hole, d2 = face_screw_head, h = cs + 0.01);
            translate([0, 0, face_t]) cylinder(d = face_screw_head, h = 1);
        }
        for (h = [0, 1], p = cover_magnets(h)) translate([p[0], p[1], face_t - magnet_h - 0.2]) cylinder(d = magnet_d + magnet_fit, h = magnet_h + 1);
    }
}

// Printed front side up: the rivet dimples are open on top, so no layer
// starts over air (front down they would be floating islands).
module face(t) {
    translate([0, 0, -face_back]) face_body(t);
}

// --- Letters cover -------------------------------------------------------

module letters_2d() {
    for (r = [0:rows - 1], c = [0:cols - 1])
        let(ch = letters[r][c]) if (ch != " ")
            translate([cell_x(c), cell_y(r) + baseline])
                text(ch, size = font_size, font = font, halign = "center", valign = "baseline");
}

// Cover half in place, on the face.
module cover_body(h) {
    x0 = h == 0 ? cover_x0 : seam_x + seam_gap / 2;
    x1 = h == 0 ? seam_x - seam_gap / 2 : cover_x1;
    translate([0, 0, depth]) difference() {
        linear_extrude(cover_t) difference() {
            intersection() {
                translate([cover_x0, cover_y0]) rounded([cover_x1 - cover_x0, cover_y1 - cover_y0], cover_r);
                translate([x0, cover_y0 - 1]) square([x1 - x0, cover_y1 - cover_y0 + 2]);
            }
            letters_2d();
        }
        for (p = cover_magnets(h)) translate([p[0], p[1], -0.01]) cylinder(d = magnet_d + magnet_fit, h = magnet_h + 0.2);
    }
}

// Printed front side down.
module cover(h) {
    translate([0, 0, depth + cover_t]) mirror([0, 0, 1]) cover_body(h);
}

// --- Legs ----------------------------------------------------------------

function table_y(z) = -z * tan(tilt);

// Leg in its own plane: u along the back of the box (y), v away from it
// (-z). Two hooks go through the back plate and hold behind it.
module leg_2d() {
    foot = [table_y(-stand_reach), stand_reach];
    polygon([[stand_y0, 0], [stand_y1, 0], foot]);
    for (y = hook_ys) {
        translate([y, -back_t - slot_fit]) square([hook[0], back_t + slot_fit + 0.01]);
        translate([y - hook[1], -back_t - slot_fit - 3]) square([hook[0] + hook[1], 3]);
    }
}

// Leg in place behind the box.
module leg_in_place(dx) {
    translate([seam_x + dx, 0, 0]) rotate([90, 0, 90]) mirror([0, 1, 0]) translate([0, 0, -leg_t / 2]) linear_extrude(leg_t) leg_2d();
}

// Printed flat.
module leg() {
    linear_extrude(leg_t) leg_2d();
}

// --- Parts drawn for the views -------------------------------------------

function hsv(h) = let(k = [for (n = [5, 3, 1]) (n + (h % 1) * 6) % 6])
    [for (v = k) 1 - max(0, min(v, 4 - v, 1))];

module leds() {
    for (c = [0:cols - 1], r = [0:rows - 1])
        translate([cell_x(c), cell_y(r), back_t]) {
            color("#e8e8e8") translate([-2.5, -2.5, 0]) cube([5, 5, 1.6]);
            color(hsv((rows - 1 - r) * 0.12 + c * 0.03)) translate([0, 0, 1.6]) cylinder(d = 3, h = 0.6);
        }
}

module glow() {
    for (c = [0:cols - 1], r = [0:rows - 1])
        color([for (v = hsv((rows - 1 - r) * 0.12 + c * 0.03)) 0.35 + 0.65 * v])
            translate([line_x(c) + wall_t / 2, cell_y(r) - pitch / 2 + wall_t / 2, back_t + grid_h - 1.5])
                cube([pitch - wall_t, pitch - wall_t, 0.5]);
}

module display() {
    translate([glass_x, glass_y, glass_back]) {
        color("#111") cube([lcd_glass[0], lcd_glass[1], lcd_t]);
        color("#3a5f8a") translate([(lcd_glass[0] - lcd_area[0]) / 2, lcd_glass[1] - lcd_area_top - lcd_area[1], lcd_t])
            cube([lcd_area[0], lcd_area[1], 0.1]);
        color("#888") translate([lcd_frame_pos[0], lcd_frame_pos[1], -lcd_back_h]) cube([lcd_frame[0], lcd_frame[1], lcd_back_h]);
    }
}

// Raspberry Pi 3B seen from the component side with USB up: the GPIO
// header runs along the left edge (pin 1 at the bottom), HDMI, power and
// audio stick out on the right, DSI at the bottom, CSI in the middle right.
module pi() {
    translate([pi_x, pi_y, pi_z]) {
        color("#1f7a3a") cube([pi_board[0], pi_board[1], pi_board_t]);
        // USB and Ethernet, 2 mm past the top edge
        color("#bbb") translate([2, pi_board[1] - 19, pi_board_t]) cube([52, 21, pi_ports_h]);
        // GPIO header with jumper housings on pins 2, 6 and 12
        color("#222") translate([1, 7.1, pi_board_t]) cube([5, 50.8, 8.5]);
        color("#c33") for (n = [2, 6, 12]) translate(pin(n) - [pi_x + 1.27, pi_y + 1.27, pi_z - pi_board_t - 2.5]) cube([2.54, 2.54, 14]);
        // DSI along the bottom, CSI to the right
        color("#eee") translate([17, 1.5, pi_board_t]) cube([22, 5, 5.5]);
        color("#eee") translate([33.5, 42.5, pi_board_t]) cube([22, 5, 5.5]);
        // Power, HDMI and audio past the right edge
        color("#999") translate([pi_board[0] - 5.6, 10.6 - 4, pi_board_t]) cube([7, 8, 3]);
        color("#999") translate([pi_board[0] - 11, 32 - 7.5, pi_board_t]) cube([12, 15, 6.5]);
        color("#222") translate([pi_board[0] - 12, 53.5 - 3, pi_board_t]) cube([14.5, 6, 6]);
        color("#333") translate([18, 25, pi_board_t]) cube([14, 14, 1.5]);
        // microSD card under the board, sticking out at the bottom
        color("#c33") translate([pi_board[0] / 2 - 6, -2.5, -1.5]) cube([12, 15, 1.4]);
    }
}

module uno() {
    translate([uno_xy[0], uno_xy[1], back_t + uno_standoff]) {
        color("#1a6ea8") cube([uno_board[0], uno_board[1], 1.6]);
        // USB-B and power jack at the top edge, headers along the sides
        color("#bbb") translate([6, uno_board[1] - 14, 1.6]) cube([12, 16, 11]);
        color("#222") translate([33, uno_board[1] - 12, 1.6]) cube([9, 14, 11]);
        color("#222") translate([0.5, 8, 1.6]) cube([2.5, 45, 8.5]);
        color("#222") translate([uno_board[0] - 3, 4, 1.6]) cube([2.5, 52, 8.5]);
    }
}

module camera() {
    translate([cam_x0, cam_y0, cam_z]) {
        color("#2a6e2a") cube([cam_board[0], cam_board[1], 1]);
        color("#111") translate([cam_board[0] / 2, cam_board[1] - cam_lens_from_top, 1]) cylinder(d = 8, h = cam_lens_h);
    }
}

module mic() {
    if (mic) translate([mic_x - mic_board[0] / 2, rivet_y - mic_board[1] / 2, mic_z]) color("#333") cube(mic_board);
}

module jack() {
    color("#222") {
        translate([jack_x, 0, jack_z]) rotate([-90, 0, 0]) cylinder(d = jack_nose[0], h = jack_y0);
        translate([jack_x - jack_body[0] / 2, jack_y0, back_t]) cube([jack_body[0], jack_body[2] - 8, jack_body[1]]);
    }
    color("#2a8a3a") translate([jack_x - jack_body[0] / 2, jack_y1 - 8, back_t]) cube([jack_body[0], 8, jack_body[1]]);
}

// Cradle for the jack body: two rails with small lips that clip over it,
// and a low stop behind it that takes the push of the plug
module jack_cradle() {
    w = jack_body[0] + 2 * jack_fit;
    h = jack_body[1] + jack_fit;
    rail = 1.6;
    lip = 0.8;
    for (side = [-1, 1]) translate([jack_x + side * (w / 2 + rail / 2), 0, 0]) {
        translate([-rail / 2, jack_y0, 0]) cube([rail, jack_body[2] - 10, back_t + h + 1.2]);
        // Lip, sloped underneath so it prints without support
        translate([-side * rail / 2, jack_y0, back_t + h]) hull() {
            cube([0.01, jack_body[2] - 10, 1.2]);
            translate([-side * lip, 0, 0.6]) cube([0.01, jack_body[2] - 10, 0.6]);
        }
    }
    translate([jack_x - w / 2 - rail, jack_y1 + jack_fit, 0]) cube([w + 2 * rail, 2, back_t + 3.5]);
}

module wagos() {
    for (i = [0, 1]) translate([wago_xy[0], wago_xy[1] + i * (wago[1] + 3), back_t]) {
        color("#e8e8e8") cube(wago);
        color("#f08a00") for (k = [0:2]) translate([2 + k * 6.5, 2, wago[2]]) cube([4, wago[1] - 4, 1.5]);
    }
}

module cable(points, c, d = 2) {
    color(c) for (i = [0:len(points) - 2]) hull() {
        translate(points[i]) sphere(d = d, $fn = 12);
        translate(points[i + 1]) sphere(d = d, $fn = 12);
    }
}

// The strip starts at the bottom-left cell (run the show with --rotate
// --mirror); power and data come up the left side of the band.
strip_in = [cell_x(0), cell_y(rows - 1), back_t + 1];
// GPIO pin n: even pins on the board edge row, pin 1 near the microSD end
function pin(n) = [pi_x + (n % 2 == 0 ? 2.23 : 4.77), pi_y + 8.37 + 2.54 * floor((n - 1) / 2), pi_z + pi_board_t + 2.5];

module wiring() {
    w = [wago_xy[0] + 4, wago_xy[1] + 4, back_t + wago[2]];
    g = [wago_xy[0] + 4, wago_xy[1] + wago[1] + 7, back_t + wago[2]];
    jk = [jack_x - 2, jack_y1, jack_z];
    up = 16;
    top = pi_y + pi_board[1] + 8;
    cable([jk, [jack_x, w[1], 10], w], "red");
    cable([jk + [2, 0, 0], [jack_x + 2, g[1], 10], g], "black");
    // Pi 5 V and ground: up out of the jumper housings, across the bottom
    // of the board above its parts, down to the WAGO connectors
    hz = dupont_top + 4;
    cable([w + [6, 0, 0], [w[0] + 6, w[1], hz], [pin(2)[0], w[1] - 6, hz], [pin(2)[0], pin(2)[1], hz], pin(2) + [0, 0, 14]], "red", 1.4);
    cable([g + [6, 0, 0], [g[0] + 6, g[1], hz], [pin(6)[0] + 1, g[1] - 6, hz], [pin(6)[0], pin(6)[1], hz], pin(6) + [0, 0, 14]], "black", 1.4);
    cable([w + [12, 0, 0], [w[0] + 12, top, 6], [up, top, 6], [up, strip_in[1] - 6, 4], [line_x(0) - 3, strip_in[1] - 4, 4], strip_in + [-6, -4, 0]], "red");
    cable([g + [12, 0, 0], [g[0] + 15, top + 3, 6], [up + 2.5, top + 3, 6], [up + 2.5, strip_in[1] - 3, 4], [line_x(0) - 3, strip_in[1], 4], strip_in + [-6, 0, 0]], "black");
    cable([pin(12) + [0, 0, 14], [pin(12)[0], pin(12)[1], hz], [shell_t + 5, pin(12)[1], hz], [shell_t + 5, top + 6, 8], [up + 5, top + 6, 8], [up + 5, strip_in[1], 4], [line_x(0) - 3, strip_in[1] + 4, 4], strip_in + [-6, 4, 0]], "green", 1.4);
    drv = [glass_x + lcd_glass[0] / 2, glass_y + 30, glass_back - lcd_back_h];
    cable([w + [18, 0, 0], [w[0] + 30, w[1], 8], [drv[0] - 20, drv[1], 8], drv + [-20, 0, 0]], "red", 1.4);
    cable([g + [18, 0, 0], [g[0] + 30, g[1], 8], [drv[0] - 20, drv[1] + 4, 8], drv + [-20, 4, 0]], "black", 1.4);
    dsi = [pi_x + 28, pi_y + 4, pi_z + 7];
    cable([dsi, [dsi[0], dsi[1], 8], [drv[0], dsi[1], 8], drv + [0, -5, 0]], "#f2f2f2", 3.5);
    // CSI: up over the USB ports, then across just above the glass, under
    // the microphone cradle if fitted, into the bottom edge of the camera board
    csi = [pi_x + 44.5, pi_y + 45, pi_z + 7];
    cable([csi, [csi[0], csi[1], pi_top + 3], [csi[0], glass_top + 2, pi_top + 3], [cam_x, glass_top + 2, 18], [cam_x, cam_y0, cam_z - 1]], "#f2f2f2", 3.5);
    usb = [pi_x + 15, pi_y + pi_board[1] + 2, pi_z + 10];
    if (mic) cable([usb, [usb[0], usb[1] + 6, 10], [mic_x - 20, glass_top + 3, 10], [mic_x - 20, rivet_y, 16], [mic_x - mic_board[0] / 2, rivet_y, mic_z + 2]], "#444", 3);
    usb2 = [pi_x + 40, pi_y + pi_board[1] + 2, pi_z + 10];
    plug = [uno_xy[0] + 12, uno_xy[1] + uno_board[1] + 4, back_t + uno_standoff + 8];
    cable([usb2, [usb2[0], usb2[1] + 12, 6], [plug[0], usb2[1] + 12, 6], plug + [0, 20, 0], plug], "#444", 3);
}

module seam_bolts_drawn() {
    color("silver") {
        for (y = seam_bolts_v) translate([seam_x, y, back_t + seam_block[2] / 2]) rotate([0, 90, 0]) cylinder(d = 5, h = 2 * seam_block[0] + 4, center = true);
        for (x = seam_bolts_h) translate([x, split_y, back_t + seam_block[2] / 2]) rotate([90, 0, 0]) cylinder(d = 5, h = 2 * seam_block[0] + 4, center = true);
    }
}

module shell_all() {
    for (t = [0:3]) shell(t);
}

module face_all() {
    for (t = [0:3]) face_body(t);
}

module inside(cables = false) {
    color("white") for (h = [0, 1]) grid_half(h);
    leds();
    display();
    pi();
    uno();
    camera();
    mic();
    jack();
    wagos();
    if (cables) wiring();
}

// Countersunk heads of the face screws, flush with the face
module face_screw_heads() {
    color("#3a3a3a") for (p = face_screws()) translate([p[0], p[1], depth - 1.86]) cylinder(d1 = face_screw_hole, d2 = face_screw_head - 0.2, h = 1.85);
}

module box(explode = 0) {
    // Black outside, as printed
    color("#262626") shell_all();
    translate([0, 0, explode]) inside();
    translate([0, 0, explode * 1.5]) glow();
    color("#1b1b1b") translate([0, 0, explode * 2]) {
        face_all();
        face_screw_heads();
    }
}

module legs() {
    color("#555") for (dx = [-stand_dx, stand_dx]) leg_in_place(dx);
}

module cover_all() {
    color("#1b1b1b") for (h = [0, 1]) cover_body(h);
}

module wall_screws() {
    color("silver") for (dx = [-keyhole_dx / 2, keyhole_dx / 2])
        translate([seam_x + dx, box_h - keyhole_from_top - wall_slide, -6]) {
            cylinder(d = 5, h = 6 + back_t + 1);
            translate([0, 0, back_t + 1]) cylinder(d = 9.5, h = 3);
        }
}

module split_lines() {
    color("red") translate([0, 0, depth + 0.1]) {
        translate([seam_x - 0.4, 0, 0]) cube([0.8, box_h, 0.2]);
        translate([0, split_y - 0.4, 0]) cube([box_w, 0.8, 0.2]);
    }
}

// --- Fit test -----------------------------------------------------------
//
// Small pieces cut from the real parts, printed together on one plate, to check the fits
// before printing the whole box: dovetails and an M5 seam block, the Pi
// posts and the microSD slot, the face with its rivets, the camera and
// microphone holes and a magnet pocket, a grid corner with its lug and
// strip notches, and two letters of the cover.

// [name, part, piece, [x0, y0], [x1, y1]]: each test piece is the region of
// a part, in front-view coordinates, in that part's print orientation.
function test_pieces() = [
    ["grid_corner", "grid", 0, [margin - 9, grid_y - 9], [line_x(2) + 1, line_y(rows - 2) + 1]],
    ["pi_corner", "shell", 0, [0, 0], [100, 60]],
    ["seam_left", "shell", 0, [seam_x - 40, 0], [seam_x + tab_depth + 1, 50]],
    ["seam_right", "shell", 1, [seam_x - 1, 0], [seam_x + 40, 50]],
    ["face_band_left", "face", 0, [seam_x - 45, glass_top - 10], [seam_x + tab_depth + 1, split_y + 1]],
    ["face_band_right", "face", 1, [seam_x - 1, glass_top - 10], [seam_x + 45, split_y + 1]],
    ["face_corner", "face", 0, [0, 0], [100, 60]],
    ["cover_letters", "cover", 0, [cover_x0, cover_y0], [cover_x0 + 75, cover_y0 + 45]],
];

// One test piece in print orientation, its region moved to the origin.
module test_piece(p) {
    x0 = p[3][0];
    y0 = p[3][1];
    region = [p[4][0] - x0, p[4][1] - y0];
    translate([-x0, -y0, 0]) intersection() {
        if (p[1] == "shell") shell(p[2]);
        else if (p[1] == "face") face(p[2]);
        else if (p[1] == "grid") grid(p[2]);
        else if (p[1] == "cover") cover(p[2]);
        translate([x0, y0, -1]) cube([region[0], region[1], depth + 10]);
    }
}

// --- Part selection -------------------------------------------------------

if (part == "shell") shell(piece);
else if (part == "grid") grid(piece);
else if (part == "face") face(piece);
else if (part == "cover") cover(piece);
else if (part == "leg") leg();
else if (part == "test") test_piece(test_pieces()[piece]);
else if (part == "assembly" || part == "front") {
    box();
    if (part == "front") split_lines();
} else if (part == "back") {
    rotate([0, 180, 0]) translate([-box_w, 0, 0]) {
        box();
        legs();
    }
} else if (part == "wall") {
    rotate([90, 0, 0]) {
        color("#d8cfc0") translate([-150, -80, -10]) cube([box_w + 300, box_h + 160, 10]);
        wall_screws();
        box();
    }
} else if (part == "table" || part == "letters_table") {
    color("#a07850") translate([-40, -150, -8]) cube([box_w + 80, 300, 8]);
    rotate([90 - tilt, 0, 0]) {
        box();
        legs();
        if (part == "letters_table") cover_all();
    }
} else if (part == "inside" || part == "inside_3d") {
    color("#d9d9d9") shell_all();
    color("white") for (h = [0, 1]) grid_half(h);
    leds();
    pi();
    uno();
    camera();
    mic();
    jack();
    wagos();
    wiring();
    seam_bolts_drawn();
    color("#888", 0.35) translate([glass_x + lcd_frame_pos[0], glass_y + lcd_frame_pos[1], glass_back - lcd_back_h])
        cube([lcd_frame[0], lcd_frame[1], lcd_back_h]);
} else if (part == "exploded") {
    box(explode = 40);
    legs();
} else if (part == "letters") {
    box();
    cover_all();
} else if (part == "letters_exploded") {
    box();
    translate([0, 0, 60]) cover_all();
}
