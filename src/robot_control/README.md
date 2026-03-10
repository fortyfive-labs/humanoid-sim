# robot-control

Python scripts for monitoring and controlling robots in the humanoid-sim environment.

## Setup

Dependencies are managed by [uv](https://docs.astral.sh/uv/) via the root `pyproject.toml`, while ROS2 packages (rclpy, sensor_msgs) come from the system installation.

```bash
# Inside the Docker container or on macOS with ROS2

# Install dependencies (run from project root)
cd /workspace  # or project root on macOS
uv sync

# Run the monitor
python3 src/robot_control/robot_monitor.py

# Or use the convenience script
./src/robot_control/run.sh
```

## Running with the Simulation

**With GUI (VNC):**
```bash
# Terminal 1: Start simulation with VNC display
docker compose run --service-ports sim bash /workspace/start_sim.sh
# Connect TigerVNC to localhost:5900 to see Gazebo

# Terminal 2: Run the monitor inside the container
docker exec -it $(docker ps -qf ancestor=sim_robo:humble) bash -c "
  source /opt/ros/humble/setup.bash &&
  source /workspace/install/setup.bash &&
  cd /workspace && python3 src/robot_control/robot_monitor.py"
```

**Headless (no GUI):**
```bash
# Terminal 1: Start simulation without GUI
docker compose run --service-ports sim bash -c "
  source /opt/ros/humble/setup.bash &&
  source /workspace/install/setup.bash &&
  ros2 launch sim_gazebo sim.launch.py gui:=false"

# Terminal 2: Run the monitor
docker exec -it $(docker ps -qf ancestor=sim_robo:humble) bash -c "
  source /opt/ros/humble/setup.bash &&
  source /workspace/install/setup.bash &&
  cd /workspace && python3 src/robot_control/robot_monitor.py"
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

- `rich` - Terminal UI library (installed via uv)
- `rclpy` - ROS2 Python client (provided by ROS2 Humble system installation)
- `sensor_msgs` - ROS2 sensor message types (provided by ROS2 system installation)
