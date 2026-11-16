# Autonomous Warehouse Mobile Robot

ROS 2 Jazzy simulation and navigation workspace for a differential-drive
warehouse robot. The workspace includes the robot model, Gazebo worlds,
controller and bridge configuration, a saved warehouse map, Nav2 localization
and navigation with recovery behavior trees, and a named-location mission
commander.

## Workspace packages

| Package | Purpose | Guide |
|---|---|---|
| `amr_description` | Robot model, simulation launch, and RViz configuration | [amr_description/README.md](amr_description/README.md) |
| `amr_gazebo` | Gazebo warehouse worlds | [amr_gazebo/README.md](amr_gazebo/README.md) |
| `amr_bringup` | Gazebo-to-ROS bridge and drive controller configuration | [amr_bringup/README.md](amr_bringup/README.md) |
| `amr_navigation` | Saved map, localization, Nav2, and recovery behavior trees | [amr_navigation/README.md](amr_navigation/README.md) |
| `amr_autonomy` | Named locations and pickup/aisle/return missions | [amr_autonomy/README.md](amr_autonomy/README.md) |

## Requirements

- Ubuntu with ROS 2 Jazzy
- Gazebo Sim and the ROS-Gazebo integration packages
- Nav2, `slam_toolbox`, `xacro`, and the packages declared in the ROS package
  manifests

Install missing ROS dependencies from the workspace root with:

```bash
rosdep install --from-paths . --ignore-src -r -y
```

Build the workspace:

```bash
source /opt/ros/jazzy/setup.bash
cd /path/to/autonomous-warehouse-mobile-robot
colcon build --symlink-install
source install/setup.bash
```

Replace `/path/to/autonomous-warehouse-mobile-robot` with the directory where
the repository was cloned.

## Start the simulation and navigation

Run each command in its own terminal. Source ROS and the workspace overlay in
each terminal.

**Terminal 1 — Gazebo, robot model, controllers, bridge, and RViz:**

```bash
source /opt/ros/jazzy/setup.bash
cd /path/to/autonomous-warehouse-mobile-robot
source install/setup.bash
ros2 launch amr_description amr_launch.xml
```

SLAM and standalone localization are disabled by default in this launch. This
avoids starting mapping while using the saved map and avoids duplicating the
localization stack started by Nav2.

**Terminal 2 — saved-map localization, Nav2 navigation, and mission commander:**

```bash
source /opt/ros/jazzy/setup.bash
cd /path/to/autonomous-warehouse-mobile-robot
source install/setup.bash
ros2 launch amr_navigation navigation.launch.py use_sim_time:=true
```

This starts the combined navigation stack with the configured BT recovery
trees. It also starts the mission commander that listens on
`/amr_autonomy/command`.

## Run a named warehouse mission

Publish a command from a third terminal (after sourcing the workspace):

```bash
ros2 topic pub --once /amr_autonomy/command std_msgs/msg/String "{data: 'go to aisle 1'}"
```

For the second aisle:

```bash
ros2 topic pub --once /amr_autonomy/command std_msgs/msg/String "{data: 'go to aisle 2'}"
```

Each mission navigates to the configured pickup point, waits five seconds,
navigates to the requested aisle, waits another five seconds, and returns to
the configured initial/charging pose. Each leg is a Nav2 `NavigateToPose` goal
and therefore uses the Nav2 navigation behavior tree and its recovery actions.

## Send a direct Nav2 goal

To send a single goal without the pickup-and-return mission, use
`/navigate_to_pose`. Example coordinates for aisle 1:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: 7.31, y: -2.58, z: 0.0}, orientation: {z: -0.992, w: 0.126}}}}"
```

The robot must be localized in the `map` frame before sending a map-frame goal.

## Configuration and troubleshooting

- Named mission poses are in `amr_autonomy/config/locations.yaml`.
- The map image and metadata are in `amr_navigation/maps/`.
- Nav2 parameters and recovery BT file paths are in
  `amr_navigation/config/nav2_params.yaml`.
- Recovery behavior trees are in `amr_navigation/behavior_trees/`.
- Robot dimensions and ROS 2 control setup are described in
  `amr_description/urdf/`.
- RViz shows the robot, map, laser scan, TF, and global/local costmaps when the
  relevant publishers are active.
- If old simulation, localization, or navigation launches are still running,
  stop those launch processes with Ctrl+C before starting another copy. Avoid
  running standalone localization at the same time as the combined navigation
  launch.
- Mission wait timers use simulation time. Gazebo must be running and unpaused
  for the five-second stops to elapse.

See each package README for a file-by-file overview and package-specific
commands.
# autonomous-warehouse-mobile-robot
