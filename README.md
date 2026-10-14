# Anchoring the Crack — Physical Community Light

This repository contains the reproducibility materials for the Physical
Community Light developed as part of the thesis project *Living in the Crack*.
The light reads an anonymised public endpoint from the Milan Emotional Map and
represents up to sixteen recent states as coloured points on a 16 × 16 RGB LED
matrix.

## Repository contents

- `firmware/` — CircuitPython program and safe configuration template.
- `enclosure/source/` — editable OpenSCAD files and the Python model generator.
- `enclosure/printable/` — STL files for 3D printing.
- `enclosure/assembly/` — assembly preview and 3MF project file.
- `api/` — the minimum public data format consumed by the light.
- `hardware/` — preliminary component list and wiring notes.

## Important enclosure-version note

The enclosure files currently included here are the latest files available in
the local thesis archive. They include the final external dimensions, USB
notches, wiring opening, and 0.2 mm side clearance, but the front-cap source and
STL do **not yet contain the four internal corner stops described in the final
thesis text**. The verified corner-stop files should replace these files before
the repository is cited as the final fabrication release.

## Firmware behaviour

- Board: LOLIN S2 Mini (`lolin_s2_mini`)
- Tested with: CircuitPython 10.3.0
- LED data pin: GPIO16
- Matrix: 16 × 16 addressable RGB LEDs in serpentine order
- Maximum displayed entries: 16
- API refresh interval in the released code: 60 seconds
- Ordinary-point brightness: 5%
- Newest-point brightness: 100%

Existing entries retain their positions. New entries are assigned random
positions that avoid occupied pixels and their horizontal or vertical
neighbours. If an update fails, the last successful display remains visible.

## Installation

1. Install CircuitPython 10.3.0 for the LOLIN S2 Mini.
2. Copy `firmware/code.py` to the root of the `CIRCUITPY` drive.
3. Install the dependencies listed in `firmware/libraries.md` under
   `CIRCUITPY/lib/`.
4. Copy `firmware/settings.example.toml` to `CIRCUITPY/settings.toml` and add
   local Wi-Fi credentials.
5. Confirm the public endpoint in `code.py` is appropriate for the deployment.

Never commit a real `settings.toml`, Wi-Fi credentials, API keys, participant
data, device UID, or MAC address.

## API privacy boundary

The lamp only needs an anonymous entry ID and one of three state codes. Location,
text, images, and participant background information remain on the website and
are not transmitted to the lamp.

## Licence

An open-source licence has not yet been selected by the project author. Until a
licence file is added, the files remain available for review but no reuse rights
are granted by default.

