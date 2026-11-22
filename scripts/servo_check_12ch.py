#!/usr/bin/env python3
"""Sweep all 12 PCA9685 channels on the Adeept Robot HAT V3.3.

Purpose: prove that the I2C bus, the PWM driver and the servos are alive.
This is a hardware/software smoke test, not walking: channels are moved one by one.

Why not the vendor library:
    the stock Adafruit CircuitPython / Blinka stack is broken on this board
    (Adafruit-Blinka-Raspberry-Pi-PWM), so PCA9685 registers are written directly.
    Details: docs/hardware.md.

WARNING:
    servos are powered ONLY from the 18650 pack. On USB, 12 actuators sag the
    rail and the board reboots.

Usage (on the Raspberry Pi, with access to /dev/i2c-1):
    sudo python3 scripts/servo_check_12ch.py
    sudo python3 scripts/servo_check_12ch.py --channels 0-3 --amplitude 150
"""

import argparse
import sys
import time

from smbus2 import SMBus

# --- Board -----------------------------------------------------------------
# IMPORTANT: on the Adeept Robot HAT V3.3 the address is hardwired to 0x5F, not 0x40.
PCA9685_ADDR = 0x5F
I2C_BUS = 1

# --- PCA9685 registers -----------------------------------------------------
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

PWM_HZ = 50
TICKS_PER_PERIOD = 4096
PERIOD_US = 1_000_000 // PWM_HZ  # 20000 us = 20 ms

# Safe pulse window for MG90S on this linkage.
# Going beyond it means hitting a mechanical stop and stripping a gear.
PULSE_US_MIN = 1100
PULSE_US_MAX = 1900
PULSE_US_CENTER = 1500


def us_to_ticks(pulse_us: int) -> int:
    """Convert a pulse width in microseconds to PCA9685 ticks (0..4095)."""
    if not PULSE_US_MIN <= pulse_us <= PULSE_US_MAX:
        raise ValueError(
            f"pulse {pulse_us} us is outside the safe window "
            f"{PULSE_US_MIN}..{PULSE_US_MAX} us"
        )
    return round(pulse_us * TICKS_PER_PERIOD / PERIOD_US)


class Pca9685:
    """Minimal PCA9685 driver on top of smbus2: only what servos need."""

    def __init__(self, bus_id: int = I2C_BUS, address: int = PCA9685_ADDR,
                 frequency_hz: int = PWM_HZ) -> None:
        self.address = address
        self.bus = SMBus(bus_id)

        # Reset and sleep so that prescale can be written
        self.bus.write_byte_data(address, MODE1, 0x00)
        time.sleep(0.05)

        prescale = round(25_000_000 / (TICKS_PER_PERIOD * frequency_hz)) - 1
        self.bus.write_byte_data(address, MODE1, 0x10)      # sleep
        self.bus.write_byte_data(address, PRESCALE, prescale)
        self.bus.write_byte_data(address, MODE1, 0x20)      # wake + auto-increment
        time.sleep(0.05)

    def set_pulse_us(self, channel: int, pulse_us: int) -> None:
        """Set the pulse width on channel 0..15."""
        off_tick = us_to_ticks(pulse_us)
        reg = LED0_ON_L + (channel * 4)
        self.bus.write_byte_data(self.address, reg, 0)                     # ON_L
        self.bus.write_byte_data(self.address, reg + 1, 0)                 # ON_H
        self.bus.write_byte_data(self.address, reg + 2, off_tick & 0xFF)   # OFF_L
        self.bus.write_byte_data(self.address, reg + 3, off_tick >> 8)     # OFF_H

    def release(self, channel: int) -> None:
        """Drop hold torque: off_tick = 0, so the motor draws no current and stays cool."""
        reg = LED0_ON_L + (channel * 4)
        for offset in range(4):
            self.bus.write_byte_data(self.address, reg + offset, 0)

    def close(self) -> None:
        self.bus.close()


def parse_channels(text: str) -> list[int]:
    """'0-3' -> [0,1,2,3], '5' -> [5], '0-2,7' -> [0,1,2,7]."""
    result: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            result.extend(range(int(start), int(end) + 1))
        elif part:
            result.append(int(part))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="PCA9685 channel sweep (12 servos)")
    parser.add_argument("--channels", default="0-11",
                        help="channels to sweep, e.g. 0-11 or 0-3 (default: 0-11)")
    parser.add_argument("--amplitude", type=int, default=250,
                        help="deviation from center in microseconds (default: 250)")
    parser.add_argument("--hold", type=float, default=0.4,
                        help="pause per position, seconds (default: 0.4)")
    args = parser.parse_args()

    channels = parse_channels(args.channels)
    if any(not 0 <= ch <= 15 for ch in channels):
        print("ERROR: channels must be within 0..15")
        return 2

    print(f"PCA9685 @ 0x{PCA9685_ADDR:02X} on /dev/i2c-{I2C_BUS}, {PWM_HZ} Hz")
    try:
        pca = Pca9685()
    except Exception as exc:  # noqa: BLE001 — surface any bus error as-is
        print(f"[ERROR] I2C unavailable: {exc}")
        print("Check: battery power, then i2cdetect -y 1 (must show 5f)")
        return 1

    print(f"Pulses: center {PULSE_US_CENTER} us +- {args.amplitude} us, "
          f"safe window {PULSE_US_MIN}..{PULSE_US_MAX} us")

    positions = [
        PULSE_US_CENTER - args.amplitude,
        PULSE_US_CENTER,
        PULSE_US_CENTER + args.amplitude,
        PULSE_US_CENTER,
    ]

    try:
        for channel in channels:
            print(f"channel {channel:2d}: ", end="", flush=True)
            for pulse in positions:
                pca.set_pulse_us(channel, pulse)
                print(f"{pulse} ", end="", flush=True)
                time.sleep(args.hold)
            pca.release(channel)
            print("ok")
        print("\n[DONE] Every requested channel responded.")
        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        return 130
    finally:
        # Always release torque, otherwise the servos buzz and heat up
        for channel in range(12):
            try:
                pca.release(channel)
            except Exception:  # noqa: BLE001
                pass
        pca.close()
        print("Hold torque released, bus closed.")


if __name__ == "__main__":
    sys.exit(main())
