// Prototype: one flat box for the mini matrix, to look at before detailing.
//
// The 10 x 6 LED grid, the 7" Raspberry Pi Touch Display v1 under it, the
// Raspberry Pi beside the display and the camera hidden behind one rivet of
// a decorative row, all in one shallow box that hangs flat on a wall. A
// detachable triangle stand slides into the back to stand it on a table.
// No button: the touch screen does its job.
//
// A letters cover can sit on top of the grid, held by magnets, to try the
// word clock face on the small matrix: stencil letters over the cells,
// swapped without tools.
//
// Volumes only, no print details. Sizes in millimetres. Front-view
// coordinates: x to the right, y up, z out of the wall (0 = the wall, the
// front of the face at z = depth).
//
//   openscad -o front.png --render -D 'view="front"' matrix_box.scad

/* [View] */
// front | back | wall | table | exploded | letters | letters_exploded | letters_table |
// inside | inside_3d
view = "exploded";

/* [Matrix] (as in ../matrix.scad) */
cols = 10;
rows = 6;
pitch = 1000 / 30;
margin = 22;
// Taller than the 22 mm of today's matrix: the box is 35 mm deep for the
// Pi, and taller walls spread the light more evenly
grid_h = 30;
wall_t = 1.2;
paper_t = 0.3;

/* [Box] */
shell_t = 2.4;
back_t = 2.4;
face_t = 2.4;
corner_r = 6;
// Margin below the display, and the band between the display and the grid
bottom_margin = 20;
band_h = 30;

/* [Display] (Touch Display v1, as in ../wordclock.scad) */
lcd_glass = [192.96, 110.76];
lcd_area = [154.08, 85.92];
lcd_area_top = 11.41;
lcd_frame = [164.9, 100.6];
lcd_frame_pos = [12.54, 3.53];
lcd_t = 6;
// Metal frame behind the glass, with the four M3 holes on its back, and the
// driver board below it
lcd_frame_h = 5;
lcd_back_h = 12;
// M3 holes on the back frame, from its bottom-left corner
lcd_m3 = [[20, 20], [146.2, 20], [20, 85.65], [146.2, 85.65]];
display_post_d = 7;

/* [Raspberry Pi 3B] */
// Upright, left of the display: microSD card down (reached through a slot in
// the bottom wall), USB and Ethernet up, GPIO header on the right.
pi_board = [56, 85];
pi_holes = [[3.5, 3.5], [52.5, 3.5], [3.5, 61.5], [52.5, 61.5]];
pi_standoff = 3;
pi_board_t = 1.6;
pi_ports_h = 16;
// Gap to the left wall (air and the HDMI side) and to the bottom wall
pi_gap = [8, 5];
sd_slot = [16, 5];

/* [Camera] (OV5647 board, lens behind one rivet) */
cam_board = [25, 24];
// M2 holes on 21 x 12.5 mm, 2 mm below the top edge
cam_holes = [21, 12.5];
cam_hole_top = 2;
cam_lens_from_top = 9.5;
cam_lens_h = 6;
cam_post_d = 5;
rivet_d = 4;
rivet_pitch = 24;

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
// Border of the cover around the grid, and its corner radius
cover_border = 9;
cover_r = 4;
// 5 x 2 mm neodymium magnets: one in the face, one in the cover, at each
// corner of the grid and in the middle of each side
magnet_d = 5;
magnet_h = 2;

/* [Power and wiring] */
// Panel-mount 5.5 x 2.1 mm DC jack in the bottom wall, and two lever
// connectors (WAGO 221-413) that share the 5 V and the ground
jack_d = 11.4;
jack_x = 82;
wago = [20.2, 13.1, 8.3];
// Ventilation slots: in the bottom wall under the Pi, and high in the left
// wall, so warm air rises out
vent = [3, 18];
// Magnets that hold the face on the box: posts in the corners and along
// the sides
face_magnet_post = 9;

/* [Wall and table] */
// Keyholes in the top margin for two M5 wall screws
keyhole_dx = 100;
screw_head_d = 9.5;
// Table stand: two triangles that slide into slots in the back. The box
// rests on its bottom back edge and on the feet of the triangles.
tilt = 15;
stand_y0 = 25;
stand_y1 = 125;
// How far the feet reach behind the box
stand_reach = 100;
stand_t = 4;
stand_dx = 120;

