from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem


class DetectionTableWidget(QTableWidget):
    def __init__(self):
        super().__init__(0, 4)
        self.setHorizontalHeaderLabels(["Plate Number", "Vehicle Type", "Confidence", "Time"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setStyleSheet(
            """
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                gridline-color: #333333;
                border: 1px solid #333333;
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #00e676;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #333333;
            }
            """
        )
        self.verticalHeader().setVisible(False)

    def add_detection(self, plate: str, v_type: str, conf: str, time_str: str):
        row_pos = self.rowCount()
        self.insertRow(row_pos)
        self.setItem(row_pos, 0, QTableWidgetItem(plate))
        self.setItem(row_pos, 1, QTableWidgetItem(v_type.capitalize()))
        self.setItem(row_pos, 2, QTableWidgetItem(conf))
        self.setItem(row_pos, 3, QTableWidgetItem(time_str))

        if self.rowCount() > 150:
            self.removeRow(150)
