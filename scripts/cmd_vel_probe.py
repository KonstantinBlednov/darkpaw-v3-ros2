#!/usr/bin/env python3
"""Publish a single command to /cmd_vel — a contour smoke test without a keyboard.

Purpose: when the goal is to check that a subscriber works, and driving the interactive
teleop_twist_keyboard is inconvenient (for example when running over SSH), publishing a
couple of Twist messages is enough.

Examples:
    python3 scripts/cmd_vel_probe.py                      # stop, 2 seconds
    python3 scripts/cmd_vel_probe.py --linear 0.15 --angular 0.0 --seconds 2
    python3 scripts/cmd_vel_probe.py --linear -0.1        # backwards

Requires ROS 2 in the environment:
    source /opt/ros/humble/setup.bash
"""

import argparse
import time

import rclpy
from geometry_msgs.msg import Twist


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a Twist to /cmd_vel")
    parser.add_argument("--linear", type=float, default=0.0,
                        help="linear velocity, m/s (forward > 0)")
    parser.add_argument("--angular", type=float, default=0.0,
                        help="angular velocity, rad/s (left > 0)")
    parser.add_argument("--seconds", type=float, default=2.0,
                        help="how long to publish (default: 2)")
    parser.add_argument("--rate", type=float, default=10.0,
                        help="publish rate, Hz (default: 10)")
    args = parser.parse_args()

    rclpy.init()
    node = rclpy.create_node("cmd_vel_probe")
    publisher = node.create_publisher(Twist, "/cmd_vel", 10)

    msg = Twist()
    msg.linear.x = args.linear
    msg.angular.z = args.angular

    node.get_logger().info(
        f"Publishing {args.linear:+.2f} m/s, {args.angular:+.2f} rad/s "
        f"for {args.seconds:.1f} s"
    )
    period = 1.0 / args.rate
    deadline = time.monotonic() + args.seconds
    while time.monotonic() < deadline:
        publisher.publish(msg)
        time.sleep(period)

    # Trailing zero: any node that waits for silence sees the command as finished
    publisher.publish(Twist())
    node.get_logger().info("Done, zero Twist sent")
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
