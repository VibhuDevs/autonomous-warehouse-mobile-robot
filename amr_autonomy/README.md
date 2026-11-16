# `amr_autonomy`

This package provides named warehouse locations and a ROS 2 mission commander.
The commander accepts an aisle command and runs a pickup → aisle → return
sequence through Nav2's `NavigateToPose` action.

## Package contents

- `config/locations.yaml` — poses in the `map` frame as `[x, y, yaw]`, with yaw
  in radians.
- `scripts/mission_commander.py` — subscribes to mission commands, loads the
  locations file, sends Nav2 goals, and waits five seconds at pickup and at the
  selected aisle.
- `CMakeLists.txt` — installs the script and location configuration.
- `package.xml` — ROS and Python runtime dependencies.

## Build

From the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-up-to amr_autonomy
source install/setup.bash
```

## Run it

The recommended way is to start it automatically with Nav2:

```bash
ros2 launch amr_navigation navigation.launch.py use_sim_time:=true
```

The commander is launched by `navigation.launch.py` and listens on
`/amr_autonomy/command`. Publish one of these commands:

```bash
ros2 topic pub --once /amr_autonomy/command std_msgs/msg/String "{data: 'aisle1'}"
ros2 topic pub --once /amr_autonomy/command std_msgs/msg/String "{data: 'go to aisle 2'}"
```

The first example accepts the aisle name directly; the second demonstrates
natural-style text containing an aisle number. Only aisle names present in
`locations.yaml` can be selected.

## Mission sequence

1. Navigate to `pickup_point`.
2. Wait five seconds.
3. Navigate to the requested aisle.
4. Wait five seconds.
5. Return to `initial_pose` (the charging pose).

The waits use ROS simulation time. Keep Gazebo running and unpaused. Nav2 must
be active and the robot must have a valid pose in the `map` frame before
issuing a mission.

To change target poses, edit `config/locations.yaml`. Each entry must have
exactly three finite numeric values: `x`, `y`, and `yaw`. Keep the required
`initial_pose` and `pickup_point` entries and at least one key named
`aisle...`.
