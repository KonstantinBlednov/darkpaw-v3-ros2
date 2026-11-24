# Servo layout — Adeept DarkPaw-V3

Source: the vendor wiring diagram, transcribed in [`docs/servo-wiring-vendor.md`](servo-wiring-vendor.md).
This file records what the vendor **claims**; the gait controller is not allowed to run until it is verified on
the hardware (see "Verification" at the bottom).

## Channel numbering

The vendor numbers servos 0–11, three per leg, and the numbering is contiguous:

| Leg (vendor name) | Servos | Side |
|---|---|---|
| Leg 1 | 0, 1, 2 | left |
| Leg 2 | 3, 4, 5 | left |
| Leg 3 | 6, 7, 8 | right |
| Leg 4 | 9, 10, 11 | right |

Vendor colour code: Leg 1 green, Leg 2 cyan, Leg 3 dark green, Leg 4 red.

Which of the two legs per side is the *front* one is not stated in the diagram. Confirm it at the
first movement by lifting one leg at a time.

## Joint role per channel

Reading the exploded diagram: every leg has the same three joints — abduction (swings the whole
leg sideways around a vertical axis), thigh (lifts the upper limb around a horizontal axis) and
knee (bends the lower limb).

The channel order inside a leg is **not** the same for all legs:

| Leg | Abduction | Thigh | Knee |
|---|---|---|---|
| Leg 1 (0,1,2) | 0 | 2 | 1 |
| Leg 2 (3,4,5) | 5 | 4 | 3 |
| Leg 3 (6,7,8) | 6 | 8 | 7 |
| Leg 4 (9,10,11) | 11 | 10 | 9 |

Pattern: legs 1 and 3 put abduction at the lowest channel of the triple (k, k+2, k+1);
legs 2 and 4 put it at the highest (k+2, k+1, k). This asymmetry is exactly the kind of detail
that must be verified rather than trusted — a wrong guess means driving a joint into its
mechanical stop.

## Pulse limits

| | Value |
|---|---|
| PWM frequency | 50 Hz (prescale `0x79`) |
| Safe pulse window | 1100–1900 µs |
| Center | 1500 µs |
| I2C address of PCA9685 | `0x5F` |

`1100–1900 µs` is deliberately narrower than the datasheet range (500–2500 µs): the linkage hits
its mechanical limit earlier, and these servos have no feedback to tell us when.

## Verification (stage 2, step 1)

Run one channel at a time with a small amplitude and watch which joint moves:

```bash
sudo python3 scripts/servo_check_12ch.py --channels 0 --amplitude 150 --hold 1.0
```

For every channel record:

1. **leg** — which of the four legs moved;
2. **joint** — abduction / thigh / knee;
3. **sign** — does a pulse *below* 1500 µs move the joint in the same direction as another leg's
   equivalent joint, or the opposite one?
4. **trim** — the pulse that makes the leg visually straight/centered (mechanical trim, ±50 µs
   is normal between hobby servos).

Results go into `config/servo_map.yaml`. Only after all 12 are filled in does the gait controller
get to move anything.
