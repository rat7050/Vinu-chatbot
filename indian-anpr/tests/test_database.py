import os

from database.database import DatabaseManager
from database.models import DetectionRecord, VehicleRecord


def test_database_crud(tmp_path):
    db_file = os.path.join(tmp_path, "test_anpr.db")
    db = DatabaseManager(db_file)

    vehicle = VehicleRecord(
        track_id=1,
        plate_number="MH47BP8265",
        vehicle_type="car",
        first_seen="2026-09-01 12:00:00",
        last_seen="2026-09-01 12:00:00",
        confidence=0.95,
        camera_id="CAM_0",
    )
    vehicle_id = db.upsert_vehicle(vehicle)
    assert vehicle_id == 1

    detection = DetectionRecord(
        vehicle_id=vehicle_id,
        timestamp="2026-09-01 12:00:00",
        plate_number="MH47BP8265",
        confidence=0.95,
        image_path="data/snapshots/dummy.jpg",
        camera_id="CAM_0",
    )
    detection_id = db.insert_detection(detection)
    assert detection_id == 1

    results = db.search_detections(plate_query="MH47")
    assert len(results) == 1
    assert results[0]["plate_number"] == "MH47BP8265"
