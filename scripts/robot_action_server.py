#!/usr/bin/env python3

import rclpy 
import time
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse
from rclpy.action.server import ServerGoalHandle
from my_robot_interfaces.action import ActionCount, MoveRobot

from geometry_msgs.msg import PoseStamped
from moveit.core.robot_state import RobotState
from moveit.planning import (
    MoveItPy,
    # MultiPipelinePlanRequestParameters,
)
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory

class my_action(Node):
	"""docstring for my_action"""
	def __init__(self):
		super().__init__("action_node")
		cfg = (
		    MoveItConfigsBuilder(robot_name="GEN3-7DOF-VISION_ARM_URDF_V12", package_name="gen3")
		    .robot_description(file_path="config/GEN3-7DOF-VISION_ARM_URDF_V12.urdf.xacro")
		    .robot_description_semantic(file_path="config/GEN3-7DOF-VISION_ARM_URDF_V12.srdf")
		    .trajectory_execution(file_path="config/moveit_controllers.yaml")
		    .joint_limits(file_path="config/joint_limits.yaml")
		    .robot_description_kinematics(file_path="config/kinematics.yaml")
		    .planning_pipelines(pipelines=["ompl"])
		    .moveit_cpp(file_path=get_package_share_directory("gen3") + "/config/motion_planning_python_api_tutorial.yaml")
		    .to_moveit_configs()
		    .to_dict()
		)
		cfg["use_sim_time"] = True
		self.gen = MoveItPy(node_name="moveit_py", config_dict=cfg)
		self.arm = self.gen.get_planning_component("arm_gripper")

		self.get_logger().info("MoveItPy instance created")

		self.get_logger().info("Action Node Started")
		self.count_until_server = ActionServer(self, MoveRobot, "move_robot", goal_callback=self.goal_callback, execute_callback=self.execute_callback)

	def goal_callback(self, goal_request: MoveRobot.Goal):
		self.get_logger().info("Received a goal")
		if goal_request.x_position <= 0 :
			self.get_logger().info("Rejecting, Target must be positiive")
			return GoalResponse.REJECT
		self.get_logger().info("Accept the goal")
		return GoalResponse.ACCEPT

	def execute_callback(self, goal_handle: ServerGoalHandle):

		x_pos = goal_handle.request.x_position
		y_pos = goal_handle.request.y_position
		z_pos = goal_handle.request.z_position

		self.arm.set_start_state_to_current_state()

		pose_goal = PoseStamped()
		pose_goal.header.frame_id = "base_link"
		pose_goal.pose.position.x = x_pos
		pose_goal.pose.position.y = y_pos
		pose_goal.pose.position.z = z_pos
		pose_goal.pose.orientation.x = 1.0
		pose_goal.pose.orientation.w = 0.0

		self.arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="end_effector_link")
		time_t0 = time.perf_counter()
		done = self.plan_and_execute(self.gen, self.arm)
		duration = time.perf_counter() - time_t0

		result = MoveRobot.Result()
		self.get_logger().info("Executing goal")

		### Modify this place for customized action 
		if done:
			goal_handle.succeed()
			result.done = int(duration)
		else:
			goal_handle.abort()
			result.done = 0
		return result

	def plan_and_execute(self, robot,
		planning_component,
		sleep_time = 1.0,
		controllers = []):
		self.get_logger().info("Planning Trajectory")
		plan_result = planning_component.plan()

		if plan_result:
			self.get_logger().info("Executing Plan")
			robot.execute(plan_result.trajectory, controllers=controllers)
			time.sleep(sleep_time)
			return True
		else:
			self.get_logger().info("Planning Failed")
			return False


def main():
	rclpy.init()
	node = my_action()
	rclpy.spin(node)
	rclpy.shutdown()

if __name__ == '__main__':
	main()