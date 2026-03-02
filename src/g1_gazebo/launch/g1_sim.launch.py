"""
Main simulation launch file for the Unitree G1.
Starts Gazebo Classic, spawns the robot, and launches all required ROS2 nodes.

Usage:
    ros2 launch g1_gazebo g1_sim.launch.py
    ros2 launch g1_gazebo g1_sim.launch.py gui:=false   # headless
    ros2 launch g1_gazebo g1_sim.launch.py paused:=true  # start paused
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # Package share paths
    g1_description_pkg = get_package_share_directory('g1_description')
    g1_gazebo_pkg = get_package_share_directory('g1_gazebo')
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    paused = LaunchConfiguration('paused', default='false')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use Gazebo simulation clock'
    )
    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Set to false to run Gazebo headless (gzserver only)'
    )
    declare_paused = DeclareLaunchArgument(
        'paused',
        default_value='false',
        description='Start Gazebo in paused state'
    )

    # File paths
    world_file = os.path.join(g1_gazebo_pkg, 'worlds', 'g1_world.world')
    xacro_file = os.path.join(g1_description_pkg, 'urdf', 'g1_sensors.urdf.xacro')

    # Process XACRO → URDF string at launch time
    robot_description_content = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file]),
        value_type=str,
    )
    robot_description = {'robot_description': robot_description_content}

    # 1. Launch Gazebo (gzserver + optional gzclient)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_file,
            'gui': gui,
            'paused': paused,
            'use_sim_time': use_sim_time,
        }.items(),
    )

    # 2. robot_state_publisher — broadcasts TF from URDF joint states
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': use_sim_time},
        ],
    )

    # 3. joint_state_publisher — publishes all 23 DOF at zero position
    #    (robot is fixed to world so no controllers are needed)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'rate': 50},
        ],
    )

    # 4. Spawn the robot into Gazebo
    #    z=0.0 because the world_to_pelvis joint in the XACRO already
    #    offsets the pelvis to z=0.79 above the ground.
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_g1',
        output='screen',
        arguments=[
            '-entity', 'g1_robot',
            '-topic', '/robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.0',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0',
            '-timeout', '300',
        ],
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_gui,
        declare_paused,
        gazebo,
        robot_state_publisher_node,
        joint_state_publisher_node,
        spawn_entity_node,
    ])
