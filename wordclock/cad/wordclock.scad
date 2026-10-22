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

/* [Part selection] */
// face | letters | diffuser | grid | pibox | pilid | assembly
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
// Opaque black layer with letter-shaped holes
face_t = 1.6;
// White backing layer that diffuses light and holds the letter islands
diffuser_t = 0.6;
font = "Liberation Sans:style=Bold";
// Cap height of the letters
cap_height = 18;

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
box_inner = [72, 60, 20];
box_wall = 2;

/* [Letters] */
rows = [
    "ITISASCTIMEQHXQ ",
];

$fn = 48;

panel_size = inner_size - clearance;
border = (panel_size - cells * pitch) / 2;
// Liberation Sans Bold capitals are ~0.955 of the font size
font_size = cap_height / 0.955;

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
            translate([cell_x(c), cell_y(r) - cap_height / 2])
                text(ch, size = font_size, font = font, halign = "center", valign = "baseline");
    }
}

// Parts printed face-down are mirrored so that the text reads correctly
// once the printed tile is flipped over.
module face_down() {
    mirror([1, 0, 0]) children();
}

module face_2d(t) {
    difference() {
        tile_rect(t);
        letters_2d(t);
    }
}

module letter_fill_2d(t) {
    intersection() {
        tile_rect(t);
        letters_2d(t);
    }
}

module face(t) {
    face_down() linear_extrude(face_t) face_2d(t);
}

module letter_fill(t) {
    face_down() linear_extrude(face_t) letter_fill_2d(t);
}

module diffuser(t) {
    face_down() translate([0, 0, face_t]) linear_extrude(diffuser_t) tile_rect(t);
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

module rounded_box(size, r = 3) {
    linear_extrude(size[2])
        offset(r) offset(-r) square([size[0], size[1]]);
}

module pibox() {
    outer = [box_inner[0] + 2 * box_wall, box_inner[1] + 2 * box_wall, box_inner[2] + box_wall];
    pi_origin = [box_wall + (box_inner[0] - pi_size[0]) / 2, box_wall + box_inner[1] - pi_size[1] - 3];
    standoff_h = 4;

    difference() {
        rounded_box(outer);
        translate([box_wall, box_wall, box_wall]) rounded_box([box_inner[0], box_inner[1], box_inner[2] + 1], 1);
        // Cable slot for the 5V input and the 3-wire LED cable
        translate([-1, box_wall + 6, box_wall + 2]) cube([box_wall + 2, 14, 8]);
        // Cable slot towards the LED matrix, through the frame back board
        translate([outer[0] / 2 - 10, box_wall + 4, -1]) cube([20, 10, box_wall + 2]);
        // Countersunk holes to screw the box onto the frame back board,
        // below the Raspberry Pi area so the screw heads stay reachable
        for (x = [8, outer[0] - 8])
            translate([x, 8, 0]) {
                translate([0, 0, -1]) cylinder(d = 3.4, h = box_wall + 2);
                translate([0, 0, box_wall - 1.6]) cylinder(d1 = 3.4, d2 = 6.6, h = 1.61);
            }
    }
    // Standoffs for M2.5 self-tapping screws
    for (dx = [0, pi_holes[0]], dy = [0, pi_holes[1]])
        translate([pi_origin[0] + 3.5 + dx, pi_origin[1] + 3.5 + dy, box_wall])
            difference() {
                cylinder(d = 5.5, h = standoff_h);
                cylinder(d = 2.2, h = standoff_h + 1);
            }
}

module pilid() {
    lip = 3;
    tol = 0.3;
    outer = [box_inner[0] + 2 * box_wall, box_inner[1] + 2 * box_wall];
    difference() {
        rounded_box([outer[0], outer[1], box_wall]);
        // Ventilation slots
        for (i = [0:5])
            translate([outer[0] / 2 - 25, 14 + i * 7, -1]) cube([50, 2.5, box_wall + 2]);
    }
    translate([box_wall + tol, box_wall + tol, box_wall])
        difference() {
            rounded_box([box_inner[0] - 2 * tol, box_inner[1] - 2 * tol, lip], 1);
            translate([1.2, 1.2, -1]) rounded_box([box_inner[0] - 2 * tol - 2.4, box_inner[1] - 2 * tol - 2.4, lip + 2], 1);
        }
}

// --- Assembly view ----------------------------------------------------------

// Whole clock seen from the front (+z), with the layers pulled apart by
// `explode`. For viewing only: use the individual parts for printing.
module assembly() {
    tiles = [[0, 8, 0, 8], [8, 16, 0, 8], [0, 8, 8, 16], [8, 16, 8, 16]];
    grid_top = back_t + grid_h;
    diffuser_z = grid_top + explode;
    face_z = diffuser_z + diffuser_t + explode / 2;

    for (t = tiles) {
        color("white") grid(t);
        color("ivory") translate([0, 0, diffuser_z]) linear_extrude(diffuser_t) tile_rect(t);
        translate([0, 0, face_z]) {
            color("#1a1a1a") linear_extrude(face_t) face_2d(t);
            color("gold") linear_extrude(face_t) letter_fill_2d(t);
        }
    }
    // Back board of the frame, behind the pixel tails
    back_z = -18;
    color("dimgray")
        translate([panel_size / 2 + 38, panel_size - 40, back_z - explode]) rotate([180, 0, 0]) pibox();
    if (show_frame) {
        frame_wall = (500 - inner_size) / 2;
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
else if (part == "letters") letter_fill(tile);
else if (part == "diffuser") diffuser(tile);
else if (part == "grid") grid(tile);
else if (part == "pibox") pibox();
else if (part == "pilid") pilid();
else if (part == "assembly") assembly();
else assert(false, str("Unknown part: ", part));
