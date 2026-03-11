"""
Multi-robot simulation launcher.

Usage:
    ros2 launch sim_gazebo sim.launch.py                     # default: G1
    ros2 launch sim_gazebo sim.launch.py robot:=g1
    ros2 launch sim_gazebo sim.launch.py robot:=astribot
    ros2 launch sim_gazebo sim.launch.py robot:=g1 gui:=false
    ros2 launch sim_gazebo sim.launch.py robot:=astribot paused:=true
    ros2 launch sim_gazebo sim.launch.py robot:=astribot rosbag:=true
    ros2 launch sim_gazebo sim.launch.py rosbag:=true bag_path:=/workspace/bags/my_run

Adding a new robot:
    1. Create src/<name>_description/ with urdf/<name>_sensors.urdf.xacro
    2. Add an entry to ROBOT_CONFIGS below
    3. colcon build --packages-select sim_gazebo <name>_description
"""

import os
import subprocess
import tempfile
from datetime import datetime

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

# ── Robot registry ────────────────────────────────────────────────────────────
# Add new robots here. Keys become valid values for the robot:= argument.
ROBOT_CONFIGS = {
    'g1': {
        'description_pkg': 'g1_description',
        'xacro_file':      'urdf/g1_sensors.urdf.xacro',
        'entity_name':     'g1_robot',
        'spawn_z':         '0.0',   # world_to_pelvis joint in XACRO offsets to z=0.79
    },
    'astribot': {
        'description_pkg': 'astribot_description',
        'xacro_file':      'urdf/astribot_sensors.urdf.xacro',
        'entity_name':     'astribot_robot',
        'spawn_z':         '0.0',   # world_to_base_link joint in XACRO handles height
    },
}

# Topics recorded when rosbag:=true
RECORD_TOPICS = [
    '/scan',
    '/points',
    '/imu/data',
    '/camera/image_raw',
    '/camera/depth/depth/image_raw',
    '/camera/depth/points',
    '/joint_states',
    '/tf',
    '/tf_static',
    '/clock',
]
# ─────────────────────────────────────────────────────────────────────────────


def launch_setup(context, *args, **kwargs):
    robot          = LaunchConfiguration('robot').perform(context)
    use_sim_time   = LaunchConfiguration('use_sim_time').perform(context)
    use_sim_time_bool = use_sim_time.lower() == 'true'
    gui            = LaunchConfiguration('gui').perform(context)
    paused         = LaunchConfiguration('paused').perform(context)
    rosbag         = LaunchConfiguration('rosbag').perform(context).lower() == 'true'
    bag_path       = LaunchConfiguration('bag_path').perform(context)
    bag_format     = LaunchConfiguration('bag_format').perform(context)

    if robot not in ROBOT_CONFIGS:
        raise ValueError(
            f"Unknown robot '{robot}'. "
            f"Available: {', '.join(ROBOT_CONFIGS.keys())}"
        )

    cfg = ROBOT_CONFIGS[robot]
    desc_pkg   = get_package_share_directory(cfg['description_pkg'])
    xacro_file = os.path.join(desc_pkg, cfg['xacro_file'])
    world_file = os.path.join(
        get_package_share_directory('g1_gazebo'), 'worlds', 'g1_world.world'
    )
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')

    # Write the processed URDF to a temp file so Gazebo reads it once from disk.
    # Using -topic causes Gazebo to re-parse /robot_description whenever a new
    # subscriber (e.g. ros2 bag record) triggers a latched republish, producing
    # a spurious "Could not find the 'robot' element" error in the gzserver log.
    urdf_result = subprocess.run(
        ['xacro', xacro_file], capture_output=True, text=True, check=True
    )
    urdf_tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.urdf', delete=False, prefix=f'{robot}_'
    )
    urdf_tmp.write(urdf_result.stdout)
    urdf_tmp.flush()
    urdf_tmp_path = urdf_tmp.name

    robot_description_content = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file]),
        value_type=str,
    )
    robot_description = {'robot_description': robot_description_content}

    # 1. Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world':        world_file,
            'gui':          gui,
            'paused':       paused,
            'use_sim_time': use_sim_time,
        }.items(),
    )

    # 2. robot_state_publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time_bool}],
    )

    # 3. joint_state_publisher
    jsp_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time_bool}, {'rate': 50}],
    )

    # 4. Spawn robot — use -file (pre-written URDF) instead of -topic so
    # Gazebo only parses the model once and never reacts to later republishes.
    spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_robot',
        output='screen',
        arguments=[
            '-entity',  cfg['entity_name'],
            '-file',    urdf_tmp_path,
            '-x', '0.0', '-y', '0.0', '-z', cfg['spawn_z'],
            '-R', '0.0', '-P', '0.0', '-Y', '0.0',
            '-timeout', '300',
        ],
    )

    actions = [gazebo, rsp_node, jsp_node, spawn_node]

    # 5. Optional bag recording
    if rosbag:
        if not bag_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            bag_path = f'/workspace/bags/{robot}_{timestamp}'
        os.makedirs('/workspace/bags', exist_ok=True)
        bag_node = ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-s', bag_format, '-o', bag_path] + RECORD_TOPICS,
            output='screen',
        )
        actions.append(bag_node)
        print(f'[sim_gazebo] Recording bag to: {bag_path}')

    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'robot',
            default_value='g1',
            description=f"Robot to simulate. Options: {', '.join(ROBOT_CONFIGS.keys())}",
        ),
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use Gazebo simulation clock'),
        DeclareLaunchArgument('gui',    default_value='true',
                              description='Launch Gazebo GUI (gzclient)'),
        DeclareLaunchArgument('paused', default_value='false',
                              description='Start Gazebo paused'),
        # NOTE: named 'rosbag' (not 'record') to avoid collision with Gazebo's
        # own --record flag which gzserver would pick up and crash with exit 255.
        DeclareLaunchArgument('rosbag', default_value='false',
                              description='Record sensor topics to a rosbag'),
        DeclareLaunchArgument('bag_path', default_value='',
                              description='Output path for the bag (default: /workspace/bags/<robot>_<timestamp>)'),
        DeclareLaunchArgument('bag_format', default_value='mcap',
                              description='Bag storage format: mcap or sqlite3'),
        OpaqueFunction(function=launch_setup),
    ])
