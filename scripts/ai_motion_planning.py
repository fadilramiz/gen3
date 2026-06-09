#!/usr/bin/env python3
"""
A script to outline the fundamentals of the moveit_py motion planning API.
"""

import ollama
import time

# generic ros libraries
import rclpy
from rclpy.logging import get_logger

# moveit python library
from moveit.core.robot_state import RobotState
from moveit.planning import (
    MoveItPy,
)


def move_to(dist, actual):
    return actual + dist


def generic_chat():
    return "please provide more information !"


def move_arm(x_pos, y_pos, z_pos):
    with open("file_1.txt", "w") as file:
        file.write(f"x:{x_pos}, y:{y_pos}, z:{z_pos}\n")


def plan_and_execute(
    robot,
    planning_component,
    logger,
    single_plan_parameters=None,
    multi_plan_parameters=None,
    sleep_time=0.0,
    controllers=["arm_gripper_controller"],
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

    # instantiate a RobotState instance using the current robot model
    robot_model = gen.get_robot_model()

    ###################################################
    # Portion of ollama code
    ###################################################
    tools = [
        {
            "type": "function",
            "function": {
                "name": "move_to",
                "description": "Move anything from one position to another given distance, only if the distance was given by the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "distance": {
                            "type": "integer",
                            "description": "the distance",
                        }
                    },
                    "required": ["distance"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generic_chat",
                "description": "When the user doesn't provide sufficient information",
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "move_arm",
                "description": "Move the arm of the robot to a new position",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x_position": {
                            "type": "string",
                            "description": "the new x position, take as string",
                        },
                        "y_position": {
                            "type": "string",
                            "description": "the new y position, take as string",
                        },
                        "z_position": {
                            "type": "string",
                            "description": "the new z position, take as string",
                        },
                    },
                    "required": ["x_position", "y_position", "z_position"],
                },
            },
        },
    ]

    print("request....")
    # request = input("Your request...")
    request = "Call the function move_arm with arguments: x_position=0.20 y_position=0.0 z_position=0.25"

    actuel = 1.0

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a function-calling assistant. "
                    "You MUST ALWAYS respond by calling exactly one tool from the provided list. "
                    "NEVER respond with plain text. "
                    "NEVER add explanations. "
                    "Only output a tool call with the correct arguments in form of string extracted from the user message."
                ),
            },
            {"role": "user", "content": request},
        ],
        tools=tools,
    )
    print(response)

    x_pos = 0.0
    y_pos = 0.0
    z_pos = 0.0

    if (
        "message" in response
        and len(response["message"]["content"]) == 0
        and "tool_calls" in response["message"]
        and "function" in response["message"]["tool_calls"][0]
        and "name" in response["message"]["tool_calls"][0]["function"]
        and "arguments" in response["message"]["tool_calls"][0]["function"]
    ):
        tool_name = response["message"]["tool_calls"][0]["function"]["name"]
        argument = response["message"]["tool_calls"][0]["function"]["arguments"]

        print("\n")
        print(f"The name is {tool_name} and the argument is {argument}")

        if tool_name == "move_to":
            actuel = move_to(int(argument["distance"]), int(actuel))
            print(actuel)
        elif tool_name == "move_arm":
            x_pos = float(argument["x_position"])
            y_pos = float(argument["y_position"])
            z_pos = float(argument["z_position"])
            move_arm(x_pos, y_pos, z_pos)
    else:
        print(generic_chat())

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
    # plan_and_execute(gen, gripper, logger, sleep_time=10.0, controllers=["gripper_plan_controller"])

    pose_goal = PoseStamped()
    pose_goal.header.frame_id = "base_link"
    pose_goal.pose.orientation.x = 1.0
    pose_goal.pose.orientation.y = 0.0
    pose_goal.pose.orientation.z = 0.0
    pose_goal.pose.orientation.w = 0.0
    pose_goal.pose.position.x = x_pos + 0.4
    pose_goal.pose.position.y = y_pos + 0.0
    pose_goal.pose.position.z = z_pos + 0.17
    arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="end_effector_link")
    # plan to goal
    plan_and_execute(gen, arm, logger, sleep_time=15.0)

    gripper.set_start_state_to_current_state()
    gripper_state.set_joint_group_positions("gripper_plan", [0.02, 0.02])
    gripper.set_goal_state(robot_state=gripper_state)
    # plan_and_execute(gen, gripper, logger, sleep_time=25.0, controllers=["gripper_plan_controller"])

    pose_goal.pose.position.z = 0.35
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="end_effector_link")
    # plan_and_execute(gen, arm, logger, sleep_time=30.0)


if __name__ == "__main__":
    main()
