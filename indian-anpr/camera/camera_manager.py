import time

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal

from camera.video_source import VideoCaptureSource
from services.anpr_pipeline import ANPRPipeline
from utils.logger import app_logger


class CameraWorker(QThread):
    frame_ready = Signal(np.ndarray, float)
    detection_occurred = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, source, pipeline: ANPRPipeline, camera_id: str = "CAM_0"):
        super().__init__()
        self.source_val = source
        self.pipeline = pipeline
        self.camera_id = camera_id
        self.is_running = True

    def run(self):
        video_cap = VideoCaptureSource(self.source_val)
        if not video_cap.cap or not video_cap.cap.isOpened():
            self.error_occurred.emit(f"Failed to connect to camera source: {self.source_val}")
            return

        prev_time = time.time()
        fps_smooth = 0.0

        while self.is_running:
            ret, frame = video_cap.read()
            if not ret:
                if isinstance(self.source_val, str) and not self.source_val.startswith("rtsp"):
                    video_cap.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                self.error_occurred.emit("Camera feed disconnected.")
                break

            try:
                annotated_frame, detections = self.pipeline.process_frame(frame, self.camera_id)
                for detection in detections:
                    self.detection_occurred.emit(detection)
            except Exception as exc:
                app_logger.error(f"Inference error: {exc}")
                annotated_frame = frame

            curr_time = time.time()
            fps = 1.0 / max(curr_time - prev_time, 0.001)
            prev_time = curr_time
            fps_smooth = (0.9 * fps_smooth) + (0.1 * fps)
            self.frame_ready.emit(annotated_frame, fps_smooth)

        video_cap.release()

    def stop(self):
        self.is_running = False
        self.wait()
