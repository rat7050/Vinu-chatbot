import datetime

import cv2
import numpy as np

from database.database import DatabaseManager
from database.models import DetectionRecord, VehicleRecord
from detection.plate_detector import PlateDetector
from detection.vehicle_detector import VehicleDetector
from ocr.validator import IndianPlateValidator
from services.duplicate_filter import DuplicateFilter
from services.result_voting import TemporalVotingManager
from services.snapshot_service import SnapshotService
from utils.logger import app_logger


class ANPRPipeline:
    def __init__(self, config: dict, db_manager: DatabaseManager, ocr_engine):
        self.config = config
        self.db = db_manager
        self.ocr = ocr_engine

        self.vehicle_detector = VehicleDetector(config["models"]["vehicle"])
        self.plate_detector = PlateDetector(config["models"]["plate"])
        self.voting_mgr = TemporalVotingManager(
            required_votes=config["tracking"].get("min_consecutive_votes", 3),
            timeout_seconds=config["tracking"].get("track_timeout_seconds", 8.0),
        )
        self.dup_filter = DuplicateFilter(cooldown_seconds=config.get("plate_cooldown", 8.0))
        self.snapshot_svc = SnapshotService(config["snapshots"]["directory"])

        self.frame_count = 0
        self.ocr_interval = config["ocr"].get("interval", 5)
        self.min_conf = config["ocr"].get("min_confidence", 0.60)

    def process_frame(self, frame: np.ndarray, camera_id: str = "CAM_0"):
        self.frame_count += 1
        annotated_frame = frame.copy()
        new_detections = []

        vehicles = self.vehicle_detector.track(
            frame,
            tracker_type=self.config["tracking"].get("tracker", "bytetrack.yaml"),
        )

        for vehicle in vehicles:
            track_id = vehicle["track_id"]
            vx1, vy1, vx2, vy2 = vehicle["box"]
            vehicle_type = vehicle["class_name"]

            vx1, vy1 = max(0, int(vx1)), max(0, int(vy1))
            vx2, vy2 = min(frame.shape[1], int(vx2)), min(frame.shape[0], int(vy2))
            vehicle_crop = frame[vy1:vy2, vx1:vx2]
            if vehicle_crop.size == 0:
                continue

            if self.frame_count % self.ocr_interval == 0:
                plate_boxes = self.plate_detector.detect(vehicle_crop)
                for plate_box in plate_boxes:
                    px1, py1, px2, py2 = plate_box
                    g_px1, g_py1 = vx1 + px1, vy1 + py1
                    g_px2, g_py2 = vx1 + px2, vy1 + py2

                    plate_crop = vehicle_crop[max(0, py1):min(vehicle_crop.shape[0], py2), max(0, px1):min(vehicle_crop.shape[1], px2)]
                    if plate_crop.size == 0:
                        continue

                    if plate_crop.shape[0] * plate_crop.shape[1] < self.config["ocr"].get("min_plate_area", 1200):
                        continue

                    raw_text, ocr_conf = self.ocr.read_text(plate_crop)
                    is_valid, final_plate, _ = IndianPlateValidator.validate(raw_text)

                    if is_valid and ocr_conf >= self.min_conf:
                        self.voting_mgr.add_observation(track_id, final_plate, ocr_conf)

            confirmed_plate, conf = self.voting_mgr.get_confirmed_plate(track_id)
            label = f"{vehicle_type.upper()} #{track_id}"

            if confirmed_plate:
                label += f" | {confirmed_plate}"
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                vehicle_record = VehicleRecord(
                    track_id=track_id,
                    plate_number=confirmed_plate,
                    vehicle_type=vehicle_type,
                    first_seen=now_str,
                    last_seen=now_str,
                    confidence=conf,
                    camera_id=camera_id,
                )
                vehicle_id = self.db.upsert_vehicle(vehicle_record)

                if self.dup_filter.should_save(confirmed_plate):
                    snapshot_path = self.snapshot_svc.save_snapshot(
                        frame=frame,
                        plate_number=confirmed_plate,
                        confidence=conf,
                        camera_name=camera_id,
                        vehicle_box=(vx1, vy1, vx2, vy2),
                    )
                    detection_record = DetectionRecord(
                        vehicle_id=vehicle_id,
                        timestamp=now_str,
                        plate_number=confirmed_plate,
                        confidence=conf,
                        image_path=snapshot_path,
                        camera_id=camera_id,
                    )
                    self.db.insert_detection(detection_record)
                    new_detections.append({
                        "plate": confirmed_plate,
                        "type": vehicle_type,
                        "conf": f"{int(conf * 100)}%",
                        "time": now_str.split()[1],
                        "snapshot": snapshot_path,
                    })

            color = (0, 255, 0) if confirmed_plate else (255, 180, 0)
            cv2.rectangle(annotated_frame, (vx1, vy1), (vx2, vy2), color, 2)
            cv2.putText(
                annotated_frame,
                label,
                (vx1, max(20, vy1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        return annotated_frame, new_detections
