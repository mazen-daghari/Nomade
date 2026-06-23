#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import time

class BrushlessMotorNode(Node):
    def __init__(self):
        super().__init__('brushless_motor_node')

        # Serial port to Arduino
        try:
            self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            time.sleep(2)  # wait for Arduino reset
            self.get_logger().info("✅ Connected to Arduino on /dev/ttyACM0")
        except Exception as e:
            self.get_logger().error(f"❌ Could not open serial port: {e}")
            self.arduino = None

        # Subscribe to cmd_vel
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.get_logger().info("🚀 Brushless Motor Node started, waiting for /cmd_vel commands")

    def cmd_vel_callback(self, msg: Twist):
        """
        Callback when /cmd_vel is received
        """
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        if linear_x > 0.01:
            throttle = self.map_speed_to_pwm(linear_x)
            self.get_logger().info(f"✅ MOTOR RUNNING | linear_x={linear_x:.2f}, throttle={throttle}")
            self.send_command(throttle, angular_z)
        else:
            self.get_logger().info("🛑 MOTOR STOPPED")
            self.send_command(1500, 0.0)  # neutral

        if angular_z > 0.1:
            self.get_logger().info("↪️ TURN LEFT")
        elif angular_z < -0.1:
            self.get_logger().info("↩️ TURN RIGHT")

    def map_speed_to_pwm(self, speed: float) -> int:
        """
        Map linear speed (0.0–1.0 m/s) to ESC PWM (1500–2000 µs)
        """
        min_pwm = 1500
        max_pwm = 2000
        return int(min_pwm + (max_pwm - min_pwm) * min(speed, 1.0))

    def send_command(self, throttle: int, angular: float):
        """
        Send throttle and steering commands to Arduino via Serial
        Format: "Txxxx,Sxxxx\n"
        """
        if self.arduino and self.arduino.is_open:
            # Map angular to servo PWM (1000–2000 µs)
            servo_pwm = 1500
            if angular > 0.1:
                servo_pwm = 1700
            elif angular < -0.1:
                servo_pwm = 1300

            command = f"T{throttle},S{servo_pwm}\n"
            self.arduino.write(command.encode('utf-8'))


def main(args=None):
    rclpy.init(args=args)
    node = BrushlessMotorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
