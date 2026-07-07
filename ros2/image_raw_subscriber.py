import threading
import time
import json
from pathlib import Path

from std_msgs.msg import String

from ultralytics import YOLO

from rclpy.node import Node
from rclpy.qos import DurabilityPolicy
from rclpy.qos import HistoryPolicy
from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

MODEL_PATH = Path(__file__).resolve().parents[1] / "yolov8n.pt"
model = YOLO(str(MODEL_PATH))


class ImageRawSubscriber(Node):

    def __init__(self):
        super().__init__('image_raw_sub')

        self.latest_frame = None
        self.latest_frame_id = 0
        self.processed_frame_id = 0
        self.running = True
        self.lock = threading.Lock()
        self.bridge = CvBridge()

        self.result_pub = self.create_publisher(
            String,
            "/yolo/detections",
            10
        )

        camera_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )

        self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            camera_qos
        )

        self.predict_thread = threading.Thread(
            target=self.predict_loop,
            daemon=True
        )
        self.predict_thread.start()

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding="bgr8"
            )
        except Exception as exc:
            self.get_logger().warning(
                f"Failed to convert image message: {exc}"
            )
            return

        with self.lock:
            self.latest_frame = frame
            self.latest_frame_id += 1

    def predict_loop(self):
        while self.running:
            with self.lock:
                frame = None if self.latest_frame is None else self.latest_frame.copy()
                frame_id = self.latest_frame_id

            if frame is None or frame_id == self.processed_frame_id:
                time.sleep(0.01)
                continue

            self.processed_frame_id = frame_id

            results = model.predict(
                source=frame,
                conf=0.25,
                verbose=False
            )

            detections = []

            for box in results[0].boxes:
                detections.append({
                    "cls": int(box.cls.item()),
                    "name": results[0].names[int(box.cls.item())],
                    "conf": float(box.conf.item()),
                    "xyxy": box.xyxy.cpu().numpy()[0].tolist()
                })

            self.publish_result(detections)
            time.sleep(0.001)

    def publish_result(self, detections):
        msg = String()

        msg.data = json.dumps(detections)

        self.result_pub.publish(msg)

    def destroy_node(self):
        self.running = False
        if self.predict_thread.is_alive():
            self.predict_thread.join(timeout=1.0)
        super().destroy_node()
