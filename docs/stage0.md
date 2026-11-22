# Stage 0 — bring-up log

November 2026. Everything below was verified on the hardware; the commands are reproducible.

## 1. ROS 2 Humble on Raspberry Pi 4B

```bash
lsb_release -ds          # Ubuntu 22.04.5 LTS
ls /opt/ros              # humble
source /opt/ros/humble/setup.bash
ros2 --version
```

Two-node check with `demo_nodes_cpp talker` + `demo_nodes_py listener`: messages flow.

Added to `~/.bashrc`:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=42
export ROS_LOCALHOST_ONLY=0
```

`ROS_DOMAIN_ID=42` keeps the robot's nodes from mixing with anyone else's on the network
(including the macOS machine). `ROS_LOCALHOST_ONLY=0` is what lets RViz2 on the Mac see topics
from the Pi over Wi-Fi.

## 2. Network

Pi and MacBook share one hotspot. SSH from the Mac uses a key:

```bash
ssh pi
```

The Pi's address is **not stable**: the hotspot hands out a new subnet after a reboot
(observed `10.117.184.65`, later `10.75.112.65`). If `ssh pi` does not answer, rescan the
subnet for port 22 and update `HostName` in `~/.ssh/config`.

## 3. LDROBOT D500 LiDAR

```bash
# the driver is built in a separate workspace
cd ~/ldlidar_ros2_ws && source install/setup.bash
ros2 launch ldlidar_stl_ros2 ld19.launch.py     # port /dev/ttyUSB0
ros2 topic hz /scan                              # ~10 Hz
```

`/scan` publishes valid data. The driver is considered done and is not touched again.

## 4. Bringing the 12 servos to life

First attempt — the vendor-provided Adafruit (CircuitPython / Blinka) path:

```
ModuleNotFoundError / demands reinstalling Adafruit-Blinka-Raspberry-Pi-PWM
```

That package is broken on this combination, and `BLINKA_SKIP_DEPENDENCY_CHECK` workarounds do not
make it stable. The direction was closed.

The working solution is writing PCA9685 registers directly through `smbus2`:

```bash
sudo i2cdetect -y 1        # table shows 48 (battery ADC) and 5f (PCA9685)
sudo python3 scripts/servo_check_12ch.py
```

What was verified:

- the chip answers at `0x5F`;
- `prescale = 0x79` yields 50 Hz;
- all 12 channels sweep and return to center;
- releasing hold torque (`off_tick = 0`) works and the motors stop heating up.

Result: the hardware access layer is understood and reproducible, which unblocks the gait
controller.

## Conclusions for the next stages

1. No ROS 2 packages exist on the Pi yet — `~/ros2_ws` is absent, so stage 1 starts from scratch.
2. `colcon` is installed, `teleop_twist_keyboard` is not (installed via `apt`).
3. `smbus2` 0.6.1 is already in the system Python, nothing to install.
4. Every future I2C command needs `sudo` (access to `/dev/i2c-1`).
