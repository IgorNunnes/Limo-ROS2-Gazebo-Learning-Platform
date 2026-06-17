import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import xacro


def generate_launch_description():
    # Usando limo_description para o modelo de 4 rodas com diferencial (diff drive)
    # pois ele já possui a configuração correta para o Ignition Fortress
    package_description = 'limo_description'
    pkg_path = get_package_share_directory(package_description)
    xacro_file = os.path.join(pkg_path, 'urdf', 'limo_four_diff_fortress.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    use_sim_time = LaunchConfiguration('use_sim_time')
    gz_args = LaunchConfiguration('gz_args')

    # Integrando o cenário da arena Work (limo_atwork_educational.sdf)
    default_world = os.path.join(pkg_path, 'worlds', 'limo_atwork_educational.sdf')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py',
            )
        ),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
    )

    # Spawning do robô com pequeno delay para garantir que o Gazebo esteja pronto
    # Spawning em uma posição central limpa da arena
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'limo_world',
            '-topic', 'robot_description',
            '-name', 'limo',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
        ],
        output='screen',
    )

    # Bridge para comunicação entre ROS 2 e Ignition Fortress
    # Necessário para enviar comandos de velocidade e receber odometria/sensores
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
            ('/model/limo/tf', '/tf'),
            ('/world/limo_world/model/limo/joint_state', '/joint_states'),
        ],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time.',
        ),
        DeclareLaunchArgument(
            'gz_args',
            default_value=['-r ', default_world],
            description='Arguments passed to Gazebo Sim / Ignition Fortress.',
        ),
        gazebo,
        robot_state_publisher,
        TimerAction(period=2.0, actions=[spawn_robot]),
        bridge,
    ])
