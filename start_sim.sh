#!/bin/bash
# Start Gazebo simulation with VNC display.
# Connect with any VNC viewer to localhost:5900 (no password).
#
# NOTE: Xvfb :99 is already started by the container entrypoint.
# This script only starts x11vnc (VNC server) and the simulation.

set -e

# Guard: workspace must be built before launching
if [ ! -f /workspace/install/setup.bash ]; then
    echo "ERROR: ROS2 workspace not built."
    echo "Run 'docker compose run --rm sim bash' then 'colcon build && source install/setup.bash' first."
    exit 1
fi

# 1. Start VNC server — no password, port 5900
#    Xvfb :99 is already running (started by /entrypoint.sh at container startup).
x11vnc -display :99 -forever -nopw -rfbport 5900 -quiet &
sleep 1

echo "VNC server running on port 5900 — connect with any VNC viewer to localhost:5900"
echo "NOTE: Gazebo GUI takes 3-5 minutes to appear under software rendering. Please wait."

# 2. Source ROS and launch simulation
source /opt/ros/humble/setup.bash
source /workspace/install/setup.bash
ros2 launch sim_gazebo sim.launch.py
