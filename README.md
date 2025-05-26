
## About Nomade Rover Project
Nomade Rover is an advanced ROS 2 package designed for ROS 2 Foxy and above. It simulates and controls a tactical 4WD robotic platform equipped with perception modules (2D LiDAR, camera, etc.), autonomous navigation, and AI-powered detection (YOLOv8).

The package enables Gazebo simulation, RViz visualization, and YOLO-based object detection — perfect for prototyping smart surveillance, tactical mobility, and AI-enhanced robotics.
















![Logo](https://github.com/mazen-daghari/Mazen_4dw/blob/77e424a2dfffa17c5dbb93baea33e0d8d2a60c1e/logo.png)


## Features

* 4WD tactical rover with realistic physics (Ackermann-based mobility)

* Integrated camera for vision and detection

* 2D LiDAR for SLAM, obstacle avoidance, and perception

* Object detection using YOLOv8 (via Ultralytics)

* RViz integration for robot state and sensor visualization

* Modular and extendable launch files

* CAN-based assisted steering (real hardware in future phase)




## Installation

Create project directory

```bash
  mkdir -p ~/mazen_ws/src cd ~/mazen_ws/src
```

Clone the project

```bash
  git clone https://github.com/mazen-daghari/Mazen_4dw.git
```

Build project

```bash
 colcon build --symlink-install
```

Source project

```bash
  source install/setup.bash 
```

Launch Gazebo simulation
```bash
  ros2 launch mazen_mac1 gazebo_model.launch.py
  ```
Launch Yolo v8
``` bash
  ros2 launch recognition launch_yolov8.launch.py
```
## Roadmap


 * Build URDF of Nomade Rover

 * Integrate RGB camera , Depth camera , 2D lidar , 3d lidar, and IMU 

 * Add Extended Kalman Filter for sensor fusion

 * Integrate YOLOv8 with simulation

 * Add real-time CAN-based control interface

 * Deploy on hardware with ESP32 + Jetson
## Acknowledgements



* Ultralytics YOLOv8

* Gazebo

* ROS 2 & Nav2 Community
## Notes


* Make sure all dependencies (e.g., YOLOv8, camera drivers, etc.) are correctly installed.

* Tested on Ubuntu 20.04 with ROS 2 Foxy. Later ROS 2 versions like Humble and Iron should also work with minor adjustments.

- Copy models (e.g., person, SUV, stop sign, bus) to your ~/.gazebo/models directory. This step is only required once. (Note: This directory may be hidden; enable 'show hidden files' if needed).


* The Gazebo simulation and the recognition package must be executed simultaneously. This requires initiating their respective launch files in distinct terminal instances.


* For any further help contact me on dagmazen@gmail.com or via linkedin
## Authors

- [@mazen-daghari](https://www.github.com/mazen-daghari)


## License

This project is protected under the following license terms:


Copyright © 2025 Mazen Daghari. All rights reserved.

This software, including all source code, assets, and documentation, is the intellectual property of Mazen Daghari and is protected by international copyright laws.

Unauthorized copying, distribution, modification, reuse, or incorporation into other software or hardware projects is strictly prohibited without the express written permission of the author.

This project is licensed for private and non-commercial use only. Commercial use, redistribution, or derivative works are not permitted.

Violators may be subject to civil and criminal penalties as provided by law.

For licensing inquiries, collaborations, or permissions, please contact:
📧dagmazen@gmail.com


## System Snapshots

These application snapshots highlight the new feature.
