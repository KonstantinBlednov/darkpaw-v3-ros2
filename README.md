# DarkPaw-V3 → Autonomous Navigation on ROS 2

[![ROS 2](https://img.shields.io/badge/ROS_2-Humble-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/humble/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04_LTS-E95420?logo=ubuntu&logoColor=white)](https://releases.ubuntu.com/22.04/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi_4B-4_GB-A22846?logo=raspberrypi&logoColor=white)](https://www.raspberrypi.com/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Turning an off-the-shelf 12-DOF quadruped (Adeept DarkPaw-V3) into an autonomous navigation
platform: from a single PWM write to a servo, all the way to SLAM and Nav2 on a Raspberry Pi 4B
running ROS 2 Humble.

No hardware upgrades. The interesting part is the software — and the undocumented hardware
quirks that every tutorial silently walks past.

## The task

| | |
|---|---|
| Platform | Adeept DarkPaw-V3, 12× MG90S servos, no position feedback |
| Compute | Raspberry Pi 4B, 4 GB, Ubuntu Server 22.04.5 LTS |
| Sensor | LDROBOT D500 LiDAR (DTOF, 360°) |
| Middleware | ROS 2 Humble Base |
| End goal | room map from SLAM + goal-reaching with Nav2 over 1–2 m |

## Status

| Stage | What happens | Status |
|:--:|---|:--:|
| 0 | Bring-up: ROS 2, network, LiDAR driver, all 12 servos driven directly via PCA9685 | ✅ done |
| 1 | Control contour: `/cmd_vel` subscriber node + `teleop_twist_keyboard` | 🚧 in progress |
| 2 | Gait controller `darkpaw_gait`: leg inverse kinematics, trot gait | ⬜ |
| 3 | RViz2 on macOS over DDS (wireless visualization) | ⬜ |
| 4 | `rf2o_laser_odometry` + `slam_toolbox`, room map | ⬜ |
| 5 | Nav2: reach a goal 1–2 m away and stop there | ⬜ |

## Architecture (target)

```
/scan ──→ rf2o_laser_odometry ──→ odometry ──┬──→ slam_toolbox ──→ /map
                                             │
Nav2 (DWB) ──→ /cmd_vel ──→ darkpaw_gait ────┴──→ 12 servos
                            (gait + IK)            via PCA9685 @ 0x5F
                                                   (smbus2, I2C)
RViz2 on MacBook ←── DDS, ROS_DOMAIN_ID=42 ────────┘
```

The core constraint: a `/cmd_vel` Twist **cannot** drive servos directly. Between Nav2 and the
hardware there has to be a gait controller that converts "move forward at 0.1 m/s, turn at
0.3 rad/s" into cyclic leg trajectories (trot gait, diagonal pairs FL+RR / FR+RL).

## Engineering findings

Three things that cost the most time and are not documented by the board vendor:

1. **On this board the PCA9685 answers at address `0x5F`, not `0x40`.** The address is hardwired
   on the Adeept Robot HAT V3.3. Every tutorial and `i2cdetect` guide looks for `0x40` and quietly
   does nothing.
2. **Adafruit CircuitPython / Blinka does not work here.** `Adafruit-Blinka-Raspberry-Pi-PWM` is
   broken on this combination and demands dependency reinstalls on every import;
   `BLINKA_SKIP_DEPENDENCY_CHECK` workarounds do not make it stable either. The solution is
   writing PCA9685 registers directly through `smbus2`.
3. **Servos are powered only from the 18650 battery pack.** 12 servos on a USB port sag the rail
   and reboot the board; in testing this looks like "the script hangs".

Details and exact register values: [`docs/hardware.md`](docs/hardware.md).
What was actually verified on the hardware in stage 0: [`docs/stage0.md`](docs/stage0.md).

## Stack

`ROS 2 Humble` · `rclpy` · `Python 3.10` · `smbus2` · `colcon` · `slam_toolbox` · `Nav2` ·
`ldlidar_stl_ros2` · `rf2o_laser_odometry` · `RoboStack / RViz2` (macOS)

## Repository layout

```
scripts/
  servo_check_12ch.py     sweep all 12 channels, pulses limited to 1100-1900 us
  cmd_vel_probe.py        publish a given Twist to /cmd_vel (contour smoke test)
docs/
  hardware.md             board, addresses, registers, power, GPIO
  stage0.md               what was verified on hardware (stage 0)
src/
  darkpaw_test/           ROS 2 package: /cmd_vel subscriber that logs incoming commands
```

## Quick start (stage 0: servo check)

On the Raspberry Pi, with the batteries connected:

```bash
git clone https://github.com/KonstantinBlednov/darkpaw-v3-ros2.git
cd darkpaw-v3-ros2
sudo python3 scripts/servo_check_12ch.py
```

Expected: each of the 12 channels sweeps to one side, to the other and back to center.
At the end hold torque is released (`off_tick = 0`) so the motors do not heat up.

## Roadmap

- [x] Stage 0 — bring-up and servo bring-up
- [ ] Stage 1 — `/cmd_vel` contour
- [ ] Stage 2 — keyboard-driven gait
- [ ] Stage 3 — RViz2 on macOS
- [ ] Stage 4 — SLAM and a room map
- [ ] Stage 5 — Nav2 goal-reaching
- [ ] Demo video and wiring diagram in `docs/`

## License

MIT — see [LICENSE](LICENSE).
