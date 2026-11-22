# Stage 1 — the /cmd_vel contour

Goal: prove that commands can travel from a keyboard to a node, before any motor is involved.

## What was built

| Piece | Role |
|---|---|
| `src/darkpaw_test` | ROS 2 package with a `/cmd_vel` subscriber that logs incoming commands |
| `scripts/cmd_vel_probe.py` | publishes a `Twist` on demand, for smoke tests without a keyboard |
| `teleop_twist_keyboard` | stock ROS 2 package that turns keypresses into `Twist` messages |

Workspace on the robot:

```bash
mkdir -p ~/ros2_ws/src
# package copied into ~/ros2_ws/src/darkpaw_test
cd ~/ros2_ws && colcon build --packages-select darkpaw_test
source install/setup.bash
```

## Run

Terminal 1 — subscriber:

```bash
ros2 run darkpaw_test listener
```

Terminal 2 — keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Result

`i`, `j`, `l`, `,` and the diagonal keys all arrived. Values logged by the subscriber:

| Key | Message received | Count |
|---|---|---|
| `i` forward | `linear=+0.50 m/s` | 48 |
| `j` / `l` turn | `angular=+1.00` / `-1.00 rad/s` | 30 / 24 |
| `,` backward | `linear=-0.47 m/s` | present |
| `u` / `o` forward + turn | `0.72 / ±1.30` | present |

## The gotcha worth writing down

While testing, the keyboard node appeared to be broken: only `q/w/z/x/c` seemed to do anything,
because those keys changed the on-screen `currently: speed … turn …` line.

That line shows the **speed limits**, not the current command. Movement keys change the command
and print nothing. Without a subscriber there is no way to see them working.

Lesson: a node can behave correctly and still look broken if it does not expose its state.
That is why this repository keeps a dedicated echo node — it turns an invisible message stream
into visible log lines. Diagnose from data, not from impressions.

## A real bug found on the way

`Ctrl+C` produced `RCLError: failed to shutdown: rcl_shutdown already called`. rclpy's signal
handler already shuts the context down, so calling `rclpy.shutdown()` again fails. Fixed with an
`rclpy.ok()` guard and by catching `ExternalShutdownException` in the node's main function.

## Next

Stage 2: map PWM channels to physical joints, one leg at a time, then stand up.
