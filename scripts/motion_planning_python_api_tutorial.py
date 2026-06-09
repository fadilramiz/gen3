#!/usr/bin/env python3
"""
A script to outline the fundamentals of the moveit_py motion planning API.
"""

import time

# generic ros libraries
import rclpy
from rclpy.logging import get_logger

# moveit python library
from moveit.core.robot_state import RobotState
from moveit.planning import (
    MoveItPy,
    MultiPipelinePlanRequestParameters,
)


def plan_and_execute(
    robot,
    planning_component,
    logger,
    single_plan_parameters=None,
    multi_plan_parameters=None,
    sleep_time=0.0,
    controllers=["arm_gripper_controller"]
):
    """Helper function to plan and execute a motion."""
    # plan to goal
    logger.info("Planning trajectory")
    if multi_plan_parameters is not None:
        plan_result = planning_component.plan(
            multi_plan_parameters=multi_plan_parameters
        )
    elif single_plan_parameters is not None:
        plan_result = planning_component.plan(
            single_plan_parameters=single_plan_parameters
        )
    else:
        plan_result = planning_component.plan()

    # execute the plan
    if plan_result:
        logger.info("Executing plan")
        robot_trajectory = plan_result.trajectory
        robot.execute(robot_trajectory, controllers=controllers)
    else:
        logger.error("Planning failed")

    time.sleep(sleep_time)



def main():

    ###################################################################
    # MoveItPy Setup
    ###################################################################
    rclpy.init()
    logger = get_logger("moveit_py.pose_goal")

    # instantiate MoveItPy instance and get planning component
    gen = MoveItPy(node_name="moveit_py")
    arm = gen.get_planning_component("arm_gripper")
    gripper = gen.get_planning_component("gripper_plan")
    logger.info("MoveItPy instance created")


    

    ###########################################################################
    # Plan 2 - set goal state with RobotState object
    ###########################################################################

    # instantiate a RobotState instance using the current robot model
    robot_model = gen.get_robot_model()
    robot_state = RobotState(robot_model)

    # randomize the robot state
    robot_state.set_joint_group_positions("arm_gripper", [-0.57, -0.57, 0.0, -0.57, -0.57, -1.57, 0.0])

    # set plan start state to current state
    arm.set_start_state_to_current_state()

    # set goal state to the initialized robot state
    logger.info("Set goal state to the initialized robot state")
    arm.set_goal_state(robot_state=robot_state)

    # plan to goal
    #plan_and_execute(gen, arm, logger, sleep_time=20.0)


    #####################################

    
    

    ###########################################################################
    # Plan 2 - set goal state with RobotState object
    ###########################################################################

    # instantiate a RobotState instance using the current robot model
    robot_model = gen.get_robot_model()
    robot_state = RobotState(robot_model)

    # randomize the robot state
    robot_state.set_to_random_positions()

    # set plan start state to current state
    arm.set_start_state_to_current_state()

    # set goal state to the initialized robot state
    logger.info("Set goal state to the initialized robot state")
    arm.set_goal_state(robot_state=robot_state)

    # plan to goal
    #plan_and_execute(gen, arm, logger, sleep_time=40.0)

    arm.set_start_state_to_current_state()
    

    ###########################################################################
    # Plan 3 - set goal state with PoseStamped message
    ###########################################################################

    # set plan start state to current state
    arm.set_start_state_to_current_state()

    # set pose goal with PoseStamped message
    from geometry_msgs.msg import PoseStamped

    gripper_state = RobotState(robot_model)
    gripper_state.set_joint_group_positions("gripper_plan", [0.8, 0.8])
    gripper.set_start_state_to_current_state()
    gripper.set_goal_state(robot_state=gripper_state)
    plan_and_execute(gen, gripper, logger, sleep_time=10.0, controllers=["gripper_plan_controller"])

    z_position = 0.12 - 0.02 + 0.04 #offset - grip_marge + z_object 

    pose_goal = PoseStamped()
    pose_goal.header.frame_id = "base_link"
    pose_goal.pose.orientation.x = 1.0
    pose_goal.pose.orientation.y = 0.0
    pose_goal.pose.orientation.z = 0.0
    pose_goal.pose.orientation.w = 0.0
    pose_goal.pose.position.x = 0.4
    pose_goal.pose.position.y = 0.0
    pose_goal.pose.position.z = z_position + 0.03 #For a bit up
    arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="end_effector_link")
    # plan to goal
    plan_and_execute(gen, arm, logger, sleep_time=15.0)

    pose_goal.pose.position.z = z_position     # hauteur de saisie (box z=0.02 + moitié 0.02 + offset pince)
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="end_effector_link")
    plan_and_execute(gen, arm, logger, sleep_time=20.0)

    gripper.set_start_state_to_current_state()
    gripper_state.set_joint_group_positions("gripper_plan", [0.02, 0.02])
    gripper.set_goal_state(robot_state=gripper_state)
    plan_and_execute(gen, gripper, logger, sleep_time=25.0, controllers=["gripper_plan_controller"])
    
    pose_goal.pose.position.z = 0.35     # hauteur de saisie (box z=0.02 + moitié 0.02 + offset pince)
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="end_effector_link")
    plan_and_execute(gen, arm, logger, sleep_time=30.0)

if __name__ == "__main__":
    main()