use <../fonts/KarlaBoldStencil.ttf>

$fn = 40;

// --- Derived sizes ---------------------------------------------------------

box_w = cols * pitch + 2 * margin;
grid_w = cols * pitch;
grid_hh = rows * pitch;
glass_x = (box_w - lcd_glass[0]) / 2;
glass_y = bottom_margin;
glass_top = glass_y + lcd_glass[1];
rivet_y = glass_top + band_h / 2;
grid_y = glass_top + band_h;
box_h = grid_y + grid_hh + margin;
// Face back and front
face_back = back_t + grid_h + paper_t;
depth = face_back + face_t;
glass_back = depth - lcd_t;
// Camera behind the rivet just right of the middle, clear of the seam
cam_x = let(r = rivets()) [for (p = r) if (p[0] > box_w / 2 + 1) p[0]][0];
cam_x0 = cam_x - cam_board[0] / 2;
cam_y0 = rivet_y + cam_lens_from_top - cam_board[1];
cam_z = face_back - cam_lens_h - 1;
glass_origin = [glass_x, glass_y];
frame_back = glass_back - lcd_frame_h;
function display_holes() = [for (h = lcd_m3) glass_origin + lcd_frame_pos + h];
// Print split: down the middle, and across just below the grid
split_y = grid_y - 4;
pi_x = shell_t + pi_gap[0];
pi_y = shell_t + pi_gap[1];
pi_z = back_t + pi_standoff;
pi_top = pi_z + pi_board_t + pi_ports_h;
wago_xy = [pi_x + pi_board[0] + 6, shell_t + 22];

echo(str("Box ", box_w, " x ", box_h, " x ", depth, " mm"));
echo(str("Display window at x ", glass_x, ", y ", glass_y));
echo(str("Camera rivet at x ", cam_x, ", split at y ", split_y));
echo(str("Pi at x ", pi_x, "..", pi_x + pi_board[0], ", y ", pi_y, "..", pi_y + pi_board[1]));
echo(str("Room above the Pi ports: ", face_back - pi_top, " mm"));
echo(str("Room under the display driver board: ", glass_back - lcd_back_h - back_t, " mm"));
echo(str("Display posts: ", frame_back - back_t, " mm; camera posts: ", cam_z - back_t, " mm"));

assert(pi_x + pi_board[0] < glass_x, "The Pi overlaps the display");
assert(face_back - pi_top >= 8, "Less than 8 mm above the Pi ports: deepen the box");
assert(glass_back - lcd_back_h - back_t >= 8, "No room for the ribbon under the display");
assert(pi_y + pi_board[1] + 3 < grid_y, "The Pi reaches the grid");
assert(wago_xy[0] + wago[0] < glass_x + lcd_frame_pos[0], "The connectors reach the display frame");
assert(rivet_y - (cam_board[1] - cam_lens_from_top) > glass_top, "Camera board hits the display");
assert(rivet_y + cam_lens_from_top < grid_y, "Camera board hits the grid");

font_size = cap_height / cap_ratio;
baseline = -(accent_ratio - descent_ratio) * font_size / 2;
cover_x0 = margin - cover_border;
cover_y0 = grid_y - cover_border;
cover_size = [grid_w + 2 * cover_border, grid_hh + 2 * cover_border];
function magnets() = let(m = cover_border / 2) [
    for (x = [cover_x0 + m, box_w / 2, cover_x0 + cover_size[0] - m],
         y = [cover_y0 + m, grid_y + grid_hh / 2, cover_y0 + cover_size[1] - m])
        if (!(x == box_w / 2 && y == grid_y + grid_hh / 2)) [x, y]
];

assert(cover_y0 - rivet_y > rivet_d, "The letters cover hides the camera rivet");

// --- Parts -------------------------------------------------------------------

module rounded(size, r) {
    offset(r) offset(-r) square(size);
}

function rivets() = let(n = floor((box_w - 2 * margin) / rivet_pitch))
    [for (i = [0:n]) [margin + i * (box_w - 2 * margin) / n, rivet_y]];

