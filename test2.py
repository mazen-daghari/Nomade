#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import serial.tools.list_ports
import threading
import time
import os


class ArduinoControllerDebugNode(Node):
    """
    Enhanced Arduino Controller Node with extensive debugging output
    """

    def __init__(self):
        super().__init__('arduino_controller_debug_node')
        
        # Declare parameters
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 9600)
        self.declare_parameter('cmd_vel_topic', 'cmd_vel')
        self.declare_parameter('debug_level', 'INFO')  # DEBUG, INFO, WARN, ERROR
        
        # Get parameters
        self.serial_port = self.get_parameter('serial_port').get_parameter_value().string_value
        self.baud_rate = self.get_parameter('baud_rate').get_parameter_value().integer_value
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').get_parameter_value().string_value
        self.debug_level = self.get_parameter('debug_level').get_parameter_value().string_value
        
        # Debug and monitoring variables
        self.commands_sent = 0
        self.connection_attempts = 0
        self.last_successful_send = 0
        self.arduino_responses = []
        
        # Initialize serial connection
        self.serial_connection = None
        self.serial_lock = threading.Lock()
        
        # Find Arduino if port is 'auto'
        if self.serial_port == 'auto':
            self.serial_port = self.find_arduino_port()
        
        # Initialize subscriber
        self.cmd_vel_subscriber = self.create_subscription(
            Twist,
            self.cmd_vel_topic,
            self.cmd_vel_callback,
            10
        )
        
        # Create timers for monitoring
        self.connection_timer = self.create_timer(2.0, self.monitor_connection)
        self.stats_timer = self.create_timer(10.0, self.print_statistics)
        
        # Command tracking
        self.last_linear_x = 0.0
        self.last_angular_z = 0.0
        self.last_command_time = time.time()
        
        self.get_logger().info(f'=== ARDUINO DEBUG NODE STARTED ===')
        self.get_logger().info(f'Target serial port: {self.serial_port}')
        self.get_logger().info(f'Baud rate: {self.baud_rate}')
        self.get_logger().info(f'Listening on topic: {self.cmd_vel_topic}')
        
        # Initial connection attempt
        self.connect_to_arduino()

    def find_arduino_port(self):
        """Find Arduino port automatically"""
        self.get_logger().info("Auto-detecting Arduino port...")
        ports = serial.tools.list_ports.comports()
        
        self.get_logger().info(f"Available serial ports:")
        for port in ports:
            self.get_logger().info(f"  {port.device}: {port.description}")
        
        # Look for Arduino-specific identifiers
        arduino_ports = []
        for port in ports:
            desc = port.description.lower()
            device = port.device.lower()
            
            if any(keyword in desc for keyword in ['arduino', 'uno']) or \
               any(keyword in device for keyword in ['ttyacm', 'ttyusb']):
                arduino_ports.append(port.device)
        
        if arduino_ports:
            selected_port = arduino_ports[0]
            self.get_logger().info(f"Found potential Arduino port: {selected_port}")
            return selected_port
        else:
            self.get_logger().warn("No Arduino port found automatically. Using /dev/ttyACM0")
            return "/dev/ttyACM0"

    def connect_to_arduino(self):
        """Establish serial connection with detailed logging"""
        self.connection_attempts += 1
        
        try:
            self.get_logger().info(f"Connection attempt #{self.connection_attempts}")
            self.get_logger().info(f"Trying to connect to: {self.serial_port}")
            
            # Check if port exists
            if not os.path.exists(self.serial_port):
                self.get_logger().error(f"Serial port {self.serial_port} does not exist!")
                self.get_logger().info("Available ports:")
                for port in serial.tools.list_ports.comports():
                    self.get_logger().info(f"  {port.device}")
                return False
            
            with self.serial_lock:
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.close()
                    self.get_logger().info("Closed existing connection")
                
                self.serial_connection = serial.Serial(
                    port=self.serial_port,
                    baudrate=self.baud_rate,
                    timeout=2.0,
                    write_timeout=2.0
                )
                
                self.get_logger().info(f"Serial port opened successfully")
                self.get_logger().info(f"Port settings: {self.serial_connection}")
                
                # Wait for Arduino to initialize
                self.get_logger().info("Waiting for Arduino to initialize...")
                time.sleep(3.0)  # Longer wait for Arduino reset
                
                # Clear any startup messages
                if self.serial_connection.in_waiting:
                    startup_msg = self.serial_connection.read_all().decode('utf-8', errors='ignore')
                    self.get_logger().info(f"Arduino startup message: {startup_msg.strip()}")
                
                # Test connection with a simple command
                self.get_logger().info("Testing connection with stop command...")
                test_success = self.send_command_to_arduino(0.0, 0.0, test_mode=True)
                
                if test_success:
                    self.get_logger().info("✓ Arduino connection established successfully!")
                    return True
                else:
                    self.get_logger().error("✗ Connection test failed")
                    return False
                
        except serial.SerialException as e:
            self.get_logger().error(f"Serial connection failed: {e}")
            self.get_logger().error(f"Make sure Arduino is connected and you have permission to access {self.serial_port}")
            self.get_logger().error("Try: sudo chmod 666 {self.serial_port} or add user to dialout group")
        except Exception as e:
            self.get_logger().error(f"Unexpected error during connection: {e}")
        
        self.serial_connection = None
        return False

    def send_command_to_arduino(self, linear_x, angular_z, test_mode=False):
        """Send command with detailed logging"""
        if not self.serial_connection or not self.serial_connection.is_open:
            if not test_mode:
                self.get_logger().warn("Cannot send command: No Arduino connection")
            return False
        
        try:
            with self.serial_lock:
                command = f"{linear_x:.3f},{angular_z:.3f}\n"
                
                if self.debug_level == 'DEBUG' or test_mode:
                    self.get_logger().info(f"Sending to Arduino: {command.strip()}")
                
                # Send command
                bytes_written = self.serial_connection.write(command.encode())
                self.serial_connection.flush()
                
                if self.debug_level == 'DEBUG':
                    self.get_logger().info(f"Bytes written: {bytes_written}")
                
                # Try to read response
                response_timeout = time.time() + 1.0
                response = ""
                
                while time.time() < response_timeout:
                    if self.serial_connection.in_waiting:
                        try:
                            response = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                            if response:
                                self.arduino_responses.append(response)
                                if self.debug_level == 'DEBUG' or test_mode:
                                    self.get_logger().info(f"Arduino response: {response}")
                                break
                        except:
                            pass
                    time.sleep(0.01)
                
                self.commands_sent += 1
                self.last_successful_send = time.time()
                
                if test_mode:
                    self.get_logger().info(f"Command sent successfully. Response: {response if response else 'None'}")
                
                return True
                
        except serial.SerialException as e:
            self.get_logger().error(f"Serial write error: {e}")
            self.serial_connection = None
            return False
        except Exception as e:
            self.get_logger().error(f"Unexpected error sending command: {e}")
            return False

    def cmd_vel_callback(self, msg):
        """Enhanced cmd_vel callback with debugging"""
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        
        self.get_logger().info(f"Received cmd_vel: linear_x={linear_x:.3f}, angular_z={angular_z:.3f}")
        
        # Analyze command
        if linear_x == 0.0 and angular_z == 0.0:
            self.get_logger().info("→ STOP command (red LED should be ON)")
        elif linear_x > 0.0 and abs(angular_z) < 0.1:
            self.get_logger().info("→ FORWARD command (motor should run, red LED OFF)")
        elif linear_x > 0.0 and angular_z > 0.1:
            self.get_logger().info("→ FORWARD + LEFT TURN (left LED should blink)")
        elif linear_x > 0.0 and angular_z < -0.1:
            self.get_logger().info("→ FORWARD + RIGHT TURN (right LED should blink)")
        elif abs(linear_x) < 0.1 and angular_z > 0.1:
            self.get_logger().info("→ TURN LEFT IN PLACE (left LED blink, no motor)")
        elif abs(linear_x) < 0.1 and angular_z < -0.1:
            self.get_logger().info("→ TURN RIGHT IN PLACE (right LED blink, no motor)")
        
        # Update tracking
        self.last_command_time = time.time()
        self.last_linear_x = linear_x
        self.last_angular_z = angular_z
        
        # Send to Arduino
        success = self.send_command_to_arduino(linear_x, angular_z)
        
        if success:
            self.get_logger().info("✓ Command sent to Arduino successfully")
        else:
            self.get_logger().error("✗ Failed to send command to Arduino")

    def monitor_connection(self):
        """Enhanced connection monitoring"""
        current_time = time.time()
        
        # Check command timeout
        if current_time - self.last_command_time > 2.0:
            if self.last_linear_x != 0.0 or self.last_angular_z != 0.0:
                self.get_logger().info("Command timeout - sending stop command")
                self.send_command_to_arduino(0.0, 0.0)
                self.last_linear_x = 0.0
                self.last_angular_z = 0.0
        
        # Check connection status
        if not self.serial_connection or not self.serial_connection.is_open:
            self.get_logger().warn("Arduino connection lost. Attempting to reconnect...")
            self.connect_to_arduino()
        else:
            # Test connection health
            if current_time - self.last_successful_send > 5.0:
                self.get_logger().info("Testing connection health...")
                self.send_command_to_arduino(self.last_linear_x, self.last_angular_z, test_mode=True)

    def print_statistics(self):
        """Print detailed statistics"""
        self.get_logger().info("=== CONNECTION STATISTICS ===")
        self.get_logger().info(f"Commands sent: {self.commands_sent}")
        self.get_logger().info(f"Connection attempts: {self.connection_attempts}")
        self.get_logger().info(f"Serial port: {self.serial_port}")
        self.get_logger().info(f"Connection status: {'CONNECTED' if self.serial_connection and self.serial_connection.is_open else 'DISCONNECTED'}")
        
        if self.arduino_responses:
            self.get_logger().info(f"Recent Arduino responses ({len(self.arduino_responses)} total):")
            for response in self.arduino_responses[-3:]:  # Show last 3 responses
                self.get_logger().info(f"  Arduino: {response}")
        else:
            self.get_logger().warn("No responses received from Arduino")

    def destroy_node(self):
        """Enhanced cleanup"""
        self.get_logger().info("Shutting down Arduino controller...")
        
        # Send stop command
        if self.serial_connection and self.serial_connection.is_open:
            self.get_logger().info("Sending final stop command...")
            self.send_command_to_arduino(0.0, 0.0)
            time.sleep(0.2)
        
        # Close connection
        with self.serial_lock:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                self.get_logger().info("Serial connection closed")
        
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = ArduinoControllerDebugNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()