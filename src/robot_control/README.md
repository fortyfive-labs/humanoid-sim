# robot-control

Python scripts for monitoring and controlling robots in the humanoid-sim environment.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management.

```bash
# Inside the Docker container
cd /workspace/src/robot_control

# Run the robot monitor
uv run robot_monitor.py
```

## Scripts

### robot_monitor.py

Live-updating dashboard showing:
- 📷 RGB Camera feed stats
- 🔲 Depth camera data
- 📡 IMU acceleration
- 📊 2D LiDAR scans
- 🗺️ 3D LiDAR point clouds
- 👋 Joint control commands

The script also sends simple wave commands to the robot's right arm.

## Dependencies

- `rich` - Terminal UI library for the live dashboard
- `rclpy` - ROS2 Python client (provided by ROS2 Humble installation)
- `sensor_msgs` - ROS2 sensor message types (provided by ROS2)
