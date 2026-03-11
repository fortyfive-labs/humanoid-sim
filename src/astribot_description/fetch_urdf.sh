#!/bin/bash
# Fetch the Astribot S1 URDF and meshes from fiveages-sim/robot_descriptions.
# Run this ONCE inside the container:
#   bash /workspace/src/astribot_description/fetch_urdf.sh
#
# Note: the upstream URDF uses .glb mesh files for visuals. Gazebo Classic 11
# cannot render .glb meshes, so the robot's 3D model won't appear in Gazebo or RViz2.
# Physics simulation and all sensor plugins work correctly regardless.

set -e
DEST=/workspace/src/astribot_description

echo "==> Cloning fiveages-sim/robot_descriptions (shallow)..."
git clone --depth=1 \
    https://github.com/fiveages-sim/robot_descriptions.git /tmp/fiveages_repos

SRC=/tmp/fiveages_repos/humanoid/Astribot/astribot_s1_description

echo "==> Copying URDF..."
cp "$SRC/urdf/astribot_s1.urdf" "$DEST/urdf/astribot_s1_base.urdf"

echo "==> Copying meshes..."
cp -r "$SRC/meshes/"* "$DEST/meshes/"

echo "==> Fixing mesh paths..."
sed -i 's|package://astribot_s1_description/|package://astribot_description/|g' \
    "$DEST/urdf/astribot_s1_base.urdf"
sed -i 's|filename="meshes/|filename="package://astribot_description/meshes/|g' \
    "$DEST/urdf/astribot_s1_base.urdf"

echo "==> Cleaning up..."
rm -rf /tmp/fiveages_repos

echo ""
echo "==> Verifying URDF..."
check_urdf "$DEST/urdf/astribot_s1_base.urdf" 2>&1 | tail -3 || true

echo ""
echo "Done! Run: colcon build --packages-select astribot_description sim_gazebo"
