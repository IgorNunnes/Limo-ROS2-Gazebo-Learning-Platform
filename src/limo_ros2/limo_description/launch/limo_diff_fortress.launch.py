import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import xacro


def generate_launch_description():
    pkg_share = get_package_share_directory('limo_description')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    default_model = os.path.join(pkg_share, 'urdf', 'limo_four_diff_fortress.xacro')
    default_world = os.path.join(pkg_share, 'worlds', 'limo_empty.sdf')
    default_rviz = os.path.join(pkg_share, 'rviz', 'urdf.rviz')

    world = LaunchConfiguration('world')
    gz_args = LaunchConfiguration('gz_args')
    rviz_config = LaunchConfiguration('rvizconfig')

    robot_description = xacro.process_file(default_model).toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    spawn_limo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'limo_world',
            '-topic', 'robot_description',
            '-name', 'limo',
            '-allow_renaming', 'true',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.02',
        ],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/limo/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/limo/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/world/limo_world/model/limo/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        parameters=[
            {'qos_overrides./scan.publisher.reliability': 'best_effort'},
            {'qos_overrides./imu.publisher.reliability': 'best_effort'},
        ],
        remappings=[
            ('/model/limo/cmd_vel', '/cmd_vel'),
            ('/model/limo/tf', '/gz_tf'),
            ('/world/limo_world/model/limo/joint_state', '/joint_states'),
        ],
        output='screen',
    )

    odom_from_tf = Node(
        package='limo_description',
        executable='limo_tf_to_odom.py',
        output='screen',
        parameters=[{
            'odom_frame': 'odom',
            'base_frame': 'base_footprint',
            'input_tf_topic': 'gz_tf',
            'use_sim_time': True,
        }],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=default_world),
        DeclareLaunchArgument('gz_args', default_value=['-r ', world]),
        DeclareLaunchArgument('rvizconfig', default_value=default_rviz),
        DeclareLaunchArgument('rviz', default_value='false'),
        gazebo,
        robot_state_publisher,
        TimerAction(period=2.0, actions=[spawn_limo]),
        bridge,
        odom_from_tf,
        rviz,
    ])
