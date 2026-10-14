#!/usr/bin/env python3
"""Generate watertight STL files for the final 161 mm two-part model."""

from collections import Counter
from math import ceil, sqrt
from pathlib import Path


Point = tuple[float, float, float]
Triangle = tuple[Point, Point, Point]
Cell = tuple[int, int, int]

REAR_OUTER = 161.0
REAR_BASE = 1.2
REAR_WALL = 2.0
REAR_WALL_RISE = 10.0
REAR_HEIGHT = REAR_BASE + REAR_WALL_RISE

USB_WIDTH = 12.0
USB_DEPTH = 7.0
REAR_USB_CENTER_X = REAR_OUTER / 2

LED_SIZE = 18.0
LED_RADIUS = 1.0
LED_CENTER_X = 125.0
LED_CENTER_Y = 39.0

CLEARANCE_PER_SIDE = 0.2
CAP_INNER = REAR_OUTER + 2 * CLEARANCE_PER_SIDE
CAP_WALL = 2.0
CAP_OUTER = CAP_INNER + 2 * CAP_WALL
CAP_PLATE = 0.6
CAP_SKIRT = 22.0
CAP_HEIGHT = CAP_PLATE + CAP_SKIRT
CAP_CHAMFER = 0.5
CAP_USB_CENTER_X = CAP_OUTER / 2


def unique(values: list[float]) -> list[float]:
    return sorted({round(value, 6) for value in values})


def stepped_range(start: float, stop: float, step: float) -> list[float]:
    count = int(round((stop - start) / step))
    return [start + i * step for i in range(count + 1)]


def quad(a: Point, b: Point, c: Point, d: Point) -> list[Triangle]:
    return [(a, b, c), (a, c, d)]


def normal(triangle: Triangle) -> Point:
    a, b, c = triangle
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    n = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    length = sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    return (n[0] / length, n[1] / length, n[2] / length)


def rounded_square_contains(x: float, y: float) -> bool:
    """True inside the 18 mm LED opening with approximately 1 mm corners."""
    straight_half = LED_SIZE / 2 - LED_RADIUS
    dx = max(abs(x - LED_CENTER_X) - straight_half, 0.0)
    dy = max(abs(y - LED_CENTER_Y) - straight_half, 0.0)
    return dx * dx + dy * dy <= LED_RADIUS * LED_RADIUS


def surface_mesh(
    xs: list[float],
    ys: list[float],
    zs: list[float],
    is_solid,
) -> list[Triangle]:
    """Extract a watertight boundary from a conforming rectilinear grid."""
    occupied: set[Cell] = set()
    for ix in range(len(xs) - 1):
        for iy in range(len(ys) - 1):
            for iz in range(len(zs) - 1):
                midpoint = (
                    (xs[ix] + xs[ix + 1]) / 2,
                    (ys[iy] + ys[iy + 1]) / 2,
                    (zs[iz] + zs[iz + 1]) / 2,
                )
                if is_solid(*midpoint):
                    occupied.add((ix, iy, iz))

    triangles: list[Triangle] = []
    for ix, iy, iz in occupied:
        x0, x1 = xs[ix], xs[ix + 1]
        y0, y1 = ys[iy], ys[iy + 1]
        z0, z1 = zs[iz], zs[iz + 1]

        if (ix - 1, iy, iz) not in occupied:
            triangles += quad(
                (x0, y1, z0), (x0, y0, z0),
                (x0, y0, z1), (x0, y1, z1),
            )
        if (ix + 1, iy, iz) not in occupied:
            triangles += quad(
                (x1, y0, z0), (x1, y1, z0),
                (x1, y1, z1), (x1, y0, z1),
            )
        if (ix, iy - 1, iz) not in occupied:
            triangles += quad(
                (x0, y0, z0), (x1, y0, z0),
                (x1, y0, z1), (x0, y0, z1),
            )
        if (ix, iy + 1, iz) not in occupied:
            triangles += quad(
                (x1, y1, z0), (x0, y1, z0),
                (x0, y1, z1), (x1, y1, z1),
            )
        if (ix, iy, iz - 1) not in occupied:
            triangles += quad(
                (x0, y0, z0), (x0, y1, z0),
                (x1, y1, z0), (x1, y0, z0),
            )
        if (ix, iy, iz + 1) not in occupied:
            triangles += quad(
                (x0, y0, z1), (x1, y0, z1),
                (x1, y1, z1), (x0, y1, z1),
            )

    return triangles