// Shell: back plate and side walls, the LED strip lies on the back plate.
module shell() {
    difference() {
        union() {
            linear_extrude(back_t) rounded([box_w, box_h], corner_r);
            linear_extrude(face_back) difference() {
                rounded([box_w, box_h], corner_r);
                offset(-shell_t) rounded([box_w, box_h], corner_r);
            }
        }
        // Keyholes for the wall screws, in the top margin
        for (dx = [-keyhole_dx / 2, keyhole_dx / 2]) translate([box_w / 2 + dx, box_h - margin / 2, -1]) {
            cylinder(d = screw_head_d + 1, h = back_t + 2);
            hull() for (dy = [0, 8]) translate([0, dy - 8, 0]) cylinder(d = 5.6, h = back_t + 2);
        }
        // Slots for the table stand
        for (dx = [-stand_dx / 2, stand_dx / 2])
            translate([box_w / 2 + dx - stand_t / 2 - 0.2, stand_y0, -1]) cube([stand_t + 0.4, stand_y1 - stand_y0, back_t - 0.8 + 1]);
        // DC jack in the bottom wall
        translate([jack_x, -1, depth / 2 - 3]) rotate([-90, 0, 0]) cylinder(d = jack_d, h = shell_t + 2);
        // microSD slot in the bottom wall, under the card
        translate([pi_x + pi_board[0] / 2 - sd_slot[0] / 2, -1, pi_z - 3]) cube([sd_slot[0], shell_t + 2, sd_slot[1]]);
        // Vents: bottom wall under the Pi, left wall high beside it
        for (i = [0:3]) translate([pi_x + 4 + i * 9, -1, back_t + 6]) cube([vent[0], shell_t + 2, vent[1]]);
        for (i = [0:3]) translate([-1, pi_y + 50 + i * 9, back_t + 6]) cube([shell_t + 2, vent[0], vent[1]]);
        // Countersunk M3 screws from the back into the display frame
        for (h = display_holes()) translate([h[0], h[1], -1]) cylinder(d = 3.4, h = back_t + 2);
    }
    // Posts: display (M3 from the back), camera (M2), Pi standoffs
    for (h = display_holes()) translate([h[0], h[1], 0]) difference() {
        cylinder(d = display_post_d, h = frame_back);
        translate([0, 0, -1]) cylinder(d = 3.4, h = frame_back + 2);
    }
    for (dx = [0, cam_holes[0]], dy = [0, cam_holes[1]])
        translate([cam_x0 + (cam_board[0] - cam_holes[0]) / 2 + dx, cam_y0 + cam_board[1] - cam_hole_top - dy, 0])
            cylinder(d = cam_post_d, h = cam_z);
    for (h = pi_holes) translate([pi_x + h[0], pi_y + h[1], 0]) cylinder(d = 6, h = pi_z);
    // Magnet posts for the face, in the corners and along the sides
    for (p = face_magnets()) translate([p[0], p[1], 0]) cylinder(d = face_magnet_post, h = face_back);
}

function face_magnets() = let(m = shell_t + face_magnet_post / 2) [
    for (x = [m, box_w / 2, box_w - m], y = [m, glass_top + band_h / 2 - 0.01, box_h - m])
        if (!(x == box_w / 2 && y != m && y != box_h - m)) [x, y]
];

module grid() {
    translate([margin, grid_y, back_t]) linear_extrude(grid_h) difference() {
        square([grid_w, grid_hh]);
        for (c = [0:cols - 1], r = [0:rows - 1])
            translate([c * pitch + wall_t / 2, r * pitch + wall_t / 2]) square(pitch - wall_t);
    }
}

module leds() {
    for (c = [0:cols - 1], r = [0:rows - 1])
        translate([margin + (c + 0.5) * pitch, grid_y + (r + 0.5) * pitch, back_t]) {
            color("#e8e8e8") translate([-2.5, -2.5, 0]) cube([5, 5, 1.6]);
            color(hsv(r * 0.12 + c * 0.03)) translate([0, 0, 1.6]) cylinder(d = 3, h = 0.6);
        }
}

function hsv(h) = let(k = [for (n = [5, 3, 1]) (n + (h % 1) * 6) % 6])
    [for (v = k) 1 - max(0, min(v, 4 - v, 1))];

// The tracing paper, each cell glowing in the colour of its LED.
module glow() {
    for (c = [0:cols - 1], r = [0:rows - 1])
        color([for (v = hsv(r * 0.12 + c * 0.03)) 0.35 + 0.65 * v])
            translate([margin + c * pitch + wall_t / 2, grid_y + r * pitch + wall_t / 2, back_t + grid_h - 1.5])
                cube([pitch - wall_t, pitch - wall_t, 0.5]);
}

