# ROS2 dependencies

This project expects ROS2 Humble to provide the ROS Python modules.
Do not install these packages with pip.

```bash
sudo apt update
sudo apt install \
  ros-humble-cv-bridge \
  ros-humble-rclpy \
  ros-humble-sensor-msgs \
  ros-humble-std-msgs
```

Before running the node:

```bash
source /opt/ros/humble/setup.bash
source venv/bin/activate
python yolov8.py
```

The camera subscriber uses `BEST_EFFORT` QoS because many ROS camera
publishers publish `/camera/image_raw` with sensor-data QoS.
