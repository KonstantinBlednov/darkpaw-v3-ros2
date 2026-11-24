# Vendor wiring diagram — transcription

Transcribed from the Adeept DarkPaw-V3 manual pages so that the numbers live in the repository,
not only in a PDF.

Original note (verbatim): *"According to the numbering, install the servos into the ports. Note
that you should not reverse the polarity of the servo wiring."*

## Board-to-servo table (as printed)

**Left leg group**

| | column 1 | column 2 | column 3 |
|---|---|---|---|
| upper row | Servo 2 | Servo 0 | Servo 5 |
| lower row | Servo 1 | Servo 3 | Servo 4 |

**Right leg group**

| | column 1 | column 2 | column 3 |
|---|---|---|---|
| upper row | Servo 11 | Servo 6 | Servo 8 |
| lower row | Servo 10 | Servo 9 | Servo 7 |

## Leg labels (as printed)

| Label | Colour | Side |
|---|---|---|
| Leg 1 | green | left |
| Leg 2 | cyan | left |
| Leg 3 | dark green | right |
| Leg 4 | red | right |

## Exploded view (as printed)

| Leg label in drawing | Servos pointing at that leg |
|---|---|
| Leg N01 | 0, 2, 1 |
| Leg N02 | 5, 4, 3 |
| Leg N03 | 6, 8, 7 |
| Leg N04 | 11, 10, 9 |

Reading the 3D drawing, the three joints per leg are: one servo on the top deck (vertical axis,
swings the whole leg), one on the upper limb (horizontal axis, lifts the thigh) and one on the
knee. Mapping channels to those roles is the job of stage 2 step 1 — see `docs/servo-map.md`.

## What the vendor diagram does not say

- which leg of a pair is front and which is rear;
- the direction of positive rotation for each joint;
- the mechanical trim (center pulse) of each individual servo;
- the safe pulse window for this linkage (the datasheet 500–2500 µs is too wide — the linkage
  hits its stop earlier).

All four are measured on the hardware and recorded in `config/servo_map.yaml`.
