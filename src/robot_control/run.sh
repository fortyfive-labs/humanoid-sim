#!/bin/bash
# Run robot monitor (uv manages deps from root pyproject.toml)

cd "$(dirname "$0")/../.."

# Ensure dependencies are installed
uv sync --quiet 2>/dev/null || true

# Run the monitor
python3 src/robot_control/robot_monitor.py
