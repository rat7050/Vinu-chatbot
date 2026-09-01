import cv2
import numpy as np


def draw_labeled_box(
    img: np.ndarray,
    box: tuple,
    label: str,
    color: tuple = (0, 255, 0),
    line_thickness: int = 2,
    font_scale: float = 0.5,
    font_thickness: int = 1,
):
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, line_thickness)

    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
    label_y = max(y1, h + 10)
    cv2.rectangle(img, (x1, label_y - h - 6), (x1 + w + 8, label_y + 4), color, -1)
    cv2.putText(
        img,
        label,
        (x1 + 4, label_y - 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0) if sum(color) > 380 else (255, 255, 255),
        font_thickness,
        lineType=cv2.LINE_AA,
    )

    return img
