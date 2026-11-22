"""Launch the /cmd_vel subscriber."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(
                package="darkpaw_test",
                executable="listener",
                name="cmd_vel_listener",
                output="screen",
            )
        ]
    )
