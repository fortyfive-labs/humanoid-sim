#!/bin/bash
set -e

source /opt/ros/humble/setup.bash

if [ -f /workspace/install/setup.bash ]; then
    source /workspace/install/setup.bash
fi

# Always start Xvfb :99 for Gazebo's render engine (needed even headless).
# gzserver blocks until it gets a working GLX context; XQuartz on Mac does
# not provide the Mesa fbConfigs Gazebo requires, so we use the virtual fb.
# Users who want the Gazebo GUI on their Mac screen can re-export DISPLAY
# after entering the container (e.g. export DISPLAY=host.docker.internal:0).
Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset &
for i in $(seq 1 20); do
    xdpyinfo -display :99 >/dev/null 2>&1 && break
    sleep 0.2
done
export DISPLAY=:99

exec "$@"
