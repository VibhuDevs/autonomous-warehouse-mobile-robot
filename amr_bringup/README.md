# `amr_bringup`

This package contains configuration shared by the simulated robot's ROS 2
control and Gazebo integration. It does not provide a standalone launch file;
the main simulation launch in `amr_description` consumes these files.

## Package contents

- `config/amr_controllers.yaml` — controller-manager, joint-state broadcaster,
  and differential-drive controller settings, including wheel geometry and
  velocity limits.
- `config/amr_gazebo_bridge.yaml` — Gazebo/ROS topic bridge mappings for
  simulation data such as clock, sensor data, and drive commands.
- `CMakeLists.txt` — installs the `config/` directory into the package share.
- `package.xml` — package metadata and dependencies.

## Build

From the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-up-to amr_bringup
source install/setup.bash
```

## Use the configuration

Start the simulation launch, which loads the controller and bridge settings:

```bash
ros2 launch amr_description amr_launch.xml
```

For controller tuning, edit `config/amr_controllers.yaml`. Ensure wheel
separation and wheel radius agree with the robot model in `amr_description`;
inconsistent geometry can cause odometry errors or apparent wheel slip. For
topic integration, edit `config/amr_gazebo_bridge.yaml` and keep the ROS topic
names aligned with the sensor and controller topics used elsewhere.
