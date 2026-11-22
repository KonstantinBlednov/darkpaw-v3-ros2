#!/usr/bin/env python3
"""Echo node: logs everything published to /cmd_vel.

Why it exists: to prove the ROS 2 contour is wired correctly — commands typed in
teleop_twist_keyboard reach a subscriber. It does not touch motors, it only verifies
messaging and the Twist message format.

Run:
    ros2 run darkpaw_test listener
    # or
    ros2 launch darkpaw_test listener.launch.py
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class CmdVelListener(Node):
    """Subscriber on /cmd_vel that only logs message contents."""

    def __init__(self) -> None:
        super().__init__("cmd_vel_listener")
        self.subscription = self.create_subscription(
            Twist, "cmd_vel", self.on_cmd_vel, 10
        )
        self.get_logger().info(
            "Waiting for /cmd_vel — press i (forward), j/l (turn), k (stop)"
        )

    def on_cmd_vel(self, msg: Twist) -> None:
        self.get_logger().info(
            f"Received: linear={msg.linear.x:+.2f} m/s, "
            f"angular={msg.angular.z:+.2f} rad/s"
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CmdVelListener()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # Ctrl+C: rclpy already shut the context down, a second call would raise RCLError
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
