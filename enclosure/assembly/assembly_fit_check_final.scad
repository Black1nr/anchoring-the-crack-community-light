// Units: mm. Cap floor at Z=0; rear base rests at Z=10.6.
exploded_gap = 0;

color("Orange", 0.65)
    import("../printable/part_2_front_cap_with_corner_stops.stl", convexity=10);

color("LightSteelBlue")
    translate([2.2, 2.2, 10.6 + exploded_gap])
        import("../printable/part_1_rear_with_openings.stl", convexity=10);