def rear_mesh() -> list[Triangle]:
    usb_left = REAR_USB_CENTER_X - USB_WIDTH / 2
    usb_right = REAR_USB_CENTER_X + USB_WIDTH / 2
    led_left = LED_CENTER_X - LED_SIZE / 2
    led_right = LED_CENTER_X + LED_SIZE / 2
    led_bottom = LED_CENTER_Y - LED_SIZE / 2
    led_top = LED_CENTER_Y + LED_SIZE / 2

    corner_x = (
        stepped_range(led_left, led_left + LED_RADIUS, 0.2)
        + stepped_range(led_right - LED_RADIUS, led_right, 0.2)
    )
    corner_y = (
        stepped_range(led_bottom, led_bottom + LED_RADIUS, 0.2)
        + stepped_range(led_top - LED_RADIUS, led_top, 0.2)
    )

    xs = unique([
        0, REAR_WALL, usb_left, usb_right,
        led_left, led_left + LED_RADIUS,
        led_right - LED_RADIUS, led_right,
        REAR_OUTER - REAR_WALL, REAR_OUTER,
        *corner_x,
    ])
    ys = unique([
        0, REAR_WALL,
        led_bottom, led_bottom + LED_RADIUS,
        led_top - LED_RADIUS, led_top,
        REAR_OUTER - REAR_WALL, REAR_OUTER,
        *corner_y,
    ])
    zs = unique([
        0, REAR_BASE,
        REAR_HEIGHT - USB_DEPTH,
        REAR_HEIGHT,
    ])

    def is_solid(x: float, y: float, z: float) -> bool:
        if z < REAR_BASE:
            return not rounded_square_contains(x, y)

        wall = (
            x < REAR_WALL or x > REAR_OUTER - REAR_WALL
            or y < REAR_WALL or y > REAR_OUTER - REAR_WALL
        )
        usb_cut = (
            usb_left < x < usb_right
            and y < REAR_WALL
            and z > REAR_HEIGHT - USB_DEPTH
        )
        return wall and not usb_cut

    return surface_mesh(xs, ys, zs, is_solid)


def cap_mesh() -> list[Triangle]:
    usb_left = CAP_USB_CENTER_X - USB_WIDTH / 2
    usb_right = CAP_USB_CENTER_X + USB_WIDTH / 2
    chamfer_offsets = stepped_range(
        CAP_WALL - CAP_CHAMFER,
        CAP_WALL,
        0.1,
    )
    chamfer_start = CAP_HEIGHT - CAP_CHAMFER

    xs = unique([
        0, *chamfer_offsets,
        usb_left, usb_right,
        *(CAP_OUTER - value for value in chamfer_offsets),
        CAP_OUTER,
    ])
    ys = unique([
        0, *chamfer_offsets,
        *(CAP_OUTER - value for value in chamfer_offsets),
        CAP_OUTER,
    ])
    zs = unique([
        0, CAP_PLATE,
        CAP_HEIGHT - USB_DEPTH,
        *stepped_range(chamfer_start, CAP_HEIGHT, 0.1),
    ])

    def wall_offset(z: float) -> float:
        if z < chamfer_start:
            return CAP_WALL
        steps = min(
            5,
            max(1, int((z - chamfer_start) / 0.1) + 1),
        )
        return CAP_WALL - steps * 0.1

    def is_solid(x: float, y: float, z: float) -> bool:
        if z < CAP_PLATE:
            return True

        offset = wall_offset(z)
        wall = (
            x < offset or x > CAP_OUTER - offset
            or y < offset or y > CAP_OUTER - offset
        )
        usb_cut = (
            usb_left < x < usb_right
            and y < CAP_WALL
            and z > CAP_HEIGHT - USB_DEPTH
        )
        return wall and not usb_cut

    return surface_mesh(xs, ys, zs, is_solid)


def validate_watertight(triangles: list[Triangle]) -> None:
    edges: Counter[tuple[Point, Point]] = Counter()
    for triangle in triangles:
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edges[tuple(sorted((a, b)))] += 1
    unmatched = [edge for edge, count in edges.items() if count != 2]
    if unmatched:
        raise RuntimeError(f"Mesh has {len(unmatched)} unmatched edges")


def signed_volume(triangles: list[Triangle]) -> float:
    volume = 0.0
    for a, b, c in triangles:
        volume += (
            a[0] * (b[1] * c[2] - b[2] * c[1])
            + a[1] * (b[2] * c[0] - b[0] * c[2])
            + a[2] * (b[0] * c[1] - b[1] * c[0])
        ) / 6
    return volume


def write_stl(path: Path, solid_name: str,
              triangles: list[Triangle]) -> None:
    with path.open("w", encoding="ascii", newline="\n") as stl:
        stl.write(f"solid {solid_name}\n")
        for triangle in triangles:
            nx, ny, nz = normal(triangle)
            stl.write(f"  facet normal {nx:.9g} {ny:.9g} {nz:.9g}\n")
            stl.write("    outer loop\n")
            for x, y, z in triangle:
                stl.write(f"      vertex {x:.9g} {y:.9g} {z:.9g}\n")
            stl.write("    endloop\n")
            stl.write("  endfacet\n")
        stl.write(f"endsolid {solid_name}\n")


if __name__ == "__main__":
    destination = Path(__file__).parent
    models = (
        (
            "part_1_rear_with_openings.stl",
            "part_1_rear_with_openings",
            rear_mesh(),
        ),
        (
            "part_2_front_cap_with_usb.stl",
            "part_2_front_cap_with_usb",
            cap_mesh(),
        ),
    )

    for filename, solid_name, mesh in models:
        validate_watertight(mesh)
        volume = signed_volume(mesh)
        if volume <= 0:
            raise RuntimeError(f"{filename} has invalid signed volume {volume}")
        write_stl(destination / filename, solid_name, mesh)
        print(f"Wrote {filename}: {len(mesh)} triangles, volume={volume:.3f} mm^3")

    print("Rear: 161 x 161 x 11.2 mm")
    print("Cap: 165.4 x 165.4 x 22.6 mm")
    print("Fit clearance: 0.2 mm per side")
    print("USB openings: 12 x 7 mm, centred and assembly-aligned")
    print("LED opening: 18 x 18 mm, centre=(125, 39) mm")
