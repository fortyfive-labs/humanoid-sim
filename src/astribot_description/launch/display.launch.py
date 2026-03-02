"""RViz2 visualization launch for the Astribot S1 (no Gazebo)."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('astribot_description')

    xacro_file = os.path.join(pkg, 'urdf', 'astribot_sensors.urdf.xacro')
    rviz_config = os.path.join(pkg, 'rviz', 'astribot_display.rviz')

    robot_description_content = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file]),
        value_type=str,
    )

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description_content}],
            output='screen',
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        ),
    ])
