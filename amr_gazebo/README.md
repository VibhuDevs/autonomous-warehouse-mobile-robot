# `amr_gazebo`

This package provides warehouse world files for Gazebo Sim. The main launch in
`amr_description` selects a world and starts Gazebo with the robot.

## Package contents

- `worlds/warehouse_obstacles.sdf` — warehouse environment with obstacles,
  used by default for navigation testing.
- `worlds/warehouse_no_obstacles.sdf` — simpler warehouse environment without
  the obstacle layout.
- `CMakeLists.txt` — installs the `worlds/` directory into the package share.
- `package.xml` — package metadata and dependencies.

## Build

From the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-up-to amr_gazebo
source install/setup.bash
```

## Launch a world

The recommended command starts Gazebo and the robot together:

```bash
ros2 launch amr_description amr_launch.xml
```

The default world path is set in `amr_description/launch/amr_launch.xml`.
Change that launch file's `world` value to select another installed SDF world.
The simulation sets `GZ_SIM_RESOURCE_PATH` to this package's `worlds/` directory
so Gazebo can resolve world resources.
