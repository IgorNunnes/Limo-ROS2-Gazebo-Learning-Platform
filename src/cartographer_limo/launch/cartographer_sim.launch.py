from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_share = get_package_share_directory('cartographer_limo')

    config_dir = os.path.join(pkg_share, "config")

    return LaunchDescription([

        # --- CARTOGRAPHER NODE ---
        Node(
            package="cartographer_ros",
            executable="cartographer_node",
            name="cartographer",
            output="screen",

            # !!! NECESARIO EN GAZEBO !!!
            parameters=[{'use_sim_time': True}],

            arguments=[
                "-configuration_directory", config_dir,
                "-configuration_basename", "limo.lua"
            ],

            remappings=[
                ("/scan", "/scan"),         # LIDAR en tu lista de tópicos
                ("/odom", "/odom")
            ],
        ),

        # --- OCCUPANCY GRID ---
        Node(
            package="cartographer_ros",
            executable="cartographer_occupancy_grid_node",
            name="occupancy_grid",
            output="screen",

            parameters=[
                {'use_sim_time': True},     # MUY IMPORTANTE
                {'resolution': 0.05}
            ],
        )
    ])
