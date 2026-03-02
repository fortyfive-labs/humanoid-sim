#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=14.3.3",
# ]
# ///
"""
robot_monitor.py — Basic robot interaction demo

This script demonstrates:
1. Reading sensor data (IMU, camera, LiDAR, depth)
2. Sending simple joint commands to make the robot wave
3. Live-updating display using Rich library

Usage:
    # Inside the Docker container, after launching the simulation:
    uv run --with-requirements <(echo rich) --system robot_monitor.py
"""

import math
import threading
from datetime import datetime
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from sensor_msgs.msg import Image, Imu, JointState, LaserScan, PointCloud2
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout


# Best-effort QoS for sensor data
SENSOR_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=5,
)


class SimpleRobotController(Node):
    """Simple robot controller that reads sensors and sends joint commands"""

    def __init__(self):
        super().__init__('simple_robot_controller')

        # Data storage for sensors
        self._lock = threading.Lock()
        self._sensor_data = {
            'camera': {'time': None, 'shape': None, 'count': 0},
            'depth': {'time': None, 'shape': None, 'count': 0},
            'imu': {'time': None, 'shape': None, 'count': 0},
            'lidar_2d': {'time': None, 'shape': None, 'count': 0},
            'lidar_3d': {'time': None, 'shape': None, 'count': 0},
            'control': {'time': None, 'shape': None, 'count': 0, 'angle': 0.0},
        }

        # Subscribe to sensors
        self.create_subscription(Image, '/camera/image_raw', self._camera_callback, SENSOR_QOS)
        self.create_subscription(Image, '/camera/depth/image_raw', self._depth_callback, SENSOR_QOS)
        self.create_subscription(Imu, '/imu/data', self._imu_callback, SENSOR_QOS)
        self.create_subscription(LaserScan, '/scan', self._lidar_2d_callback, SENSOR_QOS)
        self.create_subscription(PointCloud2, '/points', self._lidar_3d_callback, SENSOR_QOS)

        # Publisher for joint commands
        self._joint_pub = self.create_publisher(JointState, '/joint_states', 10)

        # Control loop at 20 Hz
        self._time = 0.0
        self._dt = 1.0 / 20.0
        self.create_timer(self._dt, self._control_loop)

        self.get_logger().info('🤖 Simple robot controller started!')
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.WARN)  # Reduce log spam

    def _camera_callback(self, msg: Image):
        """Process camera images"""
        with self._lock:
            self._sensor_data['camera']['time'] = datetime.now()
            self._sensor_data['camera']['shape'] = f"{msg.width}×{msg.height} {msg.encoding}"
            self._sensor_data['camera']['count'] += 1

    def _depth_callback(self, msg: Image):
        """Process depth images"""
        with self._lock:
            self._sensor_data['depth']['time'] = datetime.now()
            self._sensor_data['depth']['shape'] = f"{msg.width}×{msg.height} {msg.encoding}"
            self._sensor_data['depth']['count'] += 1

    def _imu_callback(self, msg: Imu):
        """Process IMU data"""
        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z
        with self._lock:
            self._sensor_data['imu']['time'] = datetime.now()
            self._sensor_data['imu']['shape'] = f"accel=({ax:.2f}, {ay:.2f}, {az:.2f}) m/s²"
            self._sensor_data['imu']['count'] += 1

    def _lidar_2d_callback(self, msg: LaserScan):
        """Process 2D LiDAR"""
        valid = [r for r in msg.ranges if msg.range_min < r < msg.range_max]
        with self._lock:
            self._sensor_data['lidar_2d']['time'] = datetime.now()
            self._sensor_data['lidar_2d']['shape'] = f"{len(valid)} rays, range {min(valid):.2f}-{max(valid):.2f}m" if valid else "no data"
            self._sensor_data['lidar_2d']['count'] += 1

    def _lidar_3d_callback(self, msg: PointCloud2):
        """Process 3D LiDAR"""
        num_points = msg.width * msg.height
        with self._lock:
            self._sensor_data['lidar_3d']['time'] = datetime.now()
            self._sensor_data['lidar_3d']['shape'] = f"{num_points} points, frame={msg.header.frame_id}"
            self._sensor_data['lidar_3d']['count'] += 1

    def _control_loop(self):
        """Control loop: make the robot wave its right arm"""
        self._time += self._dt

        # Create joint state message
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()

        # Simple wave motion: move right shoulder and elbow
        # Using a sine wave for smooth motion
        wave_angle = 0.5 * math.sin(2.0 * math.pi * 0.3 * self._time)  # 0.3 Hz wave

        msg.name = [
            'right_shoulder_pitch_joint',
            'right_shoulder_roll_joint',
            'right_elbow_joint',
        ]
        msg.position = [
            wave_angle,      # Shoulder pitch: wave up and down
            -0.5,            # Shoulder roll: arm out to the side
            -wave_angle,     # Elbow: complement the shoulder motion
        ]

        self._joint_pub.publish(msg)

        # Update control data
        with self._lock:
            self._sensor_data['control']['time'] = datetime.now()
            self._sensor_data['control']['angle'] = wave_angle
            self._sensor_data['control']['shape'] = f"wave={wave_angle:.3f} rad, joints=3"
            self._sensor_data['control']['count'] += 1

    def get_display_table(self) -> Table:
        """Generate the rich table for display"""
        table = Table(title="🤖 Robot Sensor Monitor & Control", show_header=True, header_style="bold magenta")
        table.add_column("Topic", style="cyan", width=30)
        table.add_column("Last Update", style="green", width=15)
        table.add_column("Message Count", style="yellow", width=15)
        table.add_column("Shape / Data", style="white", width=60)

        with self._lock:
            # Camera
            self._add_row(table, "📷 /camera/image_raw", self._sensor_data['camera'])

            # Depth camera
            self._add_row(table, "🔲 /camera/depth/image_raw", self._sensor_data['depth'])

            # IMU
            self._add_row(table, "📡 /imu/data", self._sensor_data['imu'])

            # 2D LiDAR
            self._add_row(table, "📊 /scan (2D LiDAR)", self._sensor_data['lidar_2d'])

            # 3D LiDAR
            self._add_row(table, "🗺️  /points (3D LiDAR)", self._sensor_data['lidar_3d'])

            # Control output
            self._add_row(table, "👋 /joint_states (control)", self._sensor_data['control'], style="bold blue")

        return table

    def _add_row(self, table: Table, topic: str, data: dict, style: Optional[str] = None):
        """Add a row to the table"""
        if data['time'] is None:
            time_str = "—"
            count_str = "—"
            shape_str = "waiting..."
        else:
            time_str = data['time'].strftime("%H:%M:%S.%f")[:-4]
            count_str = f"{data['count']:,}"
            shape_str = data['shape'] or "—"

        if style:
            table.add_row(topic, time_str, count_str, shape_str, style=style)
        else:
            table.add_row(topic, time_str, count_str, shape_str)


def main(args=None):
    rclpy.init(args=args)
    controller = SimpleRobotController()

    console = Console()

    # Create a separate thread for ROS spinning
    def spin_thread():
        try:
            rclpy.spin(controller)
        except Exception:
            pass

    spin = threading.Thread(target=spin_thread, daemon=True)
    spin.start()

    # Live display with rich
    try:
        with Live(controller.get_display_table(), refresh_per_second=10, console=console) as live:
            while rclpy.ok():
                live.update(controller.get_display_table())
                import time
                time.sleep(0.1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
