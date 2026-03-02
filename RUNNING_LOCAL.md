# Running Python Scripts Locally (macOS)

To run the robot monitor script natively on macOS (outside Docker), you need ROS2 installed. We'll use **Conda or Homebrew for ROS2** and **uv for Python dependencies**.

## Setup (one-time)

### Option A: Install ROS2 via Conda (Recommended)

```bash
# Create a ROS2 environment
conda create -n ros2 python=3.11
conda activate ros2

# Install ROS2 Humble packages
conda install -c robostack-staging ros-humble-desktop
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
```

### Install uv (if you don't have it)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Running Locally

```bash
# Terminal 1: Start simulation in Docker
docker compose up -d
docker compose exec sim bash -c "source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash && ros2 launch sim_gazebo sim.launch.py gui:=false"

# Terminal 2: Run monitor locally on macOS
conda activate ros2
export ROS_DOMAIN_ID=42

# Install dependencies with uv (one-time)
uv sync

# Run the monitor
python3 src/robot_control/robot_monitor.py

# Or use the convenience script:
./src/robot_control/run.sh
```

## Alternative: Use Docker Exec (No Local Install)

If you don't want to install ROS2 locally:

```bash
# After starting the simulation
docker exec -it sim_robo bash -c "cd /workspace/src/robot_control && uv run --system robot_monitor.py"
```

## Networking Notes

- The docker-compose.yml exposes ports 7400-7500 for DDS communication
- Both the container and host use `ROS_DOMAIN_ID=42` to communicate
- DDS discovery should work automatically over UDP multicast

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
