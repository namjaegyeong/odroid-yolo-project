import threading
import time
from std_msgs.msg import String

from fsspec import json
import numpy as np
from ultralytics import YOLO

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

model = YOLO("yolov8n.pt")

class ImageRawSubscriber(Node):

    def __init__(self):
        super().__init__('image_raw_sub')

        self.latest_frame = None
        self.running = True
        self.lock = threading.Lock()

        self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            10
        )

        self.predict_thread = threading.Thread(
            target=self.predict_loop,
            daemon=True
        )
        self.predict_thread.start()

    def image_callback(self, msg):
        frame = np.frombuffer(
            msg.data,
            dtype=np.uint8
        ).reshape(
            msg.height,
            msg.width,
            3
        )

        with self.lock:
            self.latest_frame = frame

    def predict_loop(self):
        while self.running:
            with self.lock:
                frame = self.latest_frame

            if frame is None:
                time.sleep(0.01)
                continue

            results = model.predict(
                source=frame,
                conf=0.25,
                verbose=False
            )

            detections = []

            for box in results[0].boxes:
                detections.append({
                    "cls": int(box.cls),
                    "conf": float(box.conf),
                    "xyxy": box.xyxy.cpu().numpy()[0].tolist()
                })

            self.publish_result(detections)

    def publish_result(self, detections):

        msg = String()

        msg.data = json.dumps(detections)

        self.result_pub.publish(msg)

    def destroy_node(self):
        self.running = False
        super().destroy_node()