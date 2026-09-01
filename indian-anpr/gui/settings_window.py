from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)
import yaml


class SettingsDialog(QDialog):
    def __init__(self, config_path: str = "config.yaml", parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.setWindowTitle("ANPR System Settings")
        self.setMinimumWidth(400)
        self.setStyleSheet("background-color: #222; color: #fff;")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.ocr_backend = QComboBox()
        self.ocr_backend.addItems(["paddleocr", "easyocr"])
        self.ocr_backend.setCurrentText(self.config["ocr"].get("backend", "paddleocr"))
        form.addRow("OCR Backend:", self.ocr_backend)

        self.min_conf = QDoubleSpinBox()
        self.min_conf.setRange(0.1, 1.0)
        self.min_conf.setSingleStep(0.05)
        self.min_conf.setValue(self.config["ocr"].get("min_confidence", 0.60))
        form.addRow("Min OCR Confidence:", self.min_conf)

        self.ocr_interval = QSpinBox()
        self.ocr_interval.setRange(1, 30)
        self.ocr_interval.setValue(self.config["ocr"].get("interval", 5))
        form.addRow("OCR Frame Interval:", self.ocr_interval)

        self.plate_model = QLineEdit(self.config["models"].get("plate", "models/indian_plate.pt"))
        form.addRow("Plate Model Path:", self.plate_model)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def save_settings(self):
        self.config["ocr"]["backend"] = self.ocr_backend.currentText()
        self.config["ocr"]["min_confidence"] = float(self.min_conf.value())
        self.config["ocr"]["interval"] = int(self.ocr_interval.value())
        self.config["models"]["plate"] = self.plate_model.text()

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False)

        QMessageBox.information(
            self,
            "Settings Saved",
            "Configuration saved. Restart or restart camera to apply changes.",
        )
        self.accept()
