import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
def load_yaml(package_name, relative_path):
    package_path = get_package_share_directory(package_name)
    absolute_path = os.path.join(package_path, relative_path)
    with open(absolute_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_text(package_name, relative_path):
    package_path = get_package_share_directory(package_name)
    absolute_path = os.path.join(package_path, relative_path)
    with open(absolute_path, "r", encoding="utf-8") as file:
        return file.read()


def generate_launch_description():
    moveit_use_rviz = LaunchConfiguration("moveit_use_rviz")
    world = LaunchConfiguration("world")
    robot_name = LaunchConfiguration("robot_name")
    robot_x = LaunchConfiguration("robot_x")
    robot_y = LaunchConfiguration("robot_y")
    robot_z = LaunchConfiguration("robot_z")

    rx1_gazebo_share = get_package_share_directory("rx1_gazebo")
    rx1_description_share = get_package_share_directory("rx1_description")

    robot_description = {
        "robot_description": load_text("rx1_description", "urdf/rx1.urdf"),
        "use_sim_time": True,
    }
    robot_description_semantic = {
        "robot_description_semantic": load_text("rx1_moveit_config", "config/rx1.srdf")
    }
    robot_description_kinematics = {
        "robot_description_kinematics": load_yaml(
            "rx1_moveit_config", "config/kinematics.yaml"
        )
    }
    ompl_planning = load_yaml("rx1_moveit_config", "config/ompl_planning.yaml")
    joint_limits = {
        "robot_description_planning": load_yaml(
            "rx1_moveit_config", "config/joint_limits.yaml"
        )
    }
    moveit_controllers = load_yaml(
        "rx1_moveit_config", "config/moveit_controllers_gazebo.yaml"
    )
    planning_pipeline_config = {
        "planning_pipelines": ["ompl"],
        "default_planning_pipeline": "ompl",
        "ompl": {
            "planning_plugins": ["ompl_interface/OMPLPlanner"],
            "request_adapters": [
                "default_planning_request_adapters/ResolveConstraintFrames",
                "default_planning_request_adapters/ValidateWorkspaceBounds",
                "default_planning_request_adapters/CheckStartStateBounds",
                "default_planning_request_adapters/CheckStartStateCollision",
            ],
            "response_adapters": [
                "default_planning_response_adapters/AddTimeOptimalParameterization",
                "default_planning_response_adapters/ValidateSolution",
                "default_planning_response_adapters/DisplayMotionPath",
            ],
            "start_state_max_bounds_error": 0.1,
        },
    }
    planning_pipeline_config["ompl"].update(ompl_planning)

    trajectory_execution = {
        "allow_trajectory_execution": True,
        "moveit_manage_controllers": False,
        "use_sim_time": True,
    }

    planning_scene_monitor_parameters = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "publish_robot_description": True,
        "publish_robot_description_semantic": True,
        "use_sim_time": True,
    }

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rx1_gazebo_share, "launch", "rx1_gazebo.launch.py")
        ),
        launch_arguments={
            "world": world,
            "robot_name": robot_name,
            "robot_x": robot_x,
            "robot_y": robot_y,
            "robot_z": robot_z,
            "use_rviz": "false",
        }.items(),
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            planning_pipeline_config,
            joint_limits,
            moveit_controllers,
            trajectory_execution,
            planning_scene_monitor_parameters,
        ],
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        condition=IfCondition(moveit_use_rviz),
        arguments=[
            "-d",
            os.path.join(
                get_package_share_directory("rx1_moveit_config"),
                "config",
                "moveit.rviz",
            ),
        ],
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            planning_pipeline_config,
            joint_limits,
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("moveit_use_rviz", default_value="true"),
            DeclareLaunchArgument(
                "world",
                default_value=os.path.join(
                    rx1_gazebo_share, "worlds", "rx1_table_world.sdf"
                ),
            ),
            DeclareLaunchArgument("robot_name", default_value="rx1"),
            DeclareLaunchArgument("robot_x", default_value="0.0"),
            DeclareLaunchArgument("robot_y", default_value="0.0"),
            DeclareLaunchArgument("robot_z", default_value="0.0"),
            sim_launch,
            move_group,
            rviz,
        ]
    )
