import datetime
import os

import cv2
import numpy as np

from utils.logger import app_logger


class SnapshotService:
    def __init__(self, directory: str = "data/snapshots"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def save_snapshot(
        self,
        frame: np.ndarray,
        plate_number: str,
        confidence: float,
        camera_name: str,
        vehicle_box: tuple = None,
        plate_box: tuple = None,
    ) -> str:
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plate_number}_{timestamp_str}.jpg"
        filepath = os.path.join(self.directory, filename)

        annotated = frame.copy()

        if vehicle_box is not None:
            x1, y1, x2, y2 = map(int, vehicle_box)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if plate_box is not None:
            px1, py1, px2, py2 = map(int, plate_box)
            cv2.rectangle(annotated, (px1, py1), (px2, py2), (0, 0, 255), 2)

        header_text = (
            f"Plate: {plate_number} | Conf: {confidence:.2f} | Cam: {camera_name} | "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        cv2.rectangle(annotated, (0, 0), (annotated.shape[1], 40), (0, 0, 0), -1)
        cv2.putText(
            annotated,
            header_text,
            (15, 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            lineType=cv2.LINE_AA,
        )

        cv2.imwrite(filepath, annotated)
        app_logger.info(f"Snapshot saved: {filepath}")
        return filepath
