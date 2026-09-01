import os
import sqlite3
from typing import List, Optional

from database.models import DetectionRecord, VehicleRecord
from utils.logger import app_logger


class DatabaseManager:
    def __init__(self, db_path: str = "data/anpr.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cameras (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_id INTEGER NOT NULL,
                    plate_number TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    confidence REAL NOT NULL,
                    camera_id TEXT NOT NULL,
                    UNIQUE(track_id, camera_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER,
                    timestamp TIMESTAMP NOT NULL,
                    plate_number TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    image_path TEXT NOT NULL,
                    camera_id TEXT NOT NULL,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
                )
                """
            )

            conn.commit()
            app_logger.info(f"Database initialized at {self.db_path}")

    def upsert_vehicle(self, record: VehicleRecord) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, plate_number, confidence FROM vehicles
                WHERE track_id = ? AND camera_id = ?
                """,
                (record.track_id, record.camera_id),
            )
            row = cursor.fetchone()

            if row:
                v_id = row["id"]
                if record.confidence >= row["confidence"]:
                    cursor.execute(
                        """
                        UPDATE vehicles
                        SET plate_number = ?, vehicle_type = ?, last_seen = ?, confidence = ?
                        WHERE id = ?
                        """,
                        (
                            record.plate_number,
                            record.vehicle_type,
                            record.last_seen,
                            record.confidence,
                            v_id,
                        ),
                    )
                else:
                    cursor.execute(
                        "UPDATE vehicles SET last_seen = ? WHERE id = ?",
                        (record.last_seen, v_id),
                    )
                conn.commit()
                return v_id

            cursor.execute(
                """
                INSERT INTO vehicles (track_id, plate_number, vehicle_type, first_seen, last_seen, confidence, camera_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.track_id,
                    record.plate_number,
                    record.vehicle_type,
                    record.first_seen,
                    record.last_seen,
                    record.confidence,
                    record.camera_id,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def insert_detection(self, record: DetectionRecord) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO detections (vehicle_id, timestamp, plate_number, confidence, image_path, camera_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.vehicle_id,
                    record.timestamp,
                    record.plate_number,
                    record.confidence,
                    record.image_path,
                    record.camera_id,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def search_detections(
        self,
        plate_query: Optional[str] = None,
        date_query: Optional[str] = None,
        vehicle_type: Optional[str] = None,
    ) -> List[sqlite3.Row]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT d.id, d.timestamp, d.plate_number, d.confidence, d.image_path, d.camera_id,
                       v.track_id, v.vehicle_type
                FROM detections d
                LEFT JOIN vehicles v ON d.vehicle_id = v.id
                WHERE 1=1
            """
            params = []

            if plate_query:
                query += " AND d.plate_number LIKE ?"
                params.append(f"%{plate_query.strip().upper()}%")
            if date_query:
                query += " AND d.timestamp LIKE ?"
                params.append(f"{date_query.strip()}%")
            if vehicle_type and vehicle_type.lower() != "all":
                query += " AND v.vehicle_type = ?"
                params.append(vehicle_type.lower())

            query += " ORDER BY d.id DESC LIMIT 200"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
