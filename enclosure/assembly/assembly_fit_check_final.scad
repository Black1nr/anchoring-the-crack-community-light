// Final assembly check. Set exploded_gap to 0 for the seated fit.

exploded_gap = 8;

rear_outer_size = 161;
cap_outer_size = 165.4;
cap_height = 22.6;
cap_overhang = (cap_outer_size - rear_outer_size) / 2; // 2.2 mm

color("LightSteelBlue")
    import("part_1_rear_with_openings.stl", convexity=10);

// Rotate the print-oriented cap for assembly while keeping both USB notches
// on the same physical side.
color("Orange", 0.72)
    translate([
        rear_outer_size + cap_overhang,
        -cap_overhang,
        cap_height + exploded_gap
    ])
        rotate([0, 180, 0])
            import("part_2_front_cap_with_usb.stl", convexity=10);
