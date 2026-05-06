from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from datetime import datetime, timedelta

from .history_manager import load_history, clear_history


class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Alert History")

        # ===== FILTER TYPE =====
        self.filter_type = QComboBox()
        self.filter_type.addItems([
            "ALL",
            "MICROSLEEP",
            "EYES CLOSED",
            "YAWN"
        ])
        self.filter_type.currentTextChanged.connect(self.apply_filter)

        # ===== FILTER TIME =====
        self.filter_time = QComboBox()
        self.filter_time.addItems([
            "ALL",
            "TODAY",
            "LAST 7 DAYS"
        ])
        self.filter_time.currentTextChanged.connect(self.apply_filter)

        # ===== CLEAR BUTTON =====
        self.btn_clear = QPushButton("🧹 Clear History")
        self.btn_clear.clicked.connect(self.clear_all)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Time", "Alert", "EAR", "MAR", "HEAD"
        ])

        # config table
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)

        # set column width
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)

        # ===== STYLE =====
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1c2541;
                color: white;
                gridline-color: #5bc0be;
                font-size: 14px;
            }

            QHeaderView::section {
                background-color: #0b132b;
                color: #5bc0be;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #5bc0be;
            }

            /* ===== BUTTON ===== */
            QPushButton {
                padding: 8px;
                border-radius: 8px;
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border: 2px solid #c0392b;
            }

            QPushButton:hover {
                background-color: #c0392b;
            }

            /* ===== DROPDOWN GIỐNG BUTTON ===== */
            QComboBox {
                background-color: #e74c3c;
                color: white;
                border: 2px solid #c0392b;
                border-radius: 8px;
                padding: 6px 10px;
                min-width: 140px;
                font-weight: bold;
            }

            QComboBox:hover {
                background-color: #c0392b;
            }

            QComboBox::drop-down {
                border: none;
            }

            /* list xổ xuống */
            QComboBox QAbstractItemView {
                background-color: #1c2541;
                color: white;
                selection-background-color: #5bc0be;
                selection-color: black;
                border: 2px solid #5bc0be;
                font-weight: bold;
            }
        """)

        # ===== TOP BAR =====
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.filter_type)
        top_layout.addWidget(self.filter_time)
        top_layout.addWidget(self.btn_clear)

        # ===== MAIN LAYOUT =====
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    # ===== LOAD DATA =====
    def load_data(self):
        self.full_data = load_history()  # lưu toàn bộ data
        self.display_data(self.full_data)

    # ===== HIỂN THỊ TABLE =====
    def display_data(self, data):
        font_bold = QFont()
        font_bold.setBold(True)

        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            # set dữ liệu
            self.table.setItem(row, 0, QTableWidgetItem(item.get("time", "")))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("type", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get("ear", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get("mar", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.get("head", ""))))

            # căn giữa
            for col in range(5):
                cell = self.table.item(row, col)
                cell.setTextAlignment(Qt.AlignCenter)

            # ===== highlight theo loại =====
            alert_type = item.get("type", "")

            if alert_type == "MICROSLEEP":
                color = "#e74c3c"
                text_color = "white"
            elif alert_type == "EYES CLOSED":
                color = "#e67e22"
                text_color = "white"
            elif alert_type == "YAWN":
                color = "#f1c40f"
                text_color = "black"
            else:
                continue

            for col in range(5):
                cell = self.table.item(row, col)
                cell.setBackground(QColor(color))
                cell.setForeground(QColor(text_color))
                cell.setFont(font_bold)

    # ===== FILTER CHÍNH =====
    def apply_filter(self):
        selected_type = self.filter_type.currentText()
        selected_time = self.filter_time.currentText()

        filtered = []
        now = datetime.now()

        for item in self.full_data:
            item_type = item.get("type", "")
            item_time_str = item.get("time", "")

            # ===== FILTER TYPE =====
            if selected_type != "ALL" and item_type != selected_type:
                continue

            # ===== FILTER TIME =====
            if selected_time != "ALL":
                try:
                    item_time = datetime.strptime(item_time_str, "%Y-%m-%d %H:%M:%S")
                except:
                    continue

                if selected_time == "TODAY":
                    if item_time.date() != now.date():
                        continue

                elif selected_time == "LAST 7 DAYS":
                    if item_time < now - timedelta(days=7):
                        continue

            filtered.append(item)

        self.display_data(filtered)

    # ===== CLEAR HISTORY =====
    def clear_all(self):
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Delete all history?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            clear_history()
            self.load_data()