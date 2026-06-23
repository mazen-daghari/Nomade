import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QTimer

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class LEDIndicator(QLabel):
    def __init__(self, label_text):
        super().__init__()
        self.setText(label_text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(100, 100)
        self.off_color = QColor('gray')
        self.on_color = QColor('green')
        self.setAutoFillBackground(True)
        self.set_state(False)

    def set_state(self, state):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, self.on_color if state else self.off_color)
        self.setPalette(palette)

class LEDMonitorGUI(Node, QWidget):
    def __init__(self):
        Node.__init__(self, 'led_monitor_gui')
        QWidget.__init__(self)

        # ROS 2 Subscriber (change topic if needed)
        self.sub = self.create_subscription(String, '/robot_leds', self.led_callback, 10)

        # Layout
        layout = QHBoxLayout()
        self.move_led = LEDIndicator('Move')
        self.stop_led = LEDIndicator('Stop')
        self.left_led = LEDIndicator('Left')
        self.right_led = LEDIndicator('Right')
        layout.addWidget(self.move_led)
        layout.addWidget(self.stop_led)
        layout.addWidget(self.left_led)
        layout.addWidget(self.right_led)
        self.setLayout(layout)
        self.setWindowTitle('Robot LED Monitor')

        # Timer for blinking left/right
        self.blink = False
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_timer.start(500)

        self.left_state = False
        self.right_state = False

    def led_callback(self, msg):
        """
        Expected message: string with letters:
        'M' -> moving, 'S' -> stopped, 'L' -> turning left, 'R' -> turning right
        Example: 'ML' means moving and turning left
        """
        self.left_state = 'L' in msg.data
        self.right_state = 'R' in msg.data
        self.move_led.set_state('M' in msg.data)
        self.stop_led.set_state('S' in msg.data)

    def toggle_blink(self):
        # Blink left/right if active
        self.blink = not self.blink
        self.left_led.set_state(self.blink if self.left_state else False)
        self.right_led.set_state(self.blink if self.right_state else False)

def main(args=None):
    rclpy.init(args=args)
    app = QApplication(sys.argv)
    gui_node = LEDMonitorGUI()
    gui_node.show()

    # Spin ROS node in a separate thread
    import threading
    def spin_node():
        rclpy.spin(gui_node)
    thread = threading.Thread(target=spin_node, daemon=True)
    thread.start()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()

