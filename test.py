#!/usr/bin/env python3

import serial
import serial.tools.list_ports
import time
import sys

def list_serial_ports():
    """List all available serial ports"""
    print("Available serial ports:")
    ports = serial.tools.list_ports.comports()
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device} - {port.description}")
    return [port.device for port in ports]

def test_arduino_connection(port, baud_rate=9600):
    """Test direct serial connection to Arduino"""
    try:
        print(f"\nTesting connection to {port} at {baud_rate} baud...")
        
        # Open serial connection
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(2)  # Wait for Arduino to reset
        
        print("Connection established. Waiting for Arduino ready message...")
        
        # Read any initial messages from Arduino
        start_time = time.time()
        while time.time() - start_time < 5:
            if ser.in_waiting:
                response = ser.readline().decode().strip()
                print(f"Arduino: {response}")
                if "ready" in response.lower():
                    print("✓ Arduino is ready!")
                    break
        
        # Test sending commands
        test_commands = [
            ("0.0,0.0", "Stop command (red LED should turn ON)"),
            ("0.5,0.0", "Forward command (red LED OFF, motor should run)"),
            ("0.5,0.5", "Forward + left turn (left LED should blink)"),
            ("0.5,-0.5", "Forward + right turn (right LED should blink)"),
            ("0.0,0.8", "Turn left in place (left LED blink, no motor)"),
            ("0.0,-0.8", "Turn right in place (right LED blink, no motor)"),
            ("0.0,0.0", "Final stop"),
        ]
        
        for cmd, description in test_commands:
            print(f"\nSending: {cmd} ({description})")
            ser.write(f"{cmd}\n".encode())
            ser.flush()
            
            # Read any response
            time.sleep(0.1)
            if ser.in_waiting:
                response = ser.readline().decode().strip()
                print(f"Arduino response: {response}")
            
            # Wait for user to observe
            input("Press Enter to continue to next test...")
        
        ser.close()
        print("\n✓ Test completed successfully!")
        return True
        
    except serial.SerialException as e:
        print(f"✗ Serial connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def check_ros2_node_output():
    """Check if ROS2 node is running and outputting debug info"""
    print("\n" + "="*50)
    print("ROS2 NODE DEBUG CHECK")
    print("="*50)
    print("To check if your ROS2 node is working:")
    print("1. In another terminal, run:")
    print("   ros2 run arduino_robot_controller arduino_controller_node --ros-args --log-level DEBUG")
    print("2. In another terminal, publish test commands:")
    print("   ros2 topic pub /cmd_vel geometry_msgs/Twist \"linear: {x: 0.5} angular: {z: 0.0}\"")
    print("3. Check if you see debug messages about sending commands to Arduino")
    print("4. Look for any error messages about serial communication")

def main():
    print("Arduino Hardware Debug Tool")
    print("="*40)
    
    # List available ports
    available_ports = list_serial_ports()
    
    if not available_ports:
        print("No serial ports found. Is Arduino connected?")
        return
    
    # Get port selection
    if len(available_ports) == 1:
        selected_port = available_ports[0]
        print(f"Using only available port: {selected_port}")
    else:
        try:
            port_index = int(input(f"Select port (0-{len(available_ports)-1}): "))
            selected_port = available_ports[port_index]
        except (ValueError, IndexError):
            print("Invalid selection. Using first port.")
            selected_port = available_ports[0]
    
    # Test connection
    success = test_arduino_connection(selected_port)
    
    if not success:
        print("\nTroubleshooting tips:")
        print("1. Check if Arduino is properly connected via USB")
        print("2. Verify Arduino code is uploaded correctly")
        print("3. Try different baud rates (9600, 115200)")
        print("4. Check if another program is using the serial port")
        print("5. Try unplugging and reconnecting Arduino")
    
    # ROS2 debugging info
    check_ros2_node_output()

if __name__ == "__main__":
    main()