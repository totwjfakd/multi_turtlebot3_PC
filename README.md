# TurtleBot3 Multi-Robot Notes

## Original Repository
- The original upstream repository is `ROBOTIS-GIT/turtlebot3`.
- Upstream URL: https://github.com/ROBOTIS-GIT/turtlebot3
- This repository contains local/custom changes for multi-robot navigation.

## Robot Setup Reference
- For TurtleBot3 SBC setup, refer to:
  - https://emanual.robotis.com/docs/en/platform/turtlebot3/sbc_setup/#sbc-setup

## Multi-Robot Navigation2 (Shared Map) Quick Start

### 1) Shared map server
```bash
ros2 launch turtlebot3_navigation2 navigation2_shared_map_server.launch.py map:=<path_to_map_yaml>
```

### 2) Per-robot bringup (teleop)
```bash
ros2 run turtlebot3_teleop teleop_keyboard namespace:=<namespace>
```

### 3) Per-robot navigation
```bash
ros2 launch turtlebot3_navigation2 navigation2_robot_navigation.launch.py \
  namespace:=<namespace> \
  shared_map_topic:=/map \
  use_sim_time:=false \
  autostart:=true \
  use_composition:=False
```
