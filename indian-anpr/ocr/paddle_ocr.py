from typing import Tuple

import cv2
import numpy as np

from ocr.base_ocr import BaseOCR
from ocr.preprocessing import PlatePreprocessor
from utils.logger import app_logger


class LocalPaddleOCR(BaseOCR):
    def __init__(self):
        try:
            from paddleocr import PaddleOCR

            # `show_log` is not supported by the installed PaddleOCR version.
            # Retain the angle flag for compatibility; the library will warn when
            # the newer textline-orientation API is preferred.
            self.ocr = PaddleOCR(use_angle_cls=False, lang="en")
            app_logger.info("PaddleOCR engine initialized locally.")
        except Exception as exc:
            app_logger.error(f"Failed to initialize PaddleOCR: {exc}")
            raise exc

    def read_text(self, image: np.ndarray) -> Tuple[str, float]:
        if image is None or image.size == 0:
            return "", 0.0

        best_text = ""
        best_conf = 0.0

        for _, variant in PlatePreprocessor.get_variants(image):
            try:
                if len(variant.shape) == 2:
                    processed = cv2.cvtColor(variant, cv2.COLOR_GRAY2BGR)
                else:
                    processed = variant

                results = self.ocr.ocr(processed, cls=False)
                if not results or not results[0]:
                    continue

                full_text = ""
                conf_sum = 0.0
                count = 0
                for line in results[0]:
                    txt, conf = line[1][0], line[1][1]
                    full_text += txt
                    conf_sum += float(conf)
                    count += 1

                avg_conf = conf_sum / max(count, 1)
                if avg_conf > best_conf and len(full_text) >= 6:
                    best_text = full_text
                    best_conf = avg_conf
            except Exception:
                continue

        return best_text, best_conf
