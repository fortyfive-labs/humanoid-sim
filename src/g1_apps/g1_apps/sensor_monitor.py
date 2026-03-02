"""
sensor_monitor.py — Unitree G1 sensor subscriber template.

Subscribes to all four simulated sensor topics and logs summary data.
Replace the callback bodies with your own perception / processing logic.

Run:
    ros2 run g1_apps sensor_monitor
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from sensor_msgs.msg import LaserScan, PointCloud2, Image, Imu


# Best-effort QoS matches the default Gazebo sensor publisher profile
SENSOR_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=5,
)


class SensorMonitor(Node):

    def __init__(self):
        super().__init__('sensor_monitor')

        self.create_subscription(LaserScan, '/scan', self._scan_cb, SENSOR_QOS)
        self.create_subscription(PointCloud2, '/points', self._points_cb, SENSOR_QOS)
        self.create_subscription(Image, '/camera/image_raw', self._image_cb, SENSOR_QOS)
        self.create_subscription(Imu, '/imu/data', self._imu_cb, SENSOR_QOS)

        self.get_logger().info('SensorMonitor started — listening on /scan, /points, '
                               '/camera/image_raw, /imu/data')

    # ------------------------------------------------------------------
    # Callbacks — replace these with your own logic
    # ------------------------------------------------------------------

    def _scan_cb(self, msg: LaserScan):
        """2D LiDAR: full 360-degree LaserScan at ~15 Hz."""
        valid = [r for r in msg.ranges if msg.range_min < r < msg.range_max]
        if valid:
            self.get_logger().info(
                f'[2D LiDAR] {len(valid)} valid rays | '
                f'min={min(valid):.2f} m  max={max(valid):.2f} m',
                throttle_duration_sec=1.0,
            )

    def _points_cb(self, msg: PointCloud2):
        """3D LiDAR: PointCloud2 at ~10 Hz."""
        self.get_logger().info(
            f'[3D LiDAR] frame={msg.header.frame_id}  '
            f'points={msg.width * msg.height}',
            throttle_duration_sec=1.0,
        )

    def _image_cb(self, msg: Image):
        """RGB Camera: 640×480 image at ~30 Hz."""
        self.get_logger().info(
            f'[Camera]   {msg.width}x{msg.height} {msg.encoding}',
            throttle_duration_sec=1.0,
        )

    def _imu_cb(self, msg: Imu):
        """IMU: linear acceleration + angular velocity at ~200 Hz."""
        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z
        self.get_logger().info(
            f'[IMU]      accel=({ax:.3f}, {ay:.3f}, {az:.3f}) m/s²',
            throttle_duration_sec=1.0,
        )


def main(args=None):
    rclpy.init(args=args)
    node = SensorMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
