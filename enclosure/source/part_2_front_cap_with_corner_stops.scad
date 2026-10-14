// Front / outer cap with a centred USB notch and a tighter slip fit.
// All dimensions are in millimetres.

rear_outer_size = 161;
clearance_per_side = 0.2;
cap_plate_thickness = 0.6;
cap_wall_thickness = 2;
cap_skirt_depth = 22;
entry_chamfer = 0.5;

cap_inner_size = rear_outer_size + 2 * clearance_per_side; // 161.4 mm
cap_outer_size = cap_inner_size + 2 * cap_wall_thickness;   // 165.4 mm
cap_height = cap_plate_thickness + cap_skirt_depth;         // 22.6 mm

usb_width = 12;
usb_depth = 7;
usb_center_x = cap_outer_size / 2; // 82.7 mm in this part

module cap_cavity_with_entry_chamfer() {
    union() {
        // Main straight cavity.
        translate([
            cap_wall_thickness,
            cap_wall_thickness,
            cap_plate_thickness
        ])
            cube([
                cap_inner_size,
                cap_inner_size,
                cap_skirt_depth - entry_chamfer + 0.01
            ]);

        // 0.5 mm lead-in chamfer at the open edge.
        hull() {
            translate([
                cap_wall_thickness,
                cap_wall_thickness,
                cap_height - entry_chamfer
            ])
                cube([cap_inner_size, cap_inner_size, 0.01]);

            translate([
                cap_wall_thickness - entry_chamfer,
                cap_wall_thickness - entry_chamfer,
                cap_height
            ])
                cube([
                    cap_inner_size + 2 * entry_chamfer,
                    cap_inner_size + 2 * entry_chamfer,
                    0.01
                ]);
        }
    }
}

module original_cap() {
 difference() {
    cube([cap_outer_size, cap_outer_size, cap_height]);
    cap_cavity_with_entry_chamfer();

    // Matching U-shaped USB opening on the bottom/front wall.
    translate([
        usb_center_x - usb_width / 2,
        -0.1,
        cap_height - usb_depth
    ])
        cube([usb_width, cap_wall_thickness + 0.2, usb_depth + 0.1]);
}

}

stop_width = 1.5;
stop_rise = 10.0;
stop_top_z = cap_plate_thickness + stop_rise; // 10.6
rear_insertion = cap_height - stop_top_z; // 12.0
assert(stop_rise > 0);
module corner_stops() {
    for (x = [cap_wall_thickness, cap_outer_size-cap_wall_thickness-stop_width])
        for (y = [cap_wall_thickness, cap_outer_size-cap_wall_thickness-stop_width])
            translate([x,y,cap_plate_thickness])
                cube([stop_width,stop_width,stop_rise]);
}
union() {
    original_cap();
    corner_stops();
}
