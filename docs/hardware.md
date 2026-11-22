# Hardware and electrics — DarkPaw-V3

Everything below was measured on this particular unit, not copied from vendor documentation.
Where the documentation is wrong, it is called out explicitly.

## Bill of materials

| Unit | Model | Notes |
|---|---|---|
| Chassis | Adeept DarkPaw-V3 | 4 legs × 3 joints = 12 actuators |
| Servos | MG90S, metal gears | ~2.2 kg·cm, 5–6 V, **no position feedback** |
| Board | Adeept Robot HAT V3.3 | 2×18650 power, battery ADC, buzzer, RGB LED |
| PWM driver | PCA9685 (on the HAT) | I2C, 16 channels, 12 used |
| SBC | Raspberry Pi 4B, 4 GB | Ubuntu Server 22.04.5 LTS |
| LiDAR | LDROBOT D500 (STL-19P) | DTOF 360°, `/dev/ttyUSB0`, publishes `/scan` |
| IMU | MPU6050 | on the bus at `0x68`, not used yet |
| Camera | CSI | out of scope for the MVP |

## I2C bus

| Address | Device | Comment |
|---|---|---|
| `0x5F` | PCA9685 (servo PWM) | **not 0x40** — see below |
| `0x48` | Battery voltage ADC | on the HAT |

Verify with:

```bash
sudo i2cdetect -y 1
```

Expected: `48` and `5f` present in the table.

### Why the PCA9685 sits at 0x5F

The default PCA9685 address is `0x40` (all three address pins tied to ground). On the Adeept
Robot HAT V3.3 the address pins are wired differently, and the chip answers at `0x5F`.
Consequences:

- any code from the internet (`Adafruit_PCA9685.PCA9685()`, `PCA9685()` with no arguments) talks
  to `0x40`, gets `OSError: [Errno 121] Remote I/O error`, and makes the board look dead;
- toggling the power-switch GPIOs (BCM 9 / 25 / 11) does not help: on this HAT revision the
  address does not depend on them.

## PCA9685 registers used

| Register | Address | Value |
|---|---|---|
| `MODE1` | `0x00` | `0x00` reset, `0x10` sleep before prescale write, `0x20` wake + auto-increment |
| `PRESCALE` | `0xFE` | `0x79` — that is 50 Hz |
| `LED0_ON_L` | `0x06` | base for channel 0; channel `n` starts at `0x06 + 4n` |

Frequency: `prescale = round(25 000 000 / (4096 × 50)) − 1 = 121 = 0x79`.

The PWM period is 20 ms (4096 ticks), so one tick is about 4.88 µs:

```
ticks = pulse_us × 4096 / 20000
1500 us → 307   (center)
1100 us → 225   (lower limit)
1900 us → 389   (upper limit)
```

## Safety limits

These servos have no feedback: the controller never knows where the shaft really is. Therefore:

- pulses stay strictly within **1100–1900 µs** (not the 500–2500 µs from the datasheet — the
  DarkPaw linkage hits its mechanical stop earlier);
- on exit, hold torque is released (`off_tick = 0`), otherwise the motors buzz and heat up;
- all transitions are interpolated, never stepped — a step is an impact on the gearbox.

## Power

- Servos run **only from the 2×18650 pack**. 12 actuators on a USB port sag the rail and reboot
  the board; in tests this looks like "the script hangs halfway".
- The Raspberry Pi is powered separately (USB-C), ground is common through the HAT.
- On-board LEDs work.

## GPIO

`gpioset` (package `gpiod`), chip `gpiochip0`. Power-switch pins per the stock firmware:
BCM 9, 25, 11 (verified by toggling the flashlight). They do not affect `0x5F` availability.

## Software on the Pi

| What | Where |
|---|---|
| ROS 2 Humble Base | `/opt/ros/humble`, sourced from `~/.bashrc` |
| LiDAR | `~/ldlidar_ros2_ws`, package `ldlidar_stl_ros2`, topic `/scan` |
| `smbus2` | system Python (`sudo pip3 install smbus2`), version 0.6.1 |
| ROS environment | `ROS_DOMAIN_ID=42`, `ROS_LOCALHOST_ONLY=0` |

Note: `rclpy` is only importable after `source /opt/ros/humble/setup.bash`. When running commands
over SSH without an interactive shell, source it explicitly — `~/.bashrc` returns early for
non-interactive sessions.
