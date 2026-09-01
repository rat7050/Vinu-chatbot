from typing import Tuple

import cv2
import numpy as np

from ocr.base_ocr import BaseOCR
from ocr.preprocessing import PlatePreprocessor
from utils.logger import app_logger


class LocalEasyOCR(BaseOCR):
    def __init__(self):
        try:
            import easyocr

            self.reader = easyocr.Reader(["en"], gpu=False)
            app_logger.info("EasyOCR engine initialized locally.")
        except Exception as exc:
            app_logger.error(f"Failed to initialize EasyOCR: {exc}")
            raise exc

    def read_text(self, image: np.ndarray) -> Tuple[str, float]:
        if image is None or image.size == 0:
            return "", 0.0

        best_text = ""
        best_conf = 0.0

        for _, variant in PlatePreprocessor.get_variants(image):
            try:
                results = self.reader.readtext(variant)
                if not results:
                    continue

                full_text = "".join(res[1] for res in results)
                avg_conf = sum(float(res[2]) for res in results) / len(results)
                if avg_conf > best_conf and len(full_text) >= 6:
                    best_conf = avg_conf
                    best_text = full_text
            except Exception:
                continue

        return best_text, best_conf
