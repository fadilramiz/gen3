#!/usr/bin/env python3

import os
from launch import LaunchDescription 
from launch_ros.actions import Node
from launch.actions import (
	TimerAction,
	IncludeLaunchDescription,
	DeclareLaunchArgument,
	)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder 
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
	# ---------------------------------------------------------------
	# 2. MoveIt config
	# ---------------------------------------------------------------
	moveit_config = (
		MoveItConfigsBuilder(robot_name="GEN3-7DOF-VISION_ARM_URDF_V12", package_name="gen3")
		.robot_description(file_path="config/GEN3-7DOF-VISION_ARM_URDF_V12.urdf.xacro")
		.robot_description_semantic(file_path="config/GEN3-7DOF-VISION_ARM_URDF_V12.srdf")
		.trajectory_execution(file_path="config/moveit_controllers.yaml")
		.joint_limits(file_path="config/joint_limits.yaml")
		.robot_description_kinematics(file_path="config/kinematics.yaml")
		.planning_pipelines(pipelines=["ompl"])
		.moveit_cpp(
			file_path=get_package_share_directory("gen3")
			+ "/config/motion_planning_python_api_tutorial.yaml")
		.to_moveit_configs()
	)

	# Paramètre use_sim_time indispensable pour synchroniser avec Gazebo
	moveit_config_dict = moveit_config.to_dict()
	moveit_config_dict["use_sim_time"] = True

	gazebo = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([
			os.path.join(get_package_share_directory('gen3'), 'launch', 'gazebo.launch.py')]),
	)

	gz_bridge = Node(
		package='ros_gz_bridge',
		executable='parameter_bridge',
		arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
		output='screen',
	)

	gz_camera_bridge = Node(
		package='ros_gz_bridge',
		executable='parameter_bridge',
		arguments=[
			'/camera/color/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
			'/camera/color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
			'/camera/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
			'/camera/depth/image_raw/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
		],
		output='screen',
	)

	move_group = Node(
		package = 'moveit_ros_move_group',
		executable = 'move_group',
		parameters = [moveit_config_dict],
	)

	rviz_config_file = os.path.join(get_package_share_directory('gen3'), 'config', 'moveit.rviz')

	rviz_node = Node(
		package = 'rviz2',
		executable = 'rviz2',
		arguments = ['-d', rviz_config_file],
		parameters = [
			moveit_config.robot_description,
			moveit_config.robot_description_semantic,
			moveit_config.robot_description_kinematics,
			{'use_sim_time': True},
		]
	)

	rqt_node = Node(
		package = 'rqt_image_view',
		executable = 'rqt_image_view',
	)

	exec_gazebo = TimerAction(
		period = 0.0,
		actions = [gazebo],
	)

	exec_gz_bridge = TimerAction(
		period = 3.0,
		actions = [gz_bridge],
	)

	exec_camera_bridge = TimerAction(
		period=15.0,
		actions=[gz_camera_bridge],
	)

	exec_move_group = TimerAction(
		period = 30.0,
		actions = [move_group],
	)

	exec_rviz = TimerAction(
		period = 35.0,
		actions = [rviz_node],
	)

	exec_rqt = TimerAction(
		period = 40.0,
		actions = [rqt_node],
	)

	example_file = DeclareLaunchArgument(
		"example_file",
		default_value="motion_planning_python_api_tutorial.py",
		description="Python API tutorial file name",
	)

	moveit_py_node = Node(
		name="moveit_py",
		package="gen3",
		executable=LaunchConfiguration("example_file"),
		output="both",
		parameters=[moveit_config_dict],
	)

	exec_moveit_py_node = TimerAction(
		period = 40.0,
		actions = [moveit_py_node],
	)


	return LaunchDescription([
		example_file,
		exec_gazebo,
		exec_gz_bridge,
		exec_camera_bridge,
		exec_move_group,
		exec_rviz,
		exec_moveit_py_node,
		#exec_rqt,
		])