module face() {
    translate([0, 0, face_back]) difference() {
        linear_extrude(face_t) rounded([box_w, box_h], corner_r);
        // One window per cell
        for (c = [0:cols - 1], r = [0:rows - 1])
            translate([margin + c * pitch + 1.5, grid_y + r * pitch + 1.5, -1])
                linear_extrude(face_t + 2) rounded([pitch - 3, pitch - 3], 1.5);
        // Display glass window
        translate([glass_x - 0.2, glass_y - 0.2, -1]) cube([lcd_glass[0] + 0.4, lcd_glass[1] + 0.4, face_t + 2]);
        // Magnet pockets for the letters cover
        for (p = magnets()) translate([p[0], p[1], face_t - magnet_h]) cylinder(d = magnet_d + 0.2, h = magnet_h + 1);
        // Rivets: shallow dimples, one goes through for the camera lens
        for (p = rivets())
            translate([p[0], p[1], abs(p[0] - cam_x) < 1 ? -1 : face_t - 0.8]) cylinder(d = rivet_d, h = face_t + 2);
    }
}

// Letters cover in place on the face: stencil letters through, one per
// cell, row 0 at the top.
module letters_cover() {
    translate([0, 0, depth]) difference() {
        translate([cover_x0, cover_y0, 0]) linear_extrude(cover_t) rounded(cover_size, cover_r);
        for (r = [0:rows - 1], c = [0:cols - 1])
            let(ch = letters[r][c]) if (ch != " ")
                translate([margin + (c + 0.5) * pitch, grid_y + (rows - r - 0.5) * pitch + baseline, -1])
                    linear_extrude(cover_t + 2)
                        text(ch, size = font_size, font = font, halign = "center", valign = "baseline");
        for (p = magnets()) translate([p[0], p[1], -0.01]) cylinder(d = magnet_d + 0.2, h = magnet_h);
    }
}

// Magnet pairs: in pockets at the front of the face and the back of the cover.
module magnet_pairs(gap = 0) {
    color("silver") for (p = magnets()) translate([p[0], p[1], 0]) {
        translate([0, 0, depth - magnet_h]) cylinder(d = magnet_d, h = magnet_h);
        translate([0, 0, depth + gap]) cylinder(d = magnet_d, h = magnet_h);
    }
}

module display() {
    translate([glass_x, glass_y, glass_back]) {
        color("#111") cube([lcd_glass[0], lcd_glass[1], lcd_t]);
        color("#3a5f8a") translate([(lcd_glass[0] - lcd_area[0]) / 2, lcd_glass[1] - lcd_area_top - lcd_area[1], lcd_t])
            cube([lcd_area[0], lcd_area[1], 0.1]);
        color("#888") translate([lcd_frame_pos[0], lcd_frame_pos[1], -lcd_back_h]) cube([lcd_frame[0], lcd_frame[1], lcd_back_h]);
    }
}

// Raspberry Pi 3B upright: SD card at the bottom, USB and Ethernet at the
// top, GPIO header on the right edge, DSI and CSI connectors on the left.
module pi() {
    translate([pi_x, pi_y, pi_z]) {
        color("#1f7a3a") cube([pi_board[0], pi_board[1], pi_board_t]);
        // USB and Ethernet stack, sticking out at the top
        color("#bbb") translate([2, pi_board[1] - 19, pi_board_t]) cube([52, 21, pi_ports_h]);
        // GPIO header, pin 1 at the bottom
        color("#222") translate([pi_board[0] - 6, 7, pi_board_t]) cube([5, 51, 8.5]);
        // DSI (display) at the bottom, CSI (camera) on the left
        color("#eee") translate([12, 2, pi_board_t]) cube([22, 4, 5.5]);
        color("#eee") translate([2, 44, pi_board_t]) cube([4, 22, 5.5]);
        color("#333") translate([18, 25, pi_board_t]) cube([14, 14, 1.5]);
        // microSD card, under the board at the bottom edge
        color("#c33") translate([pi_board[0] / 2 - 6, -3, -1.5]) cube([12, 15, 1.4]);
    }
}

