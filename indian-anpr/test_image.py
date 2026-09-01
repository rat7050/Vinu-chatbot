import argparse
import os

import cv2
import yaml

from detection.plate_detector import PlateDetector
from detection.vehicle_detector import VehicleDetector
from ocr.paddle_ocr import LocalPaddleOCR
from ocr.validator import IndianPlateValidator

__test__ = False


def test_single_image(image_path: str):
    if not os.path.exists(image_path):
        print(f"Error: Image path '{image_path}' not found.")
        return

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    frame = cv2.imread(image_path)
    if frame is None:
        print("Error: OpenCV failed to decode the image file.")
        return

    print("========================================")
    print(" Running Offline Indian ANPR Image Test ")
    print("========================================")

    v_detector = VehicleDetector(config["models"]["vehicle"])
    p_detector = PlateDetector(config["models"]["plate"])
    ocr_engine = LocalPaddleOCR()

    vehicles = v_detector.track(frame)
    print(f"Vehicles Detected: {len(vehicles)}")

    found_plates = 0
    for vehicle in vehicles:
        vx1, vy1, vx2, vy2 = vehicle["box"]
        vehicle_crop = frame[vy1:vy2, vx1:vx2]
        if vehicle_crop.size == 0:
            continue

        plate_boxes = p_detector.detect(vehicle_crop)
        for plate_box in plate_boxes:
            px1, py1, px2, py2 = plate_box
            plate_crop = vehicle_crop[py1:py2, px1:px2]
            if plate_crop.size == 0:
                continue

            found_plates += 1
            raw_text, conf = ocr_engine.read_text(plate_crop)
            is_valid, final_plate, plate_type = IndianPlateValidator.validate(raw_text)
            print(f"\n[Detection #{found_plates}]")
            print(f"Vehicle Type    : {vehicle['class_name'].capitalize()}")
            print(f"Raw OCR Output  : {raw_text}")
            print(f"Validated Plate : {final_plate}")
            print(f"Plate Format    : {plate_type}")
            print(f"Is Valid Match  : {is_valid}")
            print(f"Confidence      : {conf * 100:.2f}%")

    if found_plates == 0:
        direct_boxes = p_detector.detect(frame)
        for box in direct_boxes:
            x1, y1, x2, y2 = box
            plate_crop = frame[y1:y2, x1:x2]
            raw_text, conf = ocr_engine.read_text(plate_crop)
            is_valid, final_plate, plate_type = IndianPlateValidator.validate(raw_text)
            print("\n[Direct Plate Fallback Detection]")
            print(f"Raw OCR Output  : {raw_text}")
            print(f"Validated Plate : {final_plate}")
            print(f"Confidence      : {conf * 100:.2f}%")
            print(f"Plate Format    : {plate_type}")
            print(f"Is Valid Match  : {is_valid}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test ANPR on a single static image file")
    parser.add_argument("--image", type=str, required=True, help="Path to test image")
    args = parser.parse_args()
    test_single_image(args.image)
