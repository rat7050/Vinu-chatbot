import argparse

import cv2
import yaml

from database.database import DatabaseManager
from ocr.paddle_ocr import LocalPaddleOCR
from services.anpr_pipeline import ANPRPipeline


def run_video(video_path: str):
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    db = DatabaseManager(config["database"]["path"])
    ocr = LocalPaddleOCR()
    pipeline = ANPRPipeline(config, db, ocr)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return

    print("Processing video file locally. Press 'q' to stop.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        annotated_frame, detections = pipeline.process_frame(frame, camera_id="VIDEO_FILE")
        for detection in detections:
            print(f"[NEW DETECTION] Plate: {detection['plate']} | Type: {detection['type']} | Conf: {detection['conf']}")

        cv2.imshow("Indian ANPR - Offline Video Mode", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ANPR on a local video file")
    parser.add_argument("--video", type=str, required=True, help="Path to video file")
    args = parser.parse_args()
    run_video(args.video)
