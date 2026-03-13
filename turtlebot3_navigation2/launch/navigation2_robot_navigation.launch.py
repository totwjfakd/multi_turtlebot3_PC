# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml

TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']
ROS_DISTRO = os.environ.get('ROS_DISTRO')


def generate_launch_description():
    namespace = LaunchConfiguration('namespace', default='')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    shared_map_topic = LaunchConfiguration('shared_map_topic', default='/map')
    base_frame_id = PythonExpression(
        ['"', namespace, '" + "/base_footprint" if "', namespace, '" != "" else "base_footprint"'])
    odom_frame_id = PythonExpression(
        ['"', namespace, '" + "/odom" if "', namespace, '" != "" else "odom"'])

    param_file_name = TURTLEBOT3_MODEL + '.yaml'
    if TURTLEBOT3_MODEL == 'waffle':
        param_file_name = 'waffle_multi.yaml'
    if ROS_DISTRO == 'humble':
        params_file = LaunchConfiguration(
            'params_file',
            default=os.path.join(
                get_package_share_directory('turtlebot3_navigation2'),
                'param',
                ROS_DISTRO,
                param_file_name))
    else:
        params_file = LaunchConfiguration(
            'params_file',
            default=os.path.join(
                get_package_share_directory('turtlebot3_navigation2'),
                'param',
                param_file_name))

    autostart = LaunchConfiguration('autostart', default='true')
    use_respawn = LaunchConfiguration('use_respawn', default='False')
    log_level = LaunchConfiguration('log_level', default='info')
    nav_stack_launch_file = os.path.join(
        get_package_share_directory('turtlebot3_navigation2'),
        'launch',
        'navigation2_robot_nav_stack.launch.py')

    localization_params = ParameterFile(
        RewrittenYaml(
            source_file=params_file,
            root_key=namespace,
            param_rewrites={
                'use_sim_time': use_sim_time,
                'amcl.ros__parameters.map_topic': shared_map_topic,
                'amcl.ros__parameters.scan_topic': 'scan',
                'amcl.ros__parameters.base_frame_id': base_frame_id,
                'amcl.ros__parameters.odom_frame_id': odom_frame_id,
                'global_costmap.global_costmap.ros__parameters.static_layer.map_topic': shared_map_topic,
                'local_costmap.local_costmap.ros__parameters.static_layer.map_topic': shared_map_topic,
            },
            convert_types=True),
        allow_substs=True)

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Namespace for robot stack'),

        DeclareLaunchArgument(
            'shared_map_topic',
            default_value='/map',
            description='Map topic published by shared map_server'),

        DeclareLaunchArgument(
            'params_file',
            default_value=params_file,
            description='Full path to shared Nav2 parameter file'),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically startup AMCL stack'),

        DeclareLaunchArgument(
            'use_respawn',
            default_value='False',
            description='Respawn AMCL if it crashes when composition is disabled'),

        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Node log level'),

        GroupAction(
            actions=[
                PushRosNamespace(namespace),
                # SetRemap(src='tf', dst='/tf'),
                # SetRemap(src='tf_static', dst='/tf_static'),
                # SetRemap(src='map', dst=shared_map_topic),
                # SetRemap(src='tb3_map', dst=shared_map_topic),
                # SetRemap(src='/tb3_map', dst=shared_map_topic),
                # SetRemap(src='/scan', dst='scan'),

                Node(
                    package='nav2_amcl',
                    executable='amcl',
                    name='amcl',
                    output='screen',
                    respawn=use_respawn,
                    respawn_delay=2.0,
                    parameters=[localization_params],
                    arguments=['--ros-args', '--log-level', log_level],
                    remappings=[
                        ('map', shared_map_topic)
                    ]),

                Node(
                    package='nav2_lifecycle_manager',
                    executable='lifecycle_manager',
                    name='lifecycle_manager_localization',
                    output='screen',
                    arguments=['--ros-args', '--log-level', log_level],
                    parameters=[
                        {'use_sim_time': use_sim_time},
                        {'autostart': autostart},
                        {'node_names': ['amcl']}]),
            ]),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav_stack_launch_file),
            launch_arguments={
                'namespace': namespace,
                'shared_map_topic': shared_map_topic,
                'params_file': params_file,
                'use_sim_time': use_sim_time,
                'autostart': autostart,
                'use_respawn': use_respawn,
                'log_level': log_level,
            }.items(),
        ),
    ])
