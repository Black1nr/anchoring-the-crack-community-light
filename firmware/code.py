import gc
import os
import random
import ssl
import time

import adafruit_requests
import microcontroller
import neopixel
import socketpool
import wifi


# ==================================================
# Editable configuration
# ==================================================

WIDTH = 16
HEIGHT = 16
NUM_PIXELS = WIDTH * HEIGHT
MAX_POINTS = 16

# Brightness values from 0.0 to 1.0
STANDARD_BRIGHTNESS = 0.05
LATEST_BRIGHTNESS = 1

# Check the API once every 60 seconds
UPDATE_INTERVAL = 60

API_URL = (
    "https://livinginthecrack.bbroot.com"
    "/api/public/community-glow"
)


# ==================================================
# Wi-Fi credentials from settings.toml
# ==================================================

WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")

if not WIFI_SSID or not WIFI_PASSWORD:
    raise RuntimeError(
        "Wi-Fi credentials are missing from settings.toml"
    )

if not 0.0 <= STANDARD_BRIGHTNESS <= 1.0:
    raise ValueError(
        "STANDARD_BRIGHTNESS must be between 0.0 and 1.0"
    )

if not 0.0 <= LATEST_BRIGHTNESS <= 1.0:
    raise ValueError(
        "LATEST_BRIGHTNESS must be between 0.0 and 1.0"
    )


# ==================================================
# Google Trust Services Root R4 certificate
# ==================================================

GTS_ROOT_R4 = """-----BEGIN CERTIFICATE-----
MIICCTCCAY6gAwIBAgINAgPlwGjvYxqccpBQUjAKBggqhkjOPQQDAzBHMQswCQYD
VQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExMQzEUMBIG
A1UEAxMLR1RTIFJvb3QgUjQwHhcNMTYwNjIyMDAwMDAwWhcNMzYwNjIyMDAwMDAw
WjBHMQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2Vz
IExMQzEUMBIGA1UEAxMLR1RTIFJvb3QgUjQwdjAQBgcqhkjOPQIBBgUrgQQAIgNi
AATzdHOnaItgrkO4NcWBMHtLSZ37wWHO5t5GvWvVYRg1rkDdc/eJkTBa6zzuhXyi
QHY7qca4R9gq55KRanPpsXI5nymfopjTX15YhmUPoYRlBtHci8nHc8iMai/lxKvR
HYqjQjBAMA4GA1UdDwEB/wQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQW
BBSATNbrdP9JNqPV2Py1PsVq8JQdjDAKBggqhkjOPQQDAwNpADBmAjEA6ED/g94D
9J+uHXqnLrmvT/aDHQ4thQEd0dlq7A/Cr8deVl5c1RxYIigL9zC2L7F8AjEA8GE8
p/SgguMh1YQdc4acLa/KNJvxn7kjNuK8YAOdgLOaVsjh4rsUecrNIdSUtUlD
-----END CERTIFICATE-----
"""


# ==================================================
# Editable colors
# ==================================================

DISTANT = (0, 255, 255)      # D: cyan-blue
GROUNDED = (255, 255, 0)     # G: yellow
CONNECTED = (255, 0, 140)    # C: pink

COLOR_BY_CODE = {
    "D": DISTANT,
    "G": GROUNDED,
    "C": CONNECTED,
}


# ==================================================
# LED matrix
# ==================================================

# Global brightness stays at 1.0 because brightness is
# calculated separately for every point.
matrix = neopixel.NeoPixel(
    microcontroller.pin.GPIO16,
    NUM_PIXELS,
    brightness=1.0,
    auto_write=False,
)

# Point ID -> (x, y, base color)
active_points = {}

# ID of the newest point
latest_point_id = None


def xy_to_index(x, y):
    """Convert coordinates to a serpentine LED index."""
    if y % 2 == 0:
        return (y * WIDTH) + x

    return (y * WIDTH) + (WIDTH - 1 - x)


def scale_color(color, brightness):
    """Apply an individual brightness value to an RGB color."""
    return (
        int(color[0] * brightness),
        int(color[1] * brightness),
        int(color[2] * brightness),
    )


def draw_points():
    """Draw all points with their appropriate brightness."""
    matrix.fill((0, 0, 0))

    for point_id, point_data in active_points.items():
        x, y, base_color = point_data

        if point_id == latest_point_id:
            brightness = LATEST_BRIGHTNESS
        else:
            brightness = STANDARD_BRIGHTNESS

        displayed_color = scale_color(
            base_color,
            brightness,
        )

        matrix[xy_to_index(x, y)] = displayed_color

    matrix.show()


