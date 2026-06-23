#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial

class CmdVelToArduino(Node):
    def __init__(self):
        super().__init__('cmdvel_to_arduino')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Change port according to your Arduino connection
        self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        self.get_logger().info("Connected to Arduino on /dev/ttyUSB0")

    def cmd_vel_callback(self, msg: Twist):
        angular = msg.angular.z

        if angular > 0.1:   # turning left
            self.arduino.write(b"LEFT\n")
            self.get_logger().info("Sent LEFT")
        elif angular < -0.1:  # turning right
            self.arduino.write(b"RIGHT\n")
            self.get_logger().info("Sent RIGHT")
        else:  # no turn
            self.arduino.write(b"STOP\n")
            self.get_logger().info("Sent STOP")

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelToArduino()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
