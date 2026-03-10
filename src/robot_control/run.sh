#!/bin/bash
# Run robot monitor (uv manages deps from root pyproject.toml)

cd "$(dirname "$0")/../.."

# Ensure dependencies are installed (pin to system Python 3.10 for ROS2 compatibility)
uv sync --python /usr/bin/python3 --quiet 2>/dev/null || true
source .venv/bin/activate 2>/dev/null || true

# Run the monitor
python3 src/robot_control/robot_monitor.py
