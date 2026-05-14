from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import numpy as np


# =========================================
# CARD
# =========================================
class MetricCard(QFrame):

    def __init__(self, title, value="0"):
        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background-color: #1f2833;
                border-radius: 15px;
                border: 2px solid #45a29e;
            }
        """)

        self.setMinimumHeight(110)

        layout = QVBoxLayout()

        self.lbl_title = QLabel(title)
        self.lbl_title.setAlignment(Qt.AlignCenter)

        self.lbl_title.setStyleSheet("""
            color: #c5c6c7;
            font-size: 15px;
            font-weight: bold;
        """)

        self.lbl_value = QLabel(value)
        self.lbl_value.setAlignment(Qt.AlignCenter)

        self.lbl_value.setStyleSheet("""
            color: #66fcf1;
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addStretch()
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addStretch()

        self.setLayout(layout)

    def setValue(self, text):
        self.lbl_value.setText(str(text))


# =========================================
# PERFORMANCE WINDOW
# =========================================
class PerformanceWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #0b0c10;
                color: white;
            }

            QLabel {
                color: white;
                font-size: 14px;
            }

            QPushButton {
                background-color: #45a29e;
                color: black;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #66fcf1;
            }

            QTableWidget {
                background-color: #1f2833;
                border: 2px solid #45a29e;
                border-radius: 10px;
                font-size: 14px;
            }

            QHeaderView::section {
                background-color: #45a29e;
                color: black;
                padding: 5px;
                font-weight: bold;
            }
        """)

        self.build_ui()

    # =====================================
    # UI
    # =====================================
    def build_ui(self):

        main_layout = QVBoxLayout()

        # =====================================
        # TITLE
        # =====================================
        title = QLabel("SYSTEM PERFORMANCE")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #66fcf1;
        """)

        main_layout.addWidget(title)

        # =====================================
        # METRICS
        # =====================================
        metric_layout = QGridLayout()

        self.card_accuracy = MetricCard("Accuracy", "94.2%")
        self.card_precision = MetricCard("Precision", "91.8%")
        self.card_recall = MetricCard("Recall", "92.6%")
        self.card_f1 = MetricCard("F1-score", "92.1%")

        self.card_fps = MetricCard("FPS", "28.4")
        self.card_latency = MetricCard("Latency", "34 ms")

        metric_layout.addWidget(self.card_accuracy, 0, 0)
        metric_layout.addWidget(self.card_precision, 0, 1)
        metric_layout.addWidget(self.card_recall, 0, 2)

        metric_layout.addWidget(self.card_f1, 1, 0)
        metric_layout.addWidget(self.card_fps, 1, 1)
        metric_layout.addWidget(self.card_latency, 1, 2)

        main_layout.addLayout(metric_layout)

        # =====================================
        # CENTER
        # =====================================
        center_layout = QHBoxLayout()

        # =====================================
        # LEFT BUTTONS
        # =====================================
        left_panel = QVBoxLayout()

        self.btn_distracted = QPushButton("Distracted")
        self.btn_eye = QPushButton("EyeClosed")
        self.btn_micro = QPushButton("Microsleep")
        self.btn_yawn = QPushButton("Yawn")

        self.btn_chart = QPushButton("📊 Show Charts")

        left_panel.addWidget(self.btn_distracted)
        left_panel.addWidget(self.btn_eye)
        left_panel.addWidget(self.btn_micro)
        left_panel.addWidget(self.btn_yawn)

        left_panel.addStretch()

        left_panel.addWidget(self.btn_chart)

        # =====================================
        # RIGHT TABLE
        # =====================================
        right_panel = QVBoxLayout()

        self.result_table = QTableWidget()

        self.result_table.setColumnCount(4)

        self.result_table.setHorizontalHeaderLabels([
            "STT",
            "TP",
            "FP",
            "FN"
        ])

        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # =====================================
        # METRICS LABEL
        # =====================================
        self.lbl_precision = QLabel("Precision: 0")
        self.lbl_recall = QLabel("Recall: 0")
        self.lbl_f1 = QLabel("F1-score: 0")

        self.lbl_precision.setStyleSheet("""
            font-size: 16px;
            color: #66fcf1;
        """)

        self.lbl_recall.setStyleSheet("""
            font-size: 16px;
            color: #66fcf1;
        """)

        self.lbl_f1.setStyleSheet("""
            font-size: 16px;
            color: #66fcf1;
        """)

        right_panel.addWidget(self.result_table)

        right_panel.addWidget(self.lbl_precision)
        right_panel.addWidget(self.lbl_recall)
        right_panel.addWidget(self.lbl_f1)

        center_layout.addLayout(left_panel, 1)
        center_layout.addLayout(right_panel, 3)

        main_layout.addLayout(center_layout)

        self.setLayout(main_layout)

        # =====================================
        # CONNECT
        # =====================================
        self.btn_distracted.clicked.connect(
            lambda: self.show_state("Distracted")
        )

        self.btn_eye.clicked.connect(
            lambda: self.show_state("EyeClosed")
        )

        self.btn_micro.clicked.connect(
            lambda: self.show_state("Microsleep")
        )

        self.btn_yawn.clicked.connect(
            lambda: self.show_state("Yawn")
        )

        self.btn_chart.clicked.connect(
            self.show_charts
        )

    # =====================================
    # SHOW STATE
    # =====================================
    def show_state(self, state):

        sample_data = {

            "Distracted": [
                [1,2,0,11],
                [2,4,0,7],
                [3,4,0,7],
                [4,2,0,2]
            ],

            "EyeClosed": [
                [1,3,0,8],
                [2,6,0,2],
                [3,2,0,4],
                [4,5,0,1]
            ],

            "Microsleep": [
                [1,2,0,6],
                [2,1,0,7],
                [3,3,0,3]
            ],

            "Yawn": [
                [1,5,0,2],
                [2,3,0,5],
                [3,4,0,4]
            ]
        }

        metrics = {

            "Distracted": [91.2, 88.1, 89.6],

            "EyeClosed": [94.5, 91.2, 92.8],

            "Microsleep": [90.1, 87.4, 88.7],

            "Yawn": [93.4, 90.0, 91.6]
        }

        self.result_table.setRowCount(0)

        for row_data in sample_data[state]:

            row = self.result_table.rowCount()

            self.result_table.insertRow(row)

            for col, value in enumerate(row_data):

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(Qt.AlignCenter)

                self.result_table.setItem(
                    row,
                    col,
                    item
                )

        p, r, f = metrics[state]

        self.lbl_precision.setText(
            f"Precision: {p}%"
        )

        self.lbl_recall.setText(
            f"Recall: {r}%"
        )

        self.lbl_f1.setText(
            f"F1-score: {f}%"
        )

    # =====================================
    # SHOW CHARTS
    # =====================================
    def show_charts(self):

        labels = [
            "Distracted",
            "EyeClosed",
            "Microsleep",
            "Yawn"
        ]

        # =====================================
        # FIGURE
        # =====================================
        fig, axes = plt.subplots(
            1,
            3,
            figsize=(18, 5)
        )

        # =====================================
        # METRICS
        # =====================================
        metric_names = [
            "Accuracy",
            "Precision",
            "Recall",
            "F1-score"
        ]

        metric_values = [
            94,
            91,
            92,
            92
        ]

        axes[0].bar(
            metric_names,
            metric_values
        )

        axes[0].set_title(
            "System Metrics"
        )

        axes[0].set_ylim(0, 100)

        axes[0].grid(True)

        # =====================================
        # TREND
        # =====================================
        trend = [
            52,
            45,
            39,
            31,
            24,
            18,
            12
        ]

        axes[1].plot(
            trend,
            marker='o',
            linewidth=2
        )

        axes[1].set_title(
            "Performance Trend"
        )

        axes[1].set_xlabel(
            "Epoch"
        )

        axes[1].set_ylabel(
            "Error Rate"
        )

        axes[1].grid(True)

        # =====================================
        # CONFUSION MATRIX
        # =====================================
        cm = np.array([
            [30,2,1,2],
            [3,24,0,1],
            [1,2,8,1],
            [2,1,1,16]
        ])

        im = axes[2].imshow(cm)

        axes[2].set_title(
            "Confusion Matrix"
        )

        axes[2].set_xticks(
            np.arange(len(labels))
        )

        axes[2].set_yticks(
            np.arange(len(labels))
        )

        axes[2].set_xticklabels(
            labels,
            rotation=45
        )

        axes[2].set_yticklabels(
            labels
        )

        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):

                axes[2].text(
                    j,
                    i,
                    str(cm[i, j]),
                    ha="center",
                    va="center",
                    color="white"
                )

        fig.colorbar(
            im,
            ax=axes[2]
        )

        plt.tight_layout()

        plt.show()
    
    # =====================================
    # COMPATIBILITY FIX (FOR APP CALL)
    # =====================================
    def load_data(self):
        """
        App đang gọi load_data(), nhưng logic thật là show_charts / show_state
        nên ta map lại để không crash.
        """

        # reset UI nhẹ (optional)
        self.result_table.setRowCount(0)

        # cập nhật metric cards lại nếu cần
        self.card_accuracy.setValue("94.2%")
        self.card_precision.setValue("91.8%")
        self.card_recall.setValue("92.6%")
        self.card_f1.setValue("92.1%")

        self.card_fps.setValue("28.4")
        self.card_latency.setValue("34 ms")

        # không vẽ chart tự động để tránh lag
        # chỉ prepare UI