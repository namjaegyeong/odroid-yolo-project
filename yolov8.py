from ultralytics import YOLO

# Load a COCO-pretrained YOLOv8n model
model = YOLO("yolov8n.pt")

# Display model information (optional)
model.info()

# Run inference (detection) on CPU
results = model.predict(
    source="test.jpg",
    device="cpu"
)

for box in results[0].boxes:
    cls = int(box.cls)
    conf = float(box.conf)

    print(
        model.names[cls],
        conf
    )