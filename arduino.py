import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import os

class CmdVelToArduino(Node):
    def __init__(self):
        super().__init__('cmdvel_to_arduino')

        # Adjust topic name if using Autoware (commonly /twist_cmd or /vehicle/twist)
        self.sub = self.create_subscription(Twist, '/cmd_vel', self.callback, 10)

        # Serial port to Arduino
        self.ser = None
        self.port = '/dev/ttyACM0'  # Change if needed
        self.baudrate = 9600

        if os.path.exists(self.port):
            try:
                self.ser = serial.Serial(self.port, self.baudrate)
                self.get_logger().info(f"Connected to Arduino on {self.port}")
            except serial.SerialException as e:
                self.get_logger().error(f"Failed to open serial port: {e}")
        else:
            self.get_logger().warn(f"Serial port {self.port} not found. Connect Arduino.")

    def callback(self, msg: Twist):
        if self.ser is None or not self.ser.is_open:
            return  # Arduino not connected

        # Reset command
        command = b''

        # Forward / Stop
        if msg.linear.x != 0.0:
            command = b'M'  # Move
        else:
            command = b'S'  # Stop

        # Turn left / right
        if msg.angular.z > 0.0:
            command += b'L'
        elif msg.angular.z < 0.0:
            command += b'R'

        if command:
            try:
                self.ser.write(command)
                self.get_logger().info(f"Sent command: {command}")
            except serial.SerialException as e:
                self.get_logger().error(f"Failed to send command: {e}")

def main():
    rclpy.init()
    node = CmdVelToArduino()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

