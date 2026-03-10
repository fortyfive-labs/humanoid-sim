# sim_robo — Simulation Guide

ROS2 Humble + Gazebo Classic simulation for humanoid robots on macOS (Docker).
Supports: **Unitree G1**, **Astribot S1** (add more via `ROBOT_CONFIGS` in `sim_gazebo/launch/sim.launch.py`).

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Launching the Simulation](#2-launching-the-simulation)
3. [Subscribing to Topics](#3-subscribing-to-topics)
4. [Recording Bags](#4-recording-bags)
5. [Migrating to the Real Robot](#5-migrating-to-the-real-robot)

---

## 1. Prerequisites

### macOS host (one-time setup)

```bash
# Install Docker Desktop (if not already installed)
# https://docs.docker.com/desktop/install/mac-install/

# Build the Docker image (~5 min first time)
cd /path/to/sim_robo
docker compose build
```

### Before every session — allow X11 connections

Even in headless mode (`gui:=false`) this is needed to connect to the container:

```bash
# On macOS host (not inside Docker)
xhost +localhost
```

> If you also want to see Gazebo/RViz2 visually, install XQuartz first:
> `brew install --cask xquartz`, then enable **XQuartz → Preferences → Security → Allow connections from network clients**, and log out/back in.

---

## 2. Launching the Simulation

### Start the container

```bash
cd /path/to/sim_robo
docker compose run --rm sim bash
```

This drops you into a shell at `/workspace` with ROS2 sourced.

> **Important for `docker exec` sessions:** `docker exec` bypasses the entrypoint and does not set `DISPLAY=:99` automatically.
> Always start `docker exec` commands with:
> ```bash
> docker exec <container_name> bash -c "export DISPLAY=:99; source /opt/ros/humble/setup.bash; source /workspace/install/setup.bash; ..."
> ```

### Build packages (only needed after code changes)

```bash
# Inside the container
cd /workspace
colcon build --packages-select g1_description g1_gazebo astribot_description sim_gazebo g1_apps
source install/setup.bash
```

### Launch arguments

| Argument | Default | Options | Description |
|----------|---------|---------|-------------|
| `robot` | `g1` | `g1`, `astribot` | Which robot to simulate |
| `gui` | `true` | `true`, `false` | Show Gazebo window via VNC |
| `paused` | `false` | `true`, `false` | Start Gazebo paused |
| `use_sim_time` | `true` | `true`, `false` | Use Gazebo clock for all nodes |
| `rosbag` | `false` | `true`, `false` | Record sensor topics to a bag file |
| `bag_format` | `mcap` | `mcap`, `sqlite3` | Bag storage format |
| `bag_path` | *(auto)* | any path | Custom bag output path |

### Launch examples

```bash
# G1 (default)
ros2 launch sim_gazebo sim.launch.py

# Astribot, headless
ros2 launch sim_gazebo sim.launch.py robot:=astribot gui:=false

# G1, paused (inspect robot before physics runs)
ros2 launch sim_gazebo sim.launch.py robot:=g1 paused:=true

# Astribot, headless, recording an MCAP bag
ros2 launch sim_gazebo sim.launch.py robot:=astribot gui:=false rosbag:=true

# G1 with a named bag path
ros2 launch sim_gazebo sim.launch.py rosbag:=true bag_path:=/workspace/bags/my_run
```

### RViz2 preview (no Gazebo)

```bash
ros2 launch g1_description display.launch.py        # Unitree G1
ros2 launch astribot_description display.launch.py  # Astribot S1
```

### How to restart

```bash
# Inside the container
pkill -f gzserver          # stop Gazebo (Ctrl-C the launch if it's in the foreground)
ros2 launch sim_gazebo sim.launch.py robot:=astribot gui:=false   # relaunch
```

Startup time is ~90 s on a warm cache (models already downloaded).

---

## 3. Subscribing to Topics

### Sensor topic reference

| Topic | Message type | Target rate | Description |
|-------|-------------|-------------|-------------|
| `/scan` | `sensor_msgs/LaserScan` | 15 Hz | 2D LiDAR, 360° |
| `/points` | `sensor_msgs/PointCloud2` | 10 Hz | 3D LiDAR (sparse, wide FOV) |
| `/camera/image_raw` | `sensor_msgs/Image` | 30 Hz | RGB camera 640×480 |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | 15 Hz | Depth image (32FC1, metres) |
| `/camera/depth/points` | `sensor_msgs/PointCloud2` | 15 Hz | Dense point cloud from depth camera |
| `/imu/data` | `sensor_msgs/Imu` | 200 Hz | IMU |
| `/joint_states` | `sensor_msgs/JointState` | 50 Hz | All DOF positions |
| `/tf` | `tf2_msgs/TFMessage` | — | Transform tree |
| `/clock` | `rosgraph_msgs/Clock` | — | Simulation time |

> Actual rates are lower in software rendering (no GPU) — normal for Docker on macOS.

### Inside the container

```bash
# List all topics
ros2 topic list

# Print messages
ros2 topic echo /scan
ros2 topic echo /imu/data

# Check publish rate
ros2 topic hz /scan
ros2 topic hz /camera/image_raw

# Topic metadata
ros2 topic info /points
```

### From a second terminal on the same container

```bash
# Open a second shell into the running container
docker exec -it sim_robo bash
# (or: docker compose exec sim bash)
export DISPLAY=:99
source /opt/ros/humble/setup.bash && source /workspace/install/setup.bash
ros2 topic echo /imu/data
```

### From macOS Python (outside Docker)

Use **rosbridge** if you want to subscribe from a Mac Python script without installing ROS2.

**Step 1 — install rosbridge inside the container:**

```bash
# Inside the container (one-time)
apt-get install -y ros-humble-rosbridge-suite
```

**Step 2 — run rosbridge alongside the simulation:**

```bash
# Inside the container (separate terminal)
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
# Listens on ws://localhost:9090
```

**Step 3 — subscribe from macOS Python:**

```bash
# On macOS host
pip install roslibpy
```

```python
import roslibpy

client = roslibpy.Ros(host='localhost', port=9090)
client.run()

def on_scan(msg):
    ranges = msg['ranges']
    print(f'LiDAR: {len(ranges)} rays, min={min(ranges):.2f} m')

listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
listener.subscribe(on_scan)

input('Press Enter to stop...')
listener.unsubscribe()
client.terminate()
```

---

## 4. Recording Bags

### Automatic recording via launch argument

```bash
# MCAP format (default) — auto-named: /workspace/bags/<robot>_<YYYYMMDD_HHMMSS>/
ros2 launch sim_gazebo sim.launch.py robot:=astribot rosbag:=true

# SQLite3 format
ros2 launch sim_gazebo sim.launch.py rosbag:=true bag_format:=sqlite3

# Custom output path
ros2 launch sim_gazebo sim.launch.py rosbag:=true bag_path:=/workspace/bags/test_run
```

Bags land in `sim_robo/bags/` on your Mac (volume-mounted from `/workspace/bags/` inside the container).

**Topics recorded:** `/scan`, `/points`, `/imu/data`, `/camera/image_raw`, `/camera/depth/image_raw`, `/camera/depth/points`, `/joint_states`, `/tf`, `/tf_static`, `/clock`

### Manual recording (any topics, any time)

```bash
# Inside the container
ros2 bag record -s mcap -o /workspace/bags/my_bag \
    /scan /points /imu/data /camera/image_raw /joint_states /tf /tf_static /clock

# Record everything
ros2 bag record -s mcap -a -o /workspace/bags/everything
```

### Playback

```bash
# Inside the container
ros2 bag play /workspace/bags/astribot_20260227_143000

# Loop playback
ros2 bag play --loop /workspace/bags/astribot_20260227_143000

# Inspect bag contents
ros2 bag info /workspace/bags/astribot_20260227_143000
```

### MCAP vs SQLite3

| | MCAP | SQLite3 |
|-|------|---------|
| Extension | `.mcap` | `.db3` + `metadata.yaml` |
| Read with | Foxglove Studio, `ros2 bag play` | `ros2 bag play` |
| Performance | Better for large/high-rate data | Simpler, widely supported |
| Seeking | Fast random access | Slower |

**Foxglove Studio** (free desktop app) can open `.mcap` files directly for visualization — panels for image, point cloud, plot, 3D scene, etc.

---

## 5. Migrating to the Real Robot

Running the same ROS2 nodes on the real robot requires only a few changes — no modifications to your `g1_apps` code.

### What stays the same

- All topic names (`/scan`, `/points`, `/imu/data`, `/camera/image_raw`, `/joint_states`)
- All message types
- All your subscriber/publisher nodes in `g1_apps`

### What changes

#### Unitree G1 — real robot bridge

The real G1 uses the **Unitree ROS2 SDK** (`unitree_ros2`) to bridge hardware → ROS2 topics.

**Step 1 — clone and build unitree_ros2 on your development machine:**

```bash
# On a machine with ROS2 Humble installed (Ubuntu 22.04, NOT inside this Docker container)
mkdir -p ~/unitree_ws/src && cd ~/unitree_ws/src
git clone https://github.com/unitreerobotics/unitree_ros2.git
cd ~/unitree_ws
colcon build
source install/setup.bash
```

**Step 2 — network setup:**

Connect your machine to the G1's onboard network (Ethernet or WiFi).
The G1's default IP is `192.168.123.161`.

```bash
# Verify connection
ping 192.168.123.161
```

**Step 3 — configure DDS (CycloneDDS):**

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///path/to/cyclonedds.xml
```

The `cyclonedds.xml` should specify the network interface connected to the robot. Example:

```xml
<CycloneDDS>
  <Domain>
    <General>
      <NetworkInterfaceAddress>192.168.123.xxx</NetworkInterfaceAddress>
    </General>
  </Domain>
</CycloneDDS>
```

**Step 4 — run your nodes:**

```bash
# Launch the unitree bridge (publishes /joint_states, /imu/data, etc.)
ros2 launch unitree_ros2 unitree_ros2_launch.py

# Run your programs — identical command to simulation
ros2 run g1_apps sensor_monitor
ros2 run g1_apps joint_commander
```

The only flag to change is `use_sim_time`:

```python
# In your node, when creating:
Node(use_sim_time=False)   # real robot
Node(use_sim_time=True)    # simulation
```

Or pass it at runtime:

```bash
ros2 run g1_apps sensor_monitor --ros-args -p use_sim_time:=false
```

#### Key differences to be aware of

| | Simulation | Real G1 |
|-|-----------|---------|
| `use_sim_time` | `true` | `false` |
| Sensor rates | Lower (software rendering) | Full rate (hardware) |
| Joint control | Publishes to `/joint_states` freely | Must use safe velocity/torque limits |
| Emergency stop | Kill the launch | Physical e-stop button |
| LiDAR driver | Gazebo plugin | `unitree_lidar_ros2` or `livox_ros_driver2` |
| Camera driver | Gazebo plugin | RealSense SDK (`realsense2_camera`) |

### Recommended workflow

1. Develop and test in simulation (`use_sim_time:=true`)
2. Record a representative bag from simulation
3. Replay the bag to test your processing offline: `ros2 bag play --loop my_bag`
4. When logic is validated, connect to the real robot and switch `use_sim_time:=false`
