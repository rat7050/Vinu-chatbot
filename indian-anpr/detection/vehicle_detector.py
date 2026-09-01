import os

import cv2
import numpy as np
from ultralytics import YOLO

from utils.logger import app_logger


class VehicleDetector:
    COCO_VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

    def __init__(self, model_path: str = "models/vehicle_yolo.pt"):
        self.model_path = model_path
        self.model = None
        if os.path.exists(model_path):
            self.model = YOLO(model_path)
            app_logger.info(f"Loaded vehicle model from {model_path}")
        else:
            app_logger.warning(f"Vehicle model not found at {model_path}. Trying default YOLO model.")
            self.model = YOLO("yolov8n.pt")

    def track(self, frame: np.ndarray, tracker_type: str = "bytetrack.yaml"):
        if frame is None or frame.size == 0:
            return []

        results = self.model.track(
            source=frame,
            persist=True,
            classes=list(self.COCO_VEHICLE_CLASSES.keys()),
            tracker=tracker_type,
            verbose=False,
        )

        detections = []
        if results and len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes:
                if box.id is None:
                    continue
                track_id = int(box.id[0].item())
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                label = self.COCO_VEHICLE_CLASSES.get(cls_id, "vehicle")
                detections.append({
                    "track_id": track_id,
                    "box": xyxy,
                    "class_name": label,
                    "confidence": conf,
                })

        return detections
