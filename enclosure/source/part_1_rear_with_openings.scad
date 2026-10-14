// Rear / inner part with USB notch and LED wiring opening.
// All dimensions are in millimetres.

outer_size = 161;
base_thickness = 1.2;
wall_thickness = 2;
wall_rise = 10;
overall_height = base_thickness + wall_rise;

usb_width = 12;
usb_depth = 7;
usb_center_x = outer_size / 2; // 80.5 mm

led_hole_size = 18;
led_corner_radius = 1;
led_center_x = 125;
led_center_y = 39; // measured from the USB-notch / bottom edge

module rounded_square_hole(size, radius, height) {
    linear_extrude(height=height)
        offset(r=radius)
            square([size - 2 * radius, size - 2 * radius], center=true);
}

difference() {
    union() {
        cube([outer_size, outer_size, base_thickness]);

        translate([0, 0, base_thickness])
            difference() {
                cube([outer_size, outer_size, wall_rise]);
                translate([wall_thickness, wall_thickness, 0])
                    cube([
                        outer_size - 2 * wall_thickness,
                        outer_size - 2 * wall_thickness,
                        wall_rise
                    ]);
            }
    }

    // U-shaped USB opening, centred on the bottom/front wall.
    translate([
        usb_center_x - usb_width / 2,
        -0.1,
        overall_height - usb_depth
    ])
        cube([usb_width, wall_thickness + 0.2, usb_depth + 0.1]);

    // Through-hole exposing the LED 5V / GND / DIN pad and its wires.
    translate([led_center_x, led_center_y, -0.1])
        rounded_square_hole(
            led_hole_size,
            led_corner_radius,
            base_thickness + 0.2
        );
}
