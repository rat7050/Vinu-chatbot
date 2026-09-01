import csv
import os

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from camera.camera_manager import CameraWorker
from database.database import DatabaseManager
from gui.camera_widget import CameraDisplayWidget
from gui.detection_table import DetectionTableWidget
from gui.settings_window import SettingsDialog
from ocr.easy_ocr import LocalEasyOCR
from ocr.paddle_ocr import LocalPaddleOCR
from services.anpr_pipeline import ANPRPipeline
from utils.logger import app_logger


class ANPRMainWindow(QMainWindow):
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__()
        self.setWindowTitle("Indian ANPR - Offline Desktop Camera System")
        self.resize(1280, 780)
        self.config_path = config_path

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.db = DatabaseManager(self.config["database"]["path"])
        self.ocr_engine = self._init_ocr()
        self.pipeline = ANPRPipeline(self.config, self.db, self.ocr_engine)
        self.camera_worker = None

        self._init_ui()

    def _init_ocr(self):
        backend = self.config["ocr"].get("backend", "paddleocr").lower()
        if backend == "paddleocr":
            return LocalPaddleOCR()
        if backend == "easyocr":
            return LocalEasyOCR()
        app_logger.warning(f"Unknown OCR backend '{backend}'. Defaulting to PaddleOCR.")
        return LocalPaddleOCR()

    def _init_ui(self):
        self.setStyleSheet(
            """
            QMainWindow { background-color: #181818; }
            QLabel { color: #f0f0f0; font-family: 'Segoe UI'; font-size: 13px; }
            QGroupBox { color: #00e676; font-weight: bold; border: 1px solid #333; margin-top: 6px; padding: 10px; border-radius: 6px; }
            QPushButton {
                background-color: #2979ff; color: white; border: none; border-radius: 4px;
                padding: 8px 16px; font-weight: bold; font-family: 'Segoe UI';
            }
            QPushButton:hover { background-color: #5393ff; }
            QPushButton#stop_btn { background-color: #d50000; }
            QPushButton#stop_btn:hover { background-color: #ff3d00; }
            QLineEdit, QComboBox {
                background-color: #2c2c2c; color: white; border: 1px solid #444;
                padding: 5px; border-radius: 4px;
            }
            """
        )

        central = QWidget()
        main_layout = QVBoxLayout(central)

        top_bar = QHBoxLayout()
        title_label = QLabel("INDIAN ANPR SYSTEM (OFFLINE)")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #00e676;")
        top_bar.addWidget(title_label)
        top_bar.addStretch()

        self.cam_combo = QComboBox()
        self.cam_combo.addItems(["Camera 0", "Camera 1", "Camera 2"])
        top_bar.addWidget(QLabel("Source:"))
        top_bar.addWidget(self.cam_combo)

        self.btn_start = QPushButton("START CAMERA")
        self.btn_start.clicked.connect(self.start_camera)
        top_bar.addWidget(self.btn_start)

        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setObjectName("stop_btn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_camera)
        top_bar.addWidget(self.btn_stop)

        self.btn_open_file = QPushButton("OPEN VIDEO/RTSP")
        self.btn_open_file.clicked.connect(self.open_video_file)
        top_bar.addWidget(self.btn_open_file)

        self.btn_settings = QPushButton("SETTINGS")
        self.btn_settings.clicked.connect(self.open_settings)
        top_bar.addWidget(self.btn_settings)

        main_layout.addLayout(top_bar)

        content_layout = QHBoxLayout()
        left_col = QVBoxLayout()
        self.cam_widget = CameraDisplayWidget()
        left_col.addWidget(self.cam_widget, stretch=5)

        telemetry_box = QGroupBox("SYSTEM TELEMETRY")
        telem_layout = QHBoxLayout(telemetry_box)
        self.lbl_fps = QLabel("FPS: 0.0")
        self.lbl_vehicles = QLabel("Active Vehicles: 0")
        self.lbl_status = QLabel("Engine: Ready (Local)")
        telem_layout.addWidget(self.lbl_fps)
        telem_layout.addWidget(self.lbl_vehicles)
        telem_layout.addWidget(self.lbl_status)
        left_col.addWidget(telemetry_box, stretch=1)

        content_layout.addLayout(left_col, stretch=6)

        right_col = QVBoxLayout()
        search_box = QGroupBox("SEARCH & FILTER")
        search_layout = QHBoxLayout(search_box)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Plate (e.g. MH47)...")
        self.search_input.textChanged.connect(self.filter_detections)
        search_layout.addWidget(self.search_input)

        export_btn = QPushButton("EXPORT CSV")
        export_btn.clicked.connect(self.export_to_csv)
        search_layout.addWidget(export_btn)

        snapshots_btn = QPushButton("OPEN SNAPSHOTS")
        snapshots_btn.clicked.connect(self.open_snapshot_folder)
        search_layout.addWidget(snapshots_btn)

        right_col.addWidget(search_box)
        self.table_widget = DetectionTableWidget()
        right_col.addWidget(self.table_widget)

        content_layout.addLayout(right_col, stretch=4)
        main_layout.addLayout(content_layout)
        self.setCentralWidget(central)

    def start_camera(self, source_override=None):
        if isinstance(source_override, bool):
            source_override = None

        if source_override is None:
            source = self.cam_combo.currentIndex()
        else:
            source = source_override

        self.camera_worker = CameraWorker(source, self.pipeline, camera_id=f"CAM_{source}")
        self.camera_worker.frame_ready.connect(self.on_frame_ready)
        self.camera_worker.detection_occurred.connect(self.on_detection)
        self.camera_worker.error_occurred.connect(self.on_error)
        self.camera_worker.start()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.lbl_status.setText("Status: Live Stream Running")

    def stop_camera(self):
        if self.camera_worker:
            self.camera_worker.stop()
            self.camera_worker = None
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_status.setText("Status: Stopped")
        self.cam_widget.setText("Camera Stopped")

    def open_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Videos (*.mp4 *.avi *.mkv *.mov)",
        )
        if file_path:
            self.stop_camera()
            self.start_camera(source_override=file_path)

    def open_settings(self):
        dialog = SettingsDialog(self.config_path, self)
        dialog.exec()

    def on_frame_ready(self, frame, fps):
        self.cam_widget.update_frame(frame)
        self.lbl_fps.setText(f"FPS: {fps:.1f}")

    def on_detection(self, det_data: dict):
        self.table_widget.add_detection(
            det_data["plate"],
            det_data["type"],
            det_data["conf"],
            det_data["time"],
        )

    def on_error(self, err_msg: str):
        QMessageBox.critical(self, "ANPR Camera Error", err_msg)
        self.stop_camera()

    def filter_detections(self):
        query = self.search_input.text().strip()
        results = self.db.search_detections(plate_query=query)
        self.table_widget.setRowCount(0)
        for row in results:
            self.table_widget.add_detection(
                row["plate_number"],
                row["vehicle_type"] or "Vehicle",
                f"{int(row['confidence'] * 100)}%",
                row["timestamp"].split()[1] if " " in row["timestamp"] else row["timestamp"],
            )

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Detections to CSV",
            "anpr_export.csv",
            "CSV Files (*.csv)",
        )
        if not path:
            return

        results = self.db.search_detections()
        try:
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID",
                    "Timestamp",
                    "Camera",
                    "Track ID",
                    "Plate Number",
                    "Vehicle Type",
                    "Confidence",
                    "Snapshot",
                ])
                for row in results:
                    writer.writerow([
                        row["id"],
                        row["timestamp"],
                        row["camera_id"],
                        row["track_id"],
                        row["plate_number"],
                        row["vehicle_type"],
                        f"{row['confidence']:.2f}",
                        row["image_path"],
                    ])
            QMessageBox.information(self, "Export Successful", f"Exported {len(results)} rows to {path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Failed to save CSV: {exc}")

    def open_snapshot_folder(self):
        snap_dir = os.path.abspath(self.config["snapshots"]["directory"])
        os.makedirs(snap_dir, exist_ok=True)
        try:
            os.startfile(snap_dir)
        except AttributeError:
            QMessageBox.information(self, "Snapshots", f"Snapshot directory: {snap_dir}")

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()
