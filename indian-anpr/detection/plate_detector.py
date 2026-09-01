import os

import cv2
import numpy as np
from ultralytics import YOLO

from utils.logger import app_logger


class PlateDetector:
    def __init__(self, model_path: str = "models/indian_plate.pt"):
        self.model_path = model_path
        self.model = None
        self.is_custom_model = os.path.exists(model_path)

        if self.is_custom_model:
            self.model = YOLO(model_path)
            app_logger.info(f"Loaded Indian plate model from {model_path}")
        else:
            app_logger.warning("Indian plate model not found. Using experimental OpenCV fallback.")

    def detect(self, vehicle_crop: np.ndarray):
        if vehicle_crop is None or vehicle_crop.size == 0:
            return []

        if self.is_custom_model and self.model is not None:
            results = self.model(vehicle_crop, verbose=False, conf=0.25)
            boxes = []
            if results and len(results) > 0 and results[0].boxes is not None:
                for box in results[0].boxes:
                    boxes.append(box.xyxy[0].cpu().numpy().astype(int))
            return boxes

        return self._opencv_contour_fallback(vehicle_crop)

    def _opencv_contour_fallback(self, img: np.ndarray):
        h, w = img.shape[:2]
        if h == 0 or w == 0:
            return []

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        candidates = []

        # --- Pass 1: Canny edge detection ---
        blur = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(blur, 30, 200)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        candidates += self._find_plate_contours(edged, h, w)

        # --- Pass 2: Adaptive threshold (better for uneven lighting) ---
        if not candidates:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            thresh = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 19, 9,
            )
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            candidates += self._find_plate_contours(thresh, h, w)

        if candidates:
            # Return the candidate with the best aspect ratio for Indian plates (~3.5:1)
            candidates.sort(key=lambda c: abs((c[2] - c[0]) / max(1, c[3] - c[1]) - 3.5))
            return [candidates[0]]

        return []

    def _find_plate_contours(self, binary_img: np.ndarray, frame_h: int, frame_w: int):
        """Find rectangular contours that could be license plates."""
        contours, _ = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

        results = []
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            # Try multiple tolerance levels for polygon approximation
            for eps in [0.02, 0.04, 0.06]:
                approx = cv2.approxPolyDP(contour, eps * peri, True)
                if 4 <= len(approx) <= 6:
                    x, y, bw, bh = cv2.boundingRect(approx)
                    aspect_ratio = bw / float(bh) if bh > 0 else 0
                    area = bw * bh
                    # Indian plates: aspect ratio ~1.5 to 7.0, min area 400px
                    if 1.5 <= aspect_ratio <= 7.0 and area > 400:
                        results.append(np.array([x, y, x + bw, y + bh]))
                    break  # Use the first matching tolerance
        return results
