from typing import List, Tuple

import cv2
import numpy as np


class PlatePreprocessor:
    @staticmethod
    def get_variants(plate_crop: np.ndarray) -> List[Tuple[str, np.ndarray]]:
        if plate_crop is None or plate_crop.size == 0:
            return []

        variants: List[Tuple[str, np.ndarray]] = []

        h, w = plate_crop.shape[:2]
        scale = max(2.5, 300.0 / max(w, 1))
        resized = cv2.resize(plate_crop, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
        padded = cv2.copyMakeBorder(resized, 15, 15, 15, 15, cv2.BORDER_REPLICATE)
        variants.append(("original_upscaled", padded))

        gray = cv2.cvtColor(padded, cv2.COLOR_BGR2GRAY) if len(padded.shape) == 3 else padded
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)
        variants.append(("clahe", contrast))

        denoised = cv2.bilateralFilter(contrast, 9, 75, 75)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        variants.append(("sharpened", sharpened))

        _, otsu = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(("otsu", otsu))

        adaptive = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 19, 9
        )
        variants.append(("adaptive", adaptive))

        return variants
