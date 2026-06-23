#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import sys


class MotorTestNode(Node):
    """
    Specialized test node for brushless motor and analog output testing
    """

    def __init__(self):
        super().__init__('motor_test_node')
        
        # Create publisher for cmd_vel
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        
        self.get_logger().info('Motor Test Node started - Testing brushless motor control')

    def send_velocity_command(self, linear_x, angular_z, duration=3.0, description=""):
        """
        Send a velocity command for specified duration with description
        """
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        
        self.get_logger().info(f'🚀 {description}')
        self.get_logger().info(f'   Sending: linear_x={linear_x:.3f}, angular_z={angular_z:.3f}')
        
        if linear_x > 0:
            self.get_logger().info('   ✅ MOTOR SHOULD BE RUNNING')
            self.get_logger().info('   ✅ Analog output should be HIGH (~3.9V on pin 11)')
        else:
            self.get_logger().info('   🔴 MOTOR SHOULD BE STOPPED')
            self.get_logger().info('   📉 Analog output should be LOW (~1V on pin 11)')
        
        start_time = time.time()
        rate = self.create_rate(10)  # 10 Hz publishing
        
        while (time.time() - start_time) < duration:
            self.cmd_vel_publisher.publish(msg)
            rate.sleep()
        
        # Send stop command at end
        stop_msg = Twist()
        self.cmd_vel_publisher.publish(stop_msg)
        self.get_logger().info('   ⏹️  Command complete - STOPPED')

    def run_motor_test_sequence(self):
        """
        Run a comprehensive motor test sequence
        """
        tests = [
            # (linear_x, angular_z, duration, description)
            (0.0, 0.0, 3.0, "Initial Stop - Red LED ON, Motor OFF, Analog LOW"),
            
            (0.1, 0.0, 4.0, "Slow Forward - Motor should run at base speed"),
            (0.0, 0.0, 2.0, "Stop - Motor should stop immediately"),
            
            (0.3, 0.0, 4.0, "Medium Forward - Motor should run faster"),
            (0.0, 0.0, 2.0, "Stop - Check motor stops quickly"),
            
            (0.5, 0.0, 4.0, "Fast Forward - Motor at higher speed"),
            (0.0, 0.0, 2.0, "Stop - Verify motor control"),
            
            (0.2, 0.5, 4.0, "Forward + Left Turn - Motor ON, Left LED blinking, Servo left"),
            (0.0, 0.0, 2.0, "Stop - All systems should stop"),
            
            (0.2, -0.5, 4.0, "Forward + Right Turn - Motor ON, Right LED blinking, Servo right"),
            (0.0, 0.0, 2.0, "Stop - Return to neutral"),
            
            (0.0, 0.8, 3.0, "Turn Left in Place - Motor OFF, Left LED blink, Servo left"),
            (0.0, -0.8, 3.0, "Turn Right in Place - Motor OFF, Right LED blink, Servo right"),
            
            (1.0, 0.0, 3.0, "Maximum Forward - Motor at highest safe speed"),
            (0.0, 0.0, 3.0, "Final Stop - All systems OFF"),
        ]
        
        self.get_logger().info('🔧 Starting Motor and Analog Output Test Sequence...')
        self.get_logger().info('=' * 60)
        self.get_logger().info('Monitor your Arduino Serial output at 9600 baud for detailed status!')
        self.get_logger().info('Watch for:')
        self.get_logger().info('  - "Motor RUNNING at XXXX microseconds" messages')
        self.get_logger().info('  - "Motor STOPPED (1500 microseconds)" messages') 
        self.get_logger().info('  - "Analog output (PWM): XXX" values in status reports')
        self.get_logger().info('=' * 60)
        
        for i, (linear_x, angular_z, duration, description) in enumerate(tests):
            self.get_logger().info(f'\n📋 Test {i+1}/{len(tests)}: {description}')
            self.send_velocity_command(linear_x, angular_z, duration, description)
            
            if i < len(tests) - 1:  # Don't pause after last test
                self.get_logger().info('⏸️  Pausing 2 seconds before next test...')
                time.sleep(2.0)
        
        self.get_logger().info('\n🎉 Motor test sequence completed!')
        
        # Final status check
        self.get_logger().info('\n📊 TEST RESULTS CHECKLIST:')
        self.get_logger().info('═' * 50)
        self.get_logger().info('✓ Did the motor run during forward commands?')
        self.get_logger().info('✓ Did the motor stop during stop commands?')
        self.get_logger().info('✓ Did LEDs blink correctly during turns?')
        self.get_logger().info('✓ Did servo move for steering commands?')
        self.get_logger().info('✓ Did analog output change between moving/stopped?')
        self.get_logger().info('✓ Check Arduino Serial Monitor for "Motor RUNNING" messages')

    def run_analog_test(self):
        """
        Specific test for analog output functionality
        """
        self.get_logger().info('🔌 Testing Analog Output Functionality')
        self.get_logger().info('=' * 40)
        self.get_logger().info('This test focuses on the analog output on pin 11')
        self.get_logger().info('Monitor Arduino Serial output for "Analog output (PWM)" values')
        self.get_logger().info('')
        
        tests = [
            (0.0, 0.0, 5.0, "Stopped State - Analog should be ~50 (~1V)"),
            (0.3, 0.0, 5.0, "Moving State - Analog should be ~200 (~3.9V)"),
            (0.0, 0.0, 5.0, "Stopped Again - Analog should drop to ~50"),
            (0.5, 0.2, 5.0, "Moving + Turning - Analog should be ~200"),
            (0.0, 0.0, 3.0, "Final Stop - Analog should be ~50"),
        ]
        
        for linear_x, angular_z, duration, description in tests:
            self.get_logger().info(f'🔍 {description}')
            self.send_velocity_command(linear_x, angular_z, duration)
            time.sleep(1.0)

    def interactive_motor_test(self):
        """
        Interactive mode for manual motor testing
        """
        self.get_logger().info('🎮 Interactive Motor Test Mode')
        self.get_logger().info('=' * 35)
        self.get_logger().info('Commands:')
        self.get_logger().info('  forward <speed>     - Move forward (e.g., "forward 0.5")')
        self.get_logger().info('  turn <left/right>   - Turn in place (e.g., "turn left")')
        self.get_logger().info('  move <linear> <angular> - Custom command')
        self.get_logger().info('  stop                - Stop all movement')
        self.get_logger().info('  quit                - Exit')
        self.get_logger().info('')
        
        while True:
            try:
                user_input = input('motor_test> ').strip().lower()
                
                if user_input == 'quit':
                    break
                elif user_input == 'stop':
                    self.send_velocity_command(0.0, 0.0, 1.0, "Manual Stop")
                elif user_input.startswith('forward'):
                    try:
                        speed = float(user_input.split()[1]) if len(user_input.split()) > 1 else 0.3
                        self.send_velocity_command(speed, 0.0, 3.0, f"Manual Forward at {speed}")
                    except (IndexError, ValueError):
                        print('Usage: forward <speed> (e.g., "forward 0.5")')
                elif user_input.startswith('turn'):
                    direction = user_input.split()[1] if len(user_input.split()) > 1 else 'left'
                    angular = 0.5 if direction == 'left' else -0.5
                    self.send_velocity_command(0.0, angular, 3.0, f"Manual Turn {direction}")
                elif user_input.startswith('move'):
                    try:
                        parts = user_input.split()
                        linear = float(parts[1])
                        angular = float(parts[2])
                        self.send_velocity_command(linear, angular, 3.0, f"Manual Move {linear}, {angular}")
                    except (IndexError, ValueError):
                        print('Usage: move <linear> <angular> (e.g., "move 0.5 0.3")')
                else:
                    print('Unknown command. Type "quit" to exit.')
                    
            except KeyboardInterrupt:
                break
        
        # Final stop
        stop_msg = Twist()
        self.cmd_vel_publisher.publish(stop_msg)


def main(args=None):
    rclpy.init(args=args)
    
    node = MotorTestNode()
    
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == 'auto':
                node.run_motor_test_sequence()
            elif sys.argv[1] == 'analog':
                node.run_analog_test()
            elif sys.argv[1] == 'interactive':
                node.interactive_motor_test()
            else:
                print("Usage: python3 test_motor_control.py [auto|analog|interactive]")
        else:
            # Default to interactive mode
            node.interactive_motor_test()
            
    except KeyboardInterrupt:
        pass
    finally:
        # Send final stop command
        stop_msg = Twist()
        node.cmd_vel_publisher.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()