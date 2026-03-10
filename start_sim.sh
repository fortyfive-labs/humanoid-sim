#!/bin/bash
# Start Gazebo simulation with VNC display.
# Connect with any VNC viewer to localhost:5900 (no password).

set -e

# 1. Start virtual framebuffer (headless X display on :99)
Xvfb :99 -screen 0 1600x1000x24 &
sleep 1

# 2. Start VNC server — no password, port 5900
x11vnc -display :99 -forever -nopw -rfbport 5900 -quiet &
sleep 1

echo "VNC server running on port 5900 — connect with any VNC viewer to localhost:5900"

# 3. Source ROS and launch simulation
source /opt/ros/humble/setup.bash
source /workspace/install/setup.bash
ros2 launch g1_gazebo g1_sim.launch.py
