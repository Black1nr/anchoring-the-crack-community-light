#!/usr/bin/env python3
"""Generate the final front-cap SCAD/STL with four 10 mm corner stops."""

import os
import shutil
import subprocess
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parent
ENCLOSURE_DIR = SOURCE_DIR.parent
PRINTABLE_DIR = ENCLOSURE_DIR / "printable"
ASSEMBLY_DIR = ENCLOSURE_DIR / "assembly"

STOP_WIDTH = 1.5
STOP_HEIGHT = 10.0


base_path = SOURCE_DIR / "part_2_front_cap_with_usb.scad"
base = base_path.read_text(encoding="utf-8")
separator = "\ndifference() {"
if separator not in base:
    raise RuntimeError(f"Could not locate the cap body in {base_path.name}")

params, body = base.split(separator, 1)
scad = params + "\nmodule original_cap() {\n difference() {" + body + "\n}\n"
scad += f"""
stop_width = {STOP_WIDTH};
stop_rise = {STOP_HEIGHT};
stop_top_z = cap_plate_thickness + stop_rise; // 10.6
rear_insertion = cap_height - stop_top_z; // 12.0
assert(stop_rise > 0);
module corner_stops() {{
    for (x = [cap_wall_thickness, cap_outer_size-cap_wall_thickness-stop_width])
        for (y = [cap_wall_thickness, cap_outer_size-cap_wall_thickness-stop_width])
            translate([x,y,cap_plate_thickness])
                cube([stop_width,stop_width,stop_rise]);
}}
union() {{
    original_cap();
    corner_stops();
}}
"""

scad_path = SOURCE_DIR / "part_2_front_cap_with_corner_stops.scad"
stl_path = PRINTABLE_DIR / "part_2_front_cap_with_corner_stops.stl"
assembly_path = ASSEMBLY_DIR / "assembly_fit_check_final.scad"

scad_path.write_text(scad, encoding="utf-8")
PRINTABLE_DIR.mkdir(parents=True, exist_ok=True)
ASSEMBLY_DIR.mkdir(parents=True, exist_ok=True)

openscad = (
    os.environ.get("OPENSCAD")
    or shutil.which("openscad")
    or "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
)
if not Path(openscad).exists():
    raise FileNotFoundError(
        "OpenSCAD was not found. Install it or set the OPENSCAD environment variable."
    )

subprocess.run(
    [openscad, "-o", str(stl_path), str(scad_path)],
    check=True,
)

assembly_path.write_text(
    """// Units: mm. Cap floor at Z=0; rear base rests at Z=10.6.
exploded_gap = 0;

color("Orange", 0.65)
    import("../printable/part_2_front_cap_with_corner_stops.stl", convexity=10);

color("LightSteelBlue")
    translate([2.2, 2.2, 10.6 + exploded_gap])
        import("../printable/part_1_rear_with_openings.stl", convexity=10);
""",
    encoding="utf-8",
)

print(
    "Stops rise 10 mm above the inner floor; rear occupies Z=10.6..21.8; "
    "cap rim is Z=22.6."
)
