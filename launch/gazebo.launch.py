#!/usr/bin/env python3

import os
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
	ExecuteProcess,
	IncludeLaunchDescription,
	TimerAction,
	)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
	gazebo = IncludeLaunchDescription(
		PythonLaunchDescriptionSource([os.path.join(
			get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
		launch_arguments=[('gz_args', '-r -v4 empty.sdf --physics-engine gz-physics-bullet-featherstone-plugin')],
	)

	pkg_share = get_package_share_directory("gen3")

	# ---------------------------------------------------------------
	# 1. URDF via xacro
	# ---------------------------------------------------------------
	urdf_file = os.path.join(pkg_share, "config", "GEN3-7DOF-VISION_ARM_URDF_V12.urdf.xacro")
	initial_positions_file = os.path.join(pkg_share, "config", "initial_positions.yaml")

	robot_description_content = xacro.process_file(
		urdf_file,
		mappings={"initial_positions_file": initial_positions_file}
	).toxml()

	robot_state = Node(
		package = 'robot_state_publisher',
		executable = 'robot_state_publisher',
		parameters = [{"robot_description": robot_description_content},
		{"use_sim_time": True }],
	)

	spawn_robot = Node(
		package = 'ros_gz_sim',
		executable = 'create',
		arguments = [
			'-name', 'gen3',
			'-string', robot_description_content,
		],
	)

	gen3_arm = ExecuteProcess(
		cmd = ['ros2', 'control', 'load_controller', '--set-state', 'active', 'arm_gripper_controller']
	)

	gripper_controller = ExecuteProcess(
		cmd = ['ros2', 'control', 'load_controller', '--set-state', 'active', 'gripper_plan_controller']
	)

	joint_state = ExecuteProcess(
		cmd = ['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster']
	)

	param1 = ExecuteProcess(
		cmd = ['ros2', 'param', 'set', '/controller_manager', 'use_sim_time', 'true']
	)

	param2 = ExecuteProcess(
		cmd = ['ros2', 'param', 'set', '/gripper_plan_controller', 'use_sim_time', 'true']
	)

	param3 = ExecuteProcess(
		cmd = ['ros2', 'param', 'set', '/arm_gripper_controller', 'use_sim_time', 'true']
	)


	exec_gazebo = TimerAction(
		period = 0.0,
		actions = [gazebo],
	)

	exec_publ = TimerAction(
		period = 6.0,
		actions = [robot_state],
	)

	exec_spawn = TimerAction(
		period = 9.0,
		actions = [spawn_robot],
	)

	exec_gen3_arm = TimerAction(
		period = 15.0,
		actions = [gen3_arm],
	)

	exec_gripper_contr = TimerAction(
		period = 18.0,
		actions = [gripper_controller],
	)

	exec_state = TimerAction(
		period = 21.0,
		actions = [joint_state],
	)

	exec_param1 = TimerAction(
		period = 24.0,
		actions = [param1],
	)

	exec_param2 = TimerAction(
		period = 27.0,
		actions = [param2],
	)

	exec_param3 = TimerAction(
		period = 30.0,
		actions = [param3],
	)

	return LaunchDescription([
		exec_gazebo,
		exec_publ,
		exec_spawn,
		exec_gen3_arm,
		exec_gripper_contr,
		exec_state,
		exec_param1,
		exec_param2,
		exec_param3,
		])