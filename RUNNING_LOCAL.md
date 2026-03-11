# Running Python Scripts Locally (macOS)

To run the robot monitor script natively on macOS (outside Docker), you need ROS2 installed. We'll use **Conda or Homebrew for ROS2**.

## Setup (one-time)

### Option A: Install ROS2 via Conda (Recommended)

```bash
# Create a ROS2 environment
conda create -n ros2 python=3.10
conda activate ros2

# Install ROS2 Humble packages
conda install -c robostack-staging -c conda-forge ros-humble-rclpy ros-humble-sensor-msgs
pip install rich  # pure Python deps for the monitor script
```

### Option B: Install ROS2 via Homebrew

```bash
# Add ROS tap
brew tap ros/ros2

# Install ROS2 Humble (this takes a while)
brew install ros-humble-desktop

# Source ROS2 environment (add this to your ~/.zshrc or ~/.bashrc)
source /opt/homebrew/opt/ros-humble/setup.zsh  # for zsh
# or
source /opt/homebrew/opt/ros-humble/setup.bash  # for bash

# Install pure Python deps
pip install rich
```

## Running Locally

```bash
# Terminal 1: Start simulation in Docker (headless — no GUI needed for monitor)
docker compose run --service-ports sim bash -c "
  source /opt/ros/humble/setup.bash &&
  source /workspace/install/setup.bash &&
  ros2 launch sim_gazebo sim.launch.py gui:=false"

# Terminal 2: Run monitor locally on macOS
cd /path/to/humanoid-sim   # must be in the project root
conda activate ros2
export ROS_DOMAIN_ID=42

# Run the monitor (rich is installed in conda env, rclpy is available via conda)
python3 src/robot_control/robot_monitor.py
```

## Alternative: Use Docker Exec (No Local Install)

If you don't want to install ROS2 locally, run everything inside the container:

```bash
# Terminal 1: Start simulation (with or without GUI)
docker compose run --service-ports sim bash /workspace/start_sim.sh

# Terminal 2: Run the monitor inside the same container
docker exec -it $(docker ps -qf ancestor=sim_robo:humble) bash -c "
  source /opt/ros/humble/setup.bash &&
  source /workspace/install/setup.bash &&
  cd /workspace &&
  uv sync --python /usr/bin/python3 --quiet &&
  source .venv/bin/activate &&
  python3 src/robot_control/robot_monitor.py"
```

## Networking Notes

- The `docker-compose.yml` exposes ports 7400-7500 for DDS communication
- Both the container and host use `ROS_DOMAIN_ID=42` to communicate
- DDS discovery should work automatically over UDP multicast
- The `--service-ports` flag is required with `docker compose run` to publish ports

## Troubleshooting

If ROS2 topics aren't visible from macOS:

```bash
# Check if topics are visible
ros2 topic list

# Check DDS discovery
ros2 daemon stop
ros2 daemon start

# Try with FastDDS instead of CycloneDDS
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```
