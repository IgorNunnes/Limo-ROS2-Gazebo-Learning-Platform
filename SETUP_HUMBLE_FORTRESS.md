# ROS 2 Humble + Gazebo Fortress setup

This repository was cloned from a Gazebo Classic simulation. The installer below prepares a fresh Ubuntu 22.04 machine with ROS 2 Humble, Gazebo Fortress, Cartographer, RViz, colcon, rosdep, and the ROS/Gazebo bridge packages.

Run from the repository root:

```bash
chmod +x scripts/install_humble_fortress_deps.sh
./scripts/install_humble_fortress_deps.sh
source /opt/ros/humble/setup.bash
```

Then install package dependencies and build:

```bash
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble \
  --skip-keys "gazebo libgazebo_ros rviz"
colcon build --symlink-install
source install/setup.bash
```

Why the skipped keys matter:

- `limo_car/package.xml` still declares Gazebo Classic dependencies: `gazebo`, `libgazebo_ros`, and `rviz`.
- Fortress uses Gazebo Sim packages (`gz-fortress`) and ROS integration through `ros_gz`/`ros_ign`.
- The existing launch files call Classic nodes such as `gazebo_ros` and `spawn_entity.py`.
- The existing xacro files reference Classic plugins such as `libgazebo_ros_ray_sensor.so`, `libgazebo_ros_imu_sensor.so`, and Ackermann/diff-drive Classic plugins.

After the build succeeds, the main Gazebo Fortress differential-drive simulation is:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch limo_description limo_diff_fortress.launch.py
```

The educational RoboCup@Work-style arena is available with:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch limo_description limo_atwork_fortress.launch.py
```

The integrated work-scenario launch starts Gazebo Fortress, the differential Limo, the ROS/Gazebo
bridges, Cartographer SLAM, and RViz configured for navigation:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch limo_car diff_limo_work_scenario.launch.py
```

Useful launch switches:

```bash
ros2 launch limo_car diff_limo_work_scenario.launch.py rviz:=false
ros2 launch limo_car diff_limo_work_scenario.launch.py slam:=false
```

The first arena version uses a 6 m x 4 m mat, 30 cm physical walls, 0.8 m x 0.5 m workstations,
0/5/10/15 cm service-area heights, a 70 cm rotating-table placeholder, 2B containers, a shelf,
green tape markers, and physical obstacles while preserving rulebook-style 0.8 m navigation paths.

For headless automated tests in this arena:

```bash
ros2 launch limo_description limo_atwork_fortress.launch.py \
  gz_args:="-r -s $(ros2 pkg prefix limo_description)/share/limo_description/worlds/limo_atwork_educational.sdf"
```

Useful ROS topics:

- `/cmd_vel`: send `geometry_msgs/msg/Twist` commands to the differential drive.
- `/odom`: odometry derived from the Gazebo Fortress `odom -> base_footprint` transform.
- `/scan`: 2D lidar scan.
- `/imu`: IMU data.
- `/joint_states`: wheel joint state bridge.

For a headless run suitable for automated tests or ML loops:

```bash
ros2 launch limo_description limo_diff_fortress.launch.py \
  gz_args:="-r -s $(ros2 pkg prefix limo_description)/share/limo_description/worlds/limo_empty.sdf"
```

Test a velocity command:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.25}, angular: {z: 0.3}}" --rate 10
```

The RViz/model description parts can be tested with:

```bash
ros2 launch limo_car display_ackermann.launch.py
```

The older Ackermann Gazebo Fortress launch is available with:

```bash
ros2 launch limo_car ackermann_fortress.launch.py
```

That launch is retained only as a compatibility experiment. The robust Fortress path is
`limo_description limo_diff_fortress.launch.py`.

The original full simulation launch:

```bash
ros2 launch limo_car ackermann_gazebo.launch.py
```

is still the Gazebo Classic path. To run natively in Fortress, the robot spawn, sensor plugins, and drive controller need to be ported to Gazebo Sim / `ros_gz`.
