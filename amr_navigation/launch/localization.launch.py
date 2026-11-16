from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = LaunchConfiguration('params_file')
    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    use_composition = LaunchConfiguration('use_composition')

    nav2_localization_launch = PathJoinSubstitution(
        [
            FindPackageShare('nav2_bringup'),
            'launch',
            'localization_launch.py',
        ]
    )
    default_params_file = PathJoinSubstitution(
        [
            FindPackageShare('amr_navigation'),
            'config',
            'nav2_params.yaml',
        ]
    )
    default_map_file = PathJoinSubstitution(
        [
            FindPackageShare('amr_navigation'),
            'maps',
            'warehouse_map.yaml',
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'params_file',
                default_value=default_params_file,
                description='Path to the Nav2 parameters YAML file.',
            ),
            DeclareLaunchArgument(
                'map',
                default_value=default_map_file,
                description='Path to the static map YAML file used by AMCL.',
            ),
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='true',
                description='Use the simulation clock.',
            ),
            DeclareLaunchArgument(
                'autostart',
                default_value='true',
                description='Automatically activate the localization nodes.',
            ),
            DeclareLaunchArgument(
                'use_composition',
                default_value='False',
                description='Run localization nodes as separate processes.',
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(nav2_localization_launch),
                launch_arguments={
                    'map': map_file,
                    'params_file': params_file,
                    'use_sim_time': use_sim_time,
                    'autostart': autostart,
                    'use_composition': use_composition,
                }.items(),
            ),
        ]
    )