module jack() {
    color("#222") translate([jack_x, shell_t, depth / 2 - 3]) rotate([-90, 0, 0]) {
        cylinder(d = jack_d - 0.4, h = 4);
        translate([0, 0, 4]) cylinder(d = 8, h = 12);
    }
}

module wagos() {
    for (i = [0, 1]) translate([wago_xy[0], wago_xy[1] + i * (wago[1] + 3), back_t]) {
        color("#e8e8e8") cube(wago);
        color("#f08a00") for (k = [0:2]) translate([2 + k * 6.5, 2, wago[2]]) cube([4, wago[1] - 4, 1.5]);
    }
}

// A cable through a list of points, as a chain of rounded segments.
module cable(points, c, d = 2) {
    color(c) for (i = [0:len(points) - 2]) hull() {
        translate(points[i]) sphere(d = d, $fn = 12);
        translate(points[i + 1]) sphere(d = d, $fn = 12);
    }
}

// Flat ribbon cable (DSI, CSI), drawn as a thick white line.
module ribbon(points) {
    cable(points, "#f2f2f2", 3.5);
}

// The strip starts at the bottom-left cell: run the show with --rotate
// --mirror. Power and data come up the left side of the band.
strip_in = [margin + pitch / 2, grid_y + pitch / 2, back_t + 1];
pin = function(n) [pi_x + pi_board[0] - 3.5 - (n % 2 == 0 ? 0 : 2.5), pi_y + 7 + 2.54 * floor((n - 1) / 2), pi_z + 10];

module wiring() {
    w = [wago_xy[0] + 4, wago_xy[1] + 4, back_t + wago[2]];
    g = [wago_xy[0] + 4, wago_xy[1] + wago[1] + 7, back_t + wago[2]];
    jk = [jack_x, shell_t + 16, depth / 2 - 3];
    // Jack to the connectors
    cable([jk, [jack_x, w[1], 10], w], "red");
    cable([jk + [2, 0, 0], [jack_x + 2, g[1], 10], g], "black");
    // 5 V and ground to the Pi (pins 2 and 6)
    cable([w + [6, 0, 0], [pin(2)[0] + 8, w[1], 12], [pin(2)[0] + 8, pin(2)[1], 12], pin(2)], "red", 1.4);
    cable([g + [6, 0, 0], [pin(6)[0] + 10, g[1], 12], [pin(6)[0] + 10, pin(6)[1], 12], pin(6)], "black", 1.4);
    // 5 V, ground and data (pin 12) up the left side to the strip input
    up = shell_t + 3;
    cable([w + [12, 0, 0], [w[0] + 12, pi_y + pi_board[1] + 8, 6], [up + 2, pi_y + pi_board[1] + 8, 6], [up + 2, strip_in[1] - 6, 4], strip_in + [-6, -4, 0]], "red");
    cable([g + [12, 0, 0], [g[0] + 15, pi_y + pi_board[1] + 11, 6], [up + 4.5, pi_y + pi_board[1] + 11, 6], [up + 4.5, strip_in[1] - 3, 4], strip_in + [-6, 0, 0]], "black");
    cable([pin(12), [pin(12)[0] + 3, pin(12)[1], 14], [pin(12)[0] + 3, pi_y + pi_board[1] + 14, 8], [up + 7, pi_y + pi_board[1] + 14, 8], [up + 7, strip_in[1], 4], strip_in + [-6, 4, 0]], "green", 1.4);
    // 5 V and ground to the display driver board
    drv = [glass_x + lcd_glass[0] / 2, glass_y + 30, glass_back - lcd_back_h];
    cable([w + [18, 0, 0], [w[0] + 30, w[1], 8], [drv[0] - 20, drv[1], 8], drv + [-20, 0, 0]], "red", 1.4);
    cable([g + [18, 0, 0], [g[0] + 30, g[1], 8], [drv[0] - 20, drv[1] + 4, 8], drv + [-20, 4, 0]], "black", 1.4);
    // DSI ribbon: Pi bottom connector, under the display, to the driver board
    dsi = [pi_x + 23, pi_y + 6, pi_z + 7];
    ribbon([dsi, [dsi[0], dsi[1], 8], [drv[0], dsi[1], 8], drv + [0, -5, 0]]);
    // CSI ribbon: Pi left connector, up the left side and across the band
    csi = [pi_x + 4, pi_y + 55, pi_z + 4];
    cam = [cam_x, cam_y0 + 2, cam_z];
    ribbon([csi, [shell_t + 3, csi[1], 10], [shell_t + 3, rivet_y - 6, 14], [cam[0] - 20, rivet_y - 6, 18], cam + [0, 0, -1]]);
}

