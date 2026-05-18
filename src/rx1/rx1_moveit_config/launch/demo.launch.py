import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
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
    use_rviz = LaunchConfiguration("use_rviz")
    use_gui = LaunchConfiguration("use_gui")
    rviz_config = os.path.join(
        get_package_share_directory("rx1_moveit_config"), "config", "moveit.rviz"
    )

    robot_description_content = load_text("rx1_description", "urdf/rx1.urdf")

    robot_description = {"robot_description": robot_description_content}
    robot_description_semantic = {
        "robot_description_semantic": load_text("rx1_moveit_config", "config/rx1.srdf")
    }
    robot_description_kinematics = {
        "robot_description_kinematics": load_yaml("rx1_moveit_config", "config/kinematics.yaml")
    }
    ompl_planning = load_yaml("rx1_moveit_config", "config/ompl_planning.yaml")
    joint_limits = {"robot_description_planning": load_yaml("rx1_moveit_config", "config/joint_limits.yaml")}

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
        "allow_trajectory_execution": False,
        "moveit_manage_controllers": False,
    }

    planning_scene_monitor_parameters = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "publish_robot_description": True,
        "publish_robot_description_semantic": True,
    }

    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="true"),
        DeclareLaunchArgument("use_gui", default_value="true"),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
            output="screen",
            condition=IfCondition(use_gui),
        ),
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
            output="screen",
            condition=UnlessCondition(use_gui),
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[robot_description],
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="world_to_base_link",
            arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
            output="screen",
        ),
        Node(
            package="moveit_ros_move_group",
            executable="move_group",
            output="screen",
            parameters=[
                robot_description,
                robot_description_semantic,
                robot_description_kinematics,
                planning_pipeline_config,
                joint_limits,
                trajectory_execution,
                planning_scene_monitor_parameters,
            ],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="log",
            condition=IfCondition(use_rviz),
            arguments=["-d", rviz_config],
            parameters=[
                robot_description,
                robot_description_semantic,
                robot_description_kinematics,
                planning_pipeline_config,
                joint_limits,
            ],
        ),
    ])
