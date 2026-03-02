"""
RViz2 visualization launch for the Unitree G1.
Does NOT start Gazebo — use this for quick URDF inspection and TF debugging.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    g1_description_pkg = get_package_share_directory('g1_description')

    xacro_file = os.path.join(
        g1_description_pkg, 'urdf', 'g1_sensors.urdf.xacro'
    )
    rviz_config_file = os.path.join(
        g1_description_pkg, 'rviz', 'g1_display.rviz'
    )

    robot_description_content = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file]),
        value_type=str,
    )
    robot_description = {'robot_description': robot_description_content}

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node,
        rviz_node,
    ])
