"""
joint_commander.py — Unitree G1 joint control template.

Publishes JointState messages to drive the simulated robot joints.
Includes a simple sine-wave demo on the left hip joint as proof-of-concept.
Replace the control_loop body with your own motion / control logic.

Note: In the fixed-pose simulation the joint_state_publisher also publishes
/joint_states. Run EITHER joint_state_publisher OR joint_commander, not both.
To use this node, stop joint_state_publisher first or launch with it disabled.

Run:
    ros2 run g1_apps joint_commander
"""

import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState


# Unitree G1 23-DOF joint names (from g1_23dof_base.urdf)
G1_JOINT_NAMES = [
    # Left leg
    'left_hip_pitch_joint',
    'left_hip_roll_joint',
    'left_hip_yaw_joint',
    'left_knee_joint',
    'left_ankle_pitch_joint',
    'left_ankle_roll_joint',
    # Right leg
    'right_hip_pitch_joint',
    'right_hip_roll_joint',
    'right_hip_yaw_joint',
    'right_knee_joint',
    'right_ankle_pitch_joint',
    'right_ankle_roll_joint',
    # Waist
    'waist_yaw_joint',
    'waist_roll_joint',
    'waist_pitch_joint',
    # Left arm
    'left_shoulder_pitch_joint',
    'left_shoulder_roll_joint',
    'left_shoulder_yaw_joint',
    'left_elbow_joint',
    # Right arm
    'right_shoulder_pitch_joint',
    'right_shoulder_roll_joint',
    'right_shoulder_yaw_joint',
    'right_elbow_joint',
]


class JointCommander(Node):

    def __init__(self):
        super().__init__('joint_commander')

        self._pub = self.create_publisher(JointState, '/joint_states', 10)

        # 50 Hz control loop
        self._t = 0.0
        self._dt = 1.0 / 50.0
        self.create_timer(self._dt, self._control_loop)

        self.get_logger().info(
            'JointCommander started — publishing to /joint_states at 50 Hz'
        )

    def _control_loop(self):
        """
        Called at 50 Hz. Compute desired joint positions and publish.

        Demo: sine wave on left_hip_pitch_joint (index 0), all others at 0.
        Replace this method with your own motion planning / control logic.
        """
        self._t += self._dt

        # ------------------------------------------------------------------
        # YOUR CONTROL LOGIC HERE
        # Compute a position (rad) for each joint in G1_JOINT_NAMES order.
        # ------------------------------------------------------------------
        positions = [0.0] * len(G1_JOINT_NAMES)

        # Demo: ±0.3 rad sine wave on left_hip_pitch at 0.5 Hz
        positions[0] = 0.3 * math.sin(2.0 * math.pi * 0.5 * self._t)
        # ------------------------------------------------------------------

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = G1_JOINT_NAMES
        msg.position = positions

        self._pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = JointCommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
