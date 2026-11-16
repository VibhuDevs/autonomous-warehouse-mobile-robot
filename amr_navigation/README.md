# `amr_navigation`

This package contains the saved warehouse map, Nav2 localization and
navigation launch files, navigation parameters, and behavior trees. The main
navigation launch starts the saved-map localization and navigation stack
together, with recovery behavior configured for navigation goals.

## Package contents

- `maps/warehouse_map.yaml` and `maps/warehouse_map.pgm` — saved map metadata
  and image used by AMCL and the static costmap layer.
- `config/nav2_params.yaml` — Nav2 server parameters, costmap footprint and
  layers, inflation, controller tuning, and behavior tree file paths.
- `config/amcl.yaml` — AMCL-specific configuration.
- `config/slam_toolbox.yaml` — SLAM Toolbox settings for mapping workflows.
- `behavior_trees/` — XML trees for NavigateToPose and NavigateThroughPoses,
  including replanning and recovery behavior.
- `launch/navigation.launch.py` — unified saved-map localization, Nav2, and
  autonomy mission launch.
- `launch/localization.launch.py` — standalone localization launch for use when
  running localization without the navigation launch.
- `launch/navigation_with_recovery.launch.py` — compatibility wrapper for the
  unified navigation launch.

## Build

From the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-up-to amr_navigation
source install/setup.bash
```

## Start localization and navigation

Start the simulation in another terminal first, then run:

```bash
ros2 launch amr_navigation navigation.launch.py use_sim_time:=true
```

This launch uses the saved map, starts AMCL and the Nav2 navigation servers,
loads the configured recovery behavior trees, and starts `amr_autonomy`'s
mission commander. SLAM is not enabled by this launch.

Useful launch arguments:

```bash
ros2 launch amr_navigation navigation.launch.py --show-args
```

- `map:=/path/to/map.yaml` — select another map metadata file.
- `params_file:=/path/to/nav2_params.yaml` — select another Nav2 parameter
  file.
- `use_sim_time:=true|false` — use Gazebo time (`true`) or system time
  (`false`).
- `autostart:=true|false` — automatically activate Nav2 lifecycle nodes.

For localization without navigation, use this only when no other launch is
already starting AMCL or a map server:

```bash
ros2 launch amr_navigation localization.launch.py use_sim_time:=true
```

## Send a direct goal

Nav2's `NavigateToPose` action sends one goal and runs the configured
navigation behavior tree, including its recovery logic:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: 7.31, y: -2.58, z: 0.0}, orientation: {z: -0.992, w: 0.126}}}}"
```

Use the mission command topic for pickup → aisle → return missions; see
`amr_autonomy/README.md`.

## Tuning notes

- Match the configured footprint in both costmaps to the actual base geometry.
- Inflation radius and scaling determine how strongly the planner avoids
  obstacles; tune them against the map and robot clearance.
- The local costmap is a rolling window in `odom`; the global costmap uses the
  static map in `map`.
- RViz costmap displays become populated after Nav2 publishes the costmap
  topics.
- Keep the initial pose in the map frame and consistent with the named
  `initial_pose` in `amr_autonomy/config/locations.yaml`.
