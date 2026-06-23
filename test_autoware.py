#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import serial

class AutowareToArduino(Node):
    def __init__(self):
        super().__init__('autoware_to_arduino')

        # Subscribe to Autoware twist topic
        self.subscription = self.create_subscription(
            TwistStamped,
            '/vehicle/status/twist',   # Autoware twist feedback
            self.twist_callback,
            10
        )

        # Arduino serial
        self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        self.get_logger().info("Connected to Arduino on /dev/ttyACM0")

    def twist_callback(self, msg: TwistStamped):
        linear = msg.twist.linear.x   # m/s
        angular = msg.twist.angular.z # rad/s

        if linear > 0.05:
            self.arduino.write(b"MOVE\n")
            self.get_logger().info("MOVE")
        else:
            self.arduino.write(b"STOP\n")
            self.get_logger().info("STOP")

        if angular > 0.1:
            self.arduino.write(b"LEFT\n")
            self.get_logger().info("LEFT")
        elif angular < -0.1:
            self.arduino.write(b"RIGHT\n")
            self.get_logger().info("RIGHT")

def main(args=None):
    rclpy.init(args=args)
    node = AutowareToArduino()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
