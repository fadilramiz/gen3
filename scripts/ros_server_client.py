#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import ollama
from std_msgs.msg import String
from my_robot_interfaces.srv import OllamaResp

class ollama_listener(Node):
	"""docstring for ollama_listener"""
	def __init__(self):
		super().__init__("ollama_listen")

		self.client = self.create_client(OllamaResp, "ollama_query")

	def call_ollama(self, msg):
		while not self.client.wait_for_service(1.0):
			self.get_logger().info("Waiting for service...")
		request = OllamaResp.Request()
		request.request = msg
		future = self.client.call_async(request)
		#future.add_done_callback(self.callback_ollama_response)
		return future

	def callback_ollama_response(self, future):
		respond = future.result()
		self.get_logger().info(f"Success flag: {str(respond.success)}")
		self.get_logger().info(f"Response: {str(respond.response)}")


def main():
	demand = input("Your Query : ")
	rclpy.init()
	node = ollama_listener()
	future = node.call_ollama(demand)
	rclpy.spin_until_future_complete(node, future)
	if future.done():
		node.callback_ollama_response(future)
	rclpy.shutdown()

if __name__ == '__main__':
	main()


