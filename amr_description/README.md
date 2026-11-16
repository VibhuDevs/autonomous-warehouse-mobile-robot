# `amr_description`

This package contains the robot model and the main simulation launch. It
publishes the robot description and transforms, starts Gazebo, spawns the
robot, loads the ROS-Gazebo bridge and drive controllers, and opens RViz.

## Package contents

- `urdf/amr.urdf.xacro` — top-level Xacro robot description.
- `urdf/amr_base.xacro` — base and wheel/caster geometry and joints.
- `urdf/amr.ros2_control.xacro` — ROS 2 control interfaces.
- `urdf/amr_gazebo.xacro` — Gazebo-specific simulation plugins and settings.
- `urdf/common_properties.xacro` — shared materials and physical properties.
- `launch/amr_launch.xml` — launches Gazebo, robot state publisher, robot
  spawning, controller spawners, bridge, and RViz.
- `rviz/amr.rviz` — RViz view configuration, including map, robot, scan, TF,
  and costmap displays.

## Build

From the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-up-to amr_description
source install/setup.bash
```

## Launch the simulation

```bash
ros2 launch amr_description amr_launch.xml
```

`start_localization` defaults to `false`; the combined Nav2 launch is intended
to own localization, preventing duplicate map/localization nodes. The launch
declares a `start_slam` argument, but currently does not use it to start SLAM
Toolbox. Do not rely on `start_slam:=true` to begin mapping.

Do not run standalone localization from this launch alongside the combined
navigation launch.

## Robot model and controls

The model uses two driven wheels with passive casters. If changing wheel
positions, dimensions, joints, or control interfaces, keep the matching
geometry and limits in `amr_bringup/config/amr_controllers.yaml` consistent.
The Gazebo world selection and spawn parameters are configured in
`launch/amr_launch.xml`.
