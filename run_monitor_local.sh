#!/bin/bash
# Run robot monitor locally on macOS (outside Docker)

# Source ROS2 from Homebrew (adjust for zsh/bash)
if [ -f /opt/homebrew/opt/ros-humble/setup.zsh ]; then
    source /opt/homebrew/opt/ros-humble/setup.zsh
elif [ -f /opt/homebrew/opt/ros-humble/setup.bash ]; then
    source /opt/homebrew/opt/ros-humble/setup.bash
else
    echo "Error: ROS2 Humble not found. Install with: brew install ros-humble-desktop"
    exit 1
fi

# Set ROS environment variables to match container
export ROS_DOMAIN_ID=42
export ROS_LOCALHOST_ONLY=0

# Run with uv (will install rich if needed, uses system ROS2)
cd "$(dirname "$0")/src/robot_control"
uv run --system robot_monitor.py