# ==================================================
# Position and spacing rules
# ==================================================

def position_is_allowed(position, occupied_positions):
    """
    Reject the same pixel and horizontal/vertical neighbors.

    Diagonal neighbors are allowed.
    """
    x, y = position

    for occupied_x, occupied_y in occupied_positions:
        distance_x = abs(x - occupied_x)
        distance_y = abs(y - occupied_y)

        if distance_x + distance_y <= 1:
            return False

    return True


def find_random_free_position(occupied_positions):
    """Find a random position following the spacing rule."""

    for attempt in range(1000):
        position = (
            random.randrange(WIDTH),
            random.randrange(HEIGHT),
        )

        if position_is_allowed(
            position,
            occupied_positions,
        ):
            return position

    # Fallback if random selection cannot find a position.
    for y in range(HEIGHT):
        for x in range(WIDTH):
            position = (x, y)

            if position_is_allowed(
                position,
                occupied_positions,
            ):
                return position

    raise RuntimeError(
        "No valid free matrix position available"
    )


# Start with the matrix off.
matrix.fill((0, 0, 0))
matrix.show()


# ==================================================
# Wi-Fi
# ==================================================

def connect_wifi():
    if wifi.radio.connected:
        return

    print("Connecting to Wi-Fi:", WIFI_SSID)

    wifi.radio.connect(
        WIFI_SSID,
        WIFI_PASSWORD,
    )

    print("Connected.")
    print("IP address:", wifi.radio.ipv4_address)


connect_wifi()


# ==================================================
# HTTPS
# ==================================================

pool = socketpool.SocketPool(wifi.radio)

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(
    cadata=GTS_ROOT_R4
)

requests = adafruit_requests.Session(
    pool,
    ssl_context,
)


# ==================================================
# API data handling
# ==================================================

def update_active_points(json_data):
    global latest_point_id

    received_points = json_data.get("points", [])

    # API order is oldest-to-newest.
    received_points = received_points[-MAX_POINTS:]

    valid_points = []

    for point in received_points:
        point_id = point.get("id")
        code = str(point.get("code", "")).upper()

        # The JSON color field is intentionally ignored.
        if point_id and code in COLOR_BY_CODE:
            valid_points.append(
                (
                    point_id,
                    COLOR_BY_CODE[code],
                )
            )

    # The last valid entry is the newest point.
    if valid_points:
        latest_point_id = valid_points[-1][0]
    else:
        latest_point_id = None

    received_ids = []

    for point_id, color in valid_points:
        received_ids.append(point_id)

    # Remove IDs no longer present in the API.
    for point_id in list(active_points):
        if point_id not in received_ids:
            del active_points[point_id]

    # Collect positions belonging to retained points.
    occupied_positions = []

    for x, y, color in active_points.values():
        occupied_positions.append((x, y))

    # Existing IDs keep their positions.
    # New IDs receive spaced random positions.
    for point_id, color in valid_points:
        if point_id in active_points:
            x, y, previous_color = active_points[point_id]

            active_points[point_id] = (
                x,
                y,
                color,
            )

        else:
            x, y = find_random_free_position(
                occupied_positions
            )

            active_points[point_id] = (
                x,
                y,
                color,
            )

            occupied_positions.append((x, y))

    draw_points()

    print(
        "Displaying",
        len(active_points),
        "points",
    )

    if latest_point_id is not None:
        print(
            "Newest point:",
            latest_point_id,
            "at brightness",
            LATEST_BRIGHTNESS,
        )


def download_and_display():
    response = None

    try:
        print("Downloading JSON...")

        response = requests.get(
            API_URL,
            timeout=15,
        )

        if response.status_code != 200:
            raise RuntimeError(
                "HTTP error {}".format(
                    response.status_code
                )
            )

        json_data = response.json()
        update_active_points(json_data)

        print("Update successful.")

    finally:
        if response is not None:
            response.close()

        gc.collect()


# ==================================================
# Main loop
# ==================================================

while True:
    try:
        connect_wifi()
        download_and_display()

    except Exception as error:
        # Keep showing the last successful result.
        print("Update failed:", error)

    time.sleep(UPDATE_INTERVAL)
