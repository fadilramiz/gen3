#!/usr/bin/env python3

from action_msgs.msg import GoalStatus
import rclpy
import ollama
from rclpy.node import Node
from std_msgs.msg import String
from my_robot_interfaces.srv import OllamaResp
from my_robot_interfaces.action import ActionCount, MoveRobot
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle

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
                        "type": "integer",
                        "description": "the new x position, take as number",
                    },
                    "y_position": {
                        "type": "integer",
                        "description": "the new y position, take as number",
                    },
                    "z_position": {
                        "type": "integer",
                        "description": "the new z position, take as number",
                    },
                },
                "required": ["x_position", "y_position", "z_position"],
            },
        },
    },
]

class newclass(Node):
	"""docstring for newclass"""
	def __init__(self):
		super().__init__("ollama_quetion_publisher")
		
		self.ollama_service = self.create_service(OllamaResp, "ollama_query", self.callback_ollama)
		self.action_client = ActionClient(self, MoveRobot, "move_robot")
		self.get_logger().info("Ollama server started")

	def send_goal(self, result, delay):
		self.action_client.wait_for_server()
		goal = MoveRobot.Goal()
		goal.x_position = float(result["x_position"])
		goal.y_position = float(result["y_position"])
		goal.z_position = float(result["z_position"])
		self.action_client.send_goal_async(goal=goal).add_done_callback(self.goal_response_callback)

	def goal_response_callback(self, future):
		self.goal_handle : ClientGoalHandle = future.result()
		if self.goal_handle.accepted:
			self.get_logger().info("Request accepted")
			self.goal_handle.get_result_async().add_done_callback(self.goal_result_callback)
		else:
			self.get_logger().info("Goal Refused")

	def goal_result_callback(self, future):
		status = future.result().status
		response = future.result().result
		if status == GoalStatus.STATUS_SUCCEEDED:
			self.get_logger().info("success")
		elif status == GoalStatus.STATUS_ABORTED:
			self.get_logger().info("Aborted")
		elif status == GoalStatus.STATUS_CANCELED:
			self.get_logger().info("Cancelled")
		self.get_logger().info("Got Result " + str(response.done))

	def callback_ollama(self, request: OllamaResp.Request, response: OllamaResp.Response):
		self.query = request.request
		self.get_logger().info(f"Received the request : {self.query}")
		response.success = True
		response.response = str(self.treatment(self.query))
		return response

	def treatment(self, requete):
		response = ollama.chat(
			"qwen3:8b",
			messages=[
			{
			"role": "user", "content": requete
			}], 
			think= False,
			tools=tools
			)
		tool_call = response.message.tool_calls[0].function
		#print(tool_call)

		tool_name = tool_call.name
		tool_argument = tool_call.arguments
		#print(f"The name : {tool_name}, The arguments : {tool_arguments}")

		result = {}
		if tool_name == "move_to":
			result = {
				"name" : tool_name,
				"arguments" : tool_argument['distance']
			}
			self.send_goal(result['arguments'], 0.5)
		elif tool_name == "move_arm":
			result = {
				"name" : tool_name,
				"arguments" : tool_argument
			}
			
			self.send_goal(result['arguments'], 0.5)
		return result

def main():
	#request = input("Your request please : ")
	rclpy.init()
	node = newclass()
	rclpy.spin(node)

if __name__ == '__main__':
	main()