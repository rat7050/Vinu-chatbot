from dataclasses import dataclass
from typing import Optional


@dataclass
class VehicleRecord:
    track_id: int
    plate_number: str
    vehicle_type: str
    first_seen: str
    last_seen: str
    confidence: float
    camera_id: str
    id: Optional[int] = None


@dataclass
class DetectionRecord:
    vehicle_id: int
    timestamp: str
    plate_number: str
    confidence: float
    image_path: str
    camera_id: str
    id: Optional[int] = None
