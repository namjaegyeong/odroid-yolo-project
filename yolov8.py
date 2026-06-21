from ultralytics import YOLO

import rclpy
from rclpy.node import Node
from ros2.image_raw_subscriber import ImageRawSubscriber

# ros2 publisher node 코드
rclpy.init()
node = ImageRawSubscriber()

# ros2 node callback 실행
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass

node.destroy_node()
rclpy.shutdown()
