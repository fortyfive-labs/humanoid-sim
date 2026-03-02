# humanoid-sim

**humanoid-sim** is a turnkey ROS2 simulation environment for humanoid robots, designed to run entirely inside Docker on macOS with no native ROS installation required.

It currently supports the **Unitree G1** and **Astribot S1**, and is built to extend — adding a new robot takes one config entry and a sensor XACRO file. Each robot is equipped with five fully functional sensors out of the box: a 2D LiDAR, a 3D LiDAR, an RGB camera, a depth camera with point cloud output, and an IMU — all publishing on standard ROS2 topic names and message types.

The focus is on **sensor data workflows**: collecting, recording, and processing perception data in simulation before deploying to hardware. Bags can be recorded in MCAP or SQLite3 format directly from the launch command. Because all topics use standard `sensor_msgs` types and the same names as the physical robots, code written against the simulation runs on real hardware without modification — only `use_sim_time:=false` needs to change.

---

Each robot ships with five sensors:

| Topic | Type | Source |
|-------|------|--------|
| `/scan` | `LaserScan` | 2D LiDAR |
| `/points` | `PointCloud2` | 3D LiDAR |
| `/camera/image_raw` | `Image` | RGB camera |
| `/camera/depth/image_raw` | `Image` | Depth image |
| `/camera/depth/points` | `PointCloud2` | Depth point cloud |
| `/imu/data` | `Imu` | IMU |
| `/joint_states` | `JointState` | All joints |

---

## Prerequisites

| Tool | Install |
|------|---------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop) | Required |
| [XQuartz](https://www.xquartz.org) | Only if you want the Gazebo GUI |

**XQuartz one-time setup** (GUI only):
1. After install: XQuartz → Preferences → Security → ✓ *Allow connections from network clients*
2. Log out and back in

---

## Setup

### 1. Clone

```bash
git clone https://github.com/fortyfive-labs/humanoid-sim.git
cd humanoid-sim
```

### 2. Build the Docker image

```bash
docker compose build
```

First build takes ~5–10 min. Subsequent builds are cached.

### 3. Create the Gazebo model cache volume

```bash
docker volume create sim_robo_gazebo-cache
```

This persists Gazebo's downloaded model database across container restarts. Without it, the first launch takes ~8 min every time.

### 4. Build the ROS2 packages

```bash
# Start the container
docker compose run --rm sim bash

# Inside the container
cd /workspace
colcon build
source install/setup.bash
```

---

## Launching

> **Before every session**, run on the macOS host:
> ```bash
> xhost +localhost
> ```

```bash
# Start the container (if not already inside)
docker compose run --rm sim bash

# Source the workspace (inside container)
source /opt/ros/humble/setup.bash
source /workspace/install/setup.bash
```

### Launch commands

```bash
# Unitree G1 (default)
ros2 launch sim_gazebo sim.launch.py

# Astribot S1
ros2 launch sim_gazebo sim.launch.py robot:=astribot

# Headless (no GUI window)
ros2 launch sim_gazebo sim.launch.py robot:=astribot gui:=false

# Record sensor data to an MCAP bag
ros2 launch sim_gazebo sim.launch.py robot:=astribot record:=true

# RViz2 preview only (no Gazebo)
ros2 launch g1_description display.launch.py
ros2 launch astribot_description display.launch.py
```

### All launch arguments

| Argument | Default | Options |
|----------|---------|---------|
| `robot` | `g1` | `g1`, `astribot` |
| `gui` | `true` | `true`, `false` |
| `paused` | `false` | `true`, `false` |
| `record` | `false` | `true`, `false` |
| `bag_format` | `mcap` | `mcap`, `sqlite3` |
| `bag_path` | *(auto)* | any path |

Bags are saved to `bags/` in the repo root (volume-mounted, visible on macOS).

---

## Verifying topics

```bash
# Inside the container
ros2 topic list
ros2 topic echo /scan
ros2 topic hz /imu/data
```

First launch takes ~90 s for gzserver to initialize (software rendering, no GPU). Topics appear after the robot spawns.

---

## Project structure

```
humanoid-sim/
├── Dockerfile                     # Ubuntu 22.04 + ROS2 Humble + Gazebo Classic
├── docker-compose.yml
├── entrypoint.sh
├── GUIDE.md                       # Full reference: launch, subscribe, record, real robot
└── src/
    ├── g1_description/            # Unitree G1 URDF, meshes, sensor XACRO
    ├── g1_gazebo/                 # Gazebo world
    ├── astribot_description/      # Astribot S1 URDF, meshes, sensor XACRO
    ├── sim_gazebo/                # Unified multi-robot launcher
    └── g1_apps/                   # Template subscriber and joint controller nodes
```

---

## Adding a new robot

1. Create `src/<name>_description/` with `urdf/<name>_sensors.urdf.xacro`
2. Add an entry to `ROBOT_CONFIGS` in `src/sim_gazebo/launch/sim.launch.py`
3. `colcon build --packages-select sim_gazebo <name>_description`

See `GUIDE.md` for the full sensor setup reference and real-robot migration guide.
