// Prototype: one flat box for the mini matrix, to look at before detailing.
//
// The 10 x 6 LED grid, the 7" Raspberry Pi Touch Display v1 under it, the
// Raspberry Pi beside the display and the camera hidden behind one rivet of
// a decorative row, all in one shallow box that hangs flat on a wall. A
// detachable triangle stand slides into the back to stand it on a table.
// No button: the touch screen does its job.
//
// Volumes only, no print details. Sizes in millimetres. Front-view
// coordinates: x to the right, y up, z out of the wall (0 = the wall, the
// front of the face at z = depth).
//
//   openscad -o front.png --render -D 'view="front"' matrix_box.scad

/* [View] */
// front | back | wall | table | exploded
view = "exploded";

/* [Matrix] (as in ../matrix.scad) */
cols = 10;
rows = 6;
pitch = 1000 / 30;
margin = 22;
grid_h = 22;
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
// Metal frame and driver board behind the glass
lcd_back_h = 12;

/* [Raspberry Pi 3B] */
pi_board = [85, 56];
pi_standoff = 3;
pi_board_t = 1.6;
pi_ports_h = 17;

/* [Camera] (OV5647 board, lens behind one rivet) */
cam_board = [25, 24];
cam_lens_from_top = 9.5;
cam_lens_h = 6;
rivet_d = 4;
rivet_pitch = 24;

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
// Print split: down the middle, and across just below the grid
split_y = grid_y - 4;
pi_x = shell_t + 1;
pi_y = glass_y + (lcd_glass[1] - pi_board[1]) / 2;
pi_top = back_t + pi_standoff + pi_board_t + pi_ports_h;

echo(str("Box ", box_w, " x ", box_h, " x ", depth, " mm"));
echo(str("Display window at x ", glass_x, ", y ", glass_y));
echo(str("Camera rivet at x ", cam_x, ", split at y ", split_y));
echo(str("Pi at x ", pi_x, "..", pi_x + pi_board[0], ", top at z ", pi_top));

assert(pi_x + pi_board[0] < glass_x, "The Pi overlaps the display");
assert(pi_top < face_back, "The Pi ports reach the face: deepen the box");
assert(glass_back - lcd_back_h > back_t, "The display does not fit in the depth");
assert(rivet_y - (cam_board[1] - cam_lens_from_top) > glass_top, "Camera board hits the display");
assert(rivet_y + cam_lens_from_top < grid_y, "Camera board hits the grid");

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
        // Power cable out at the bottom
        translate([pi_x + 20, -1, back_t]) cube([14, shell_t + 2, 8]);
    }
}

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
        // Rivets: shallow dimples, one goes through for the camera lens
        for (p = rivets())
            translate([p[0], p[1], abs(p[0] - cam_x) < 1 ? -1 : face_t - 0.8]) cylinder(d = rivet_d, h = face_t + 2);
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

module pi() {
    translate([pi_x, pi_y, back_t + pi_standoff]) {
        color("#1f7a3a") cube([pi_board[0], pi_board[1], pi_board_t]);
        color("#bbb") translate([pi_board[0] - 21, 2, pi_board_t]) cube([21, 52, pi_ports_h]);
        color("#222") translate([20, 10, pi_board_t]) cube([14, 14, 2]);
    }
}

module camera() {
    translate([cam_x - cam_board[0] / 2, rivet_y + cam_lens_from_top - cam_board[1], face_back - cam_lens_h - 1]) {
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

module inside() {
    color("white") grid();
    leds();
    display();
    pi();
    camera();
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
} else if (view == "exploded") {
    box(explode = 35);
    stand();
}
