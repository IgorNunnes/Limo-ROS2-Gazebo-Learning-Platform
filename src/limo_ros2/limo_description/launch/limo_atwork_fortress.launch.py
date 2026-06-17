import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_share = get_package_share_directory('limo_description')
    default_world = os.path.join(pkg_share, 'worlds', 'limo_atwork_educational.sdf')
    world = LaunchConfiguration('world')
    gz_args = LaunchConfiguration('gz_args')

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=default_world),
        DeclareLaunchArgument('gz_args', default_value=['-r ', world]),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_share, 'launch', 'limo_diff_fortress.launch.py')
            ),
            launch_arguments={
                'world': world,
                'gz_args': gz_args,
            }.items(),
        ),
    ])
