from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    paused = LaunchConfiguration("paused")
    gui = LaunchConfiguration("gui")
    verbose = LaunchConfiguration("verbose")
    robot_x = LaunchConfiguration("robot_x")
    robot_y = LaunchConfiguration("robot_y")
    robot_z = LaunchConfiguration("robot_z")

    gazebo_world = PathJoinSubstitution(
        [FindPackageShare("rx1_gazebo"), "worlds", "table_world.world"]
    )
    robot_description_content = Command(
        [
            FindExecutable(name="xacro"),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("rx1_description"), "urdf", "rx1.gazebo.urdf"]
            ),
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument("paused", default_value="false"),
        DeclareLaunchArgument("gui", default_value="true"),
        DeclareLaunchArgument("verbose", default_value="true"),
        DeclareLaunchArgument("robot_x", default_value="0.0"),
        DeclareLaunchArgument("robot_y", default_value="0.0"),
        DeclareLaunchArgument("robot_z", default_value="0.01"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"]
                )
            ),
            launch_arguments={
                "world": gazebo_world,
                "pause": paused,
                "gui": gui,
                "verbose": verbose,
            }.items(),
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description_content}],
        ),
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=[
                "-topic",
                "robot_description",
                "-entity",
                "rx1",
                "-x",
                robot_x,
                "-y",
                robot_y,
                "-z",
                robot_z,
            ],
            output="screen",
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="world_broadcaster",
            arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
            output="screen",
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="map_broadcaster",
            arguments=["0", "0", "0", "0", "0", "0", "world", "map"],
            output="screen",
        ),
        ExecuteProcess(
            cmd=[
                "ros2",
                "run",
                "controller_manager",
                "spawner",
                "joint_state_broadcaster",
                "--controller-manager",
                "/controller_manager",
            ],
            output="screen",
        ),
    ])