module camera() {
    translate([cam_x0, cam_y0, cam_z]) {
        color("#2a6e2a") cube([cam_board[0], cam_board[1], 1]);
        color("#111") translate([cam_board[0] / 2, cam_board[1] - cam_lens_from_top, 1]) cylinder(d = 8, h = cam_lens_h);
    }
}

// Table plane in box coordinates, through the bottom back edge: the box
// stands leaning back by `tilt`, so up is (0, cos(tilt), sin(tilt)).
function table_y(z) = -z * tan(tilt);

// Triangle leg in the yz plane: one edge on the back of the box, the foot
// on the table behind it.
module stand_leg() {
    foot = [table_y(-stand_reach), -stand_reach];
    rotate([90, 0, 90]) linear_extrude(stand_t, center = true)
        polygon([[stand_y0, 0], [stand_y1, 0], foot]);
}

module stand() {
    color("#555") for (dx = [-stand_dx / 2, stand_dx / 2]) translate([box_w / 2 + dx, 0, 0]) stand_leg();
}

module wall_screws() {
    color("silver") for (dx = [-keyhole_dx / 2, keyhole_dx / 2])
        translate([box_w / 2 + dx, box_h - margin / 2 - 8, -6]) {
            cylinder(d = 5, h = 6 + back_t + 1);
            translate([0, 0, back_t + 1]) cylinder(d = screw_head_d, h = 3);
        }
}

module split_lines() {
    color("red") translate([0, 0, depth + 0.1]) {
        translate([box_w / 2 - 0.4, 0, 0]) cube([0.8, box_h, 0.2]);
        translate([0, split_y - 0.4, 0]) cube([box_w, 0.8, 0.2]);
    }
}

module inside(cables = false) {
    color("white") grid();
    leds();
    display();
    pi();
    camera();
    jack();
    wagos();
    if (cables) wiring();
}

module box(explode = 0) {
    color("#d9d9d9") shell();
    translate([0, 0, explode]) inside();
    translate([0, 0, explode * 1.5]) glow();
    color("#1b1b1b") translate([0, 0, explode * 2]) face();
}

// --- Views -------------------------------------------------------------------

if (view == "front") {
    box();
    split_lines();
} else if (view == "back") {
    rotate([0, 180, 0]) translate([-box_w, 0, 0]) {
        box();
        stand();
    }
} else if (view == "wall") {
    // Hanging on the wall: box y up, the wall behind it.
    rotate([90, 0, 0]) {
        color("#d8cfc0") translate([-150, -80, -10]) cube([box_w + 300, box_h + 160, 10]);
        wall_screws();
        box();
    }
} else if (view == "table") {
    // Standing on the table, leaning back: box y up, box z towards the viewer.
    color("#a07850") translate([-40, -150, -8]) cube([box_w + 80, 300, 8]);
    rotate([90 - tilt, 0, 0]) {
        box();
        stand();
    }
} else if (view == "letters") {
    box();
    color("#1b1b1b") letters_cover();
} else if (view == "letters_exploded") {
    box();
    magnet_pairs(gap = 60);
    color("#1b1b1b") translate([0, 0, 60]) letters_cover();
} else if (view == "letters_table") {
    color("#a07850") translate([-40, -150, -8]) cube([box_w + 80, 300, 8]);
    rotate([90 - tilt, 0, 0]) {
        box();
        stand();
        color("#1b1b1b") letters_cover();
    }
} else if (view == "inside" || view == "inside_3d") {
    // Face and display off, to see the parts and the wiring
    color("#d9d9d9") shell();
    color("white") grid();
    leds();
    pi();
    camera();
    jack();
    wagos();
    wiring();
    color("#888", 0.35) translate([glass_x + lcd_frame_pos[0], glass_y + lcd_frame_pos[1], glass_back - lcd_back_h])
        cube([lcd_frame[0], lcd_frame[1], lcd_back_h]);
} else if (view == "exploded") {
    box(explode = 35);
    stand();
}
