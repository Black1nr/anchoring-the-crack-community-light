# Wiring notes

The current firmware sends LED data from `GPIO16` on the LOLIN S2 Mini to the
matrix data-input connection.

Minimum logical connections:

| Controller / supply | LED matrix |
| --- | --- |
| GPIO16 | DIN |
| GND | GND |
| Regulated power appropriate to the matrix | 5V power input |

The controller and matrix must share ground. Do not power a full 256-pixel
matrix through a GPIO pin. Confirm the matrix's actual current requirements,
connector orientation, power supply, and wiring against the physical prototype
before assembly. Only up to sixteen pixels are illuminated by the current
program, but the power arrangement should still be documented and verified.

