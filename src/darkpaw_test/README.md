# darkpaw_test

Verifies the ROS 2 control contour: commands published to `/cmd_vel` reach a node.

## Contents

| File | Purpose |
|---|---|
| `darkpaw_test/listener.py` | `/cmd_vel` subscriber (`geometry_msgs/Twist`) that logs `linear` and `angular` |
| `launch/listener.launch.py` | starts the node via `ros2 launch` |

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select darkpaw_test
source install/setup.bash
```

## Run (two terminals on the robot)

Terminal 1 — listen:

```bash
source ~/ros2_ws/install/setup.bash
ros2 run darkpaw_test listener
```

Terminal 2 — drive:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keys: `i` forward, `,` backward, `j` turn left, `l` turn right, `k` stop,
`q`/`z` increase/decrease speed.

## Expected result

Every keypress produces a line in terminal 1:

```
[cmd_vel_listener]: Received: linear=+0.50 m/s, angular=+0.00 rad/s
```

If nothing appears, check `ROS_DOMAIN_ID` on both sides and that the nodes are on the
same DDS domain (see `docs/` in the repository root).

## Why this is a separate package

It is a "mute" contour: no motors involved. First we prove messages flow, then a gait
controller (`darkpaw_gait`) subscribes to the same topic. That way any failure splits into
two independent questions — "messaging" and "hardware" — and is diagnosed separately.
