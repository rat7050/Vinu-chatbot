import argparse

import cv2
import yaml

from database.database import DatabaseManager
from ocr.paddle_ocr import LocalPaddleOCR
from services.anpr_pipeline import ANPRPipeline


def run_camera(cam_index: int):
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    db = DatabaseManager(config["database"]["path"])
    ocr = LocalPaddleOCR()
    pipeline = ANPRPipeline(config, db, ocr)

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print(f"Error: Could not access camera index {cam_index}")
        return

    print(f"Running ANPR on Camera #{cam_index}. Press 'q' to quit.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab camera frame.")
            break

        annotated_frame, detections = pipeline.process_frame(frame, camera_id=f"CAM_{cam_index}")
        for detection in detections:
            print(f"[CONFIRMED PLATE] {detection['plate']} ({detection['conf']}) at {detection['time']}")

        cv2.imshow("Indian ANPR - Live Stream", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ANPR on local camera stream")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (e.g. 0, 1)")
    args = parser.parse_args()
    run_camera(args.camera)
