# performance/performance_window.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

from .evaluator import PerformanceEvaluator
from .metrics import MetricsCalculator


class PerformanceWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.labels = [
            "AWAKE",
            "YAWN",
            "EYES CLOSED",
            "MICROSLEEP",
            "DISTRACTED"
        ]

        self.metrics_data = None

        self.init_ui()

    # ==================================================
    # UI
    # ==================================================

    def init_ui(self):

        main_layout = QVBoxLayout()

        # ==================================================
        # TITLE
        # ==================================================

        title = QLabel("System Performance Evaluation")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)

        # ==================================================
        # OVERALL METRICS
        # ==================================================

        metrics_layout = QGridLayout()

        self.card_accuracy = self.create_card(
            "ACCURACY",
            "0%"
        )

        self.card_precision = self.create_card(
            "PRECISION",
            "0%"
        )

        self.card_recall = self.create_card(
            "RECALL",
            "0%"
        )

        self.card_f1 = self.create_card(
            "F1-SCORE",
            "0%"
        )

        self.card_fps = self.create_card(
            "AVG FPS",
            "0"
        )

        self.card_latency = self.create_card(
            "AVG LATENCY",
            "0 ms"
        )

        metrics_layout.addWidget(self.card_accuracy, 0, 0)
        metrics_layout.addWidget(self.card_precision, 0, 1)
        metrics_layout.addWidget(self.card_recall, 0, 2)

        metrics_layout.addWidget(self.card_f1, 1, 0)
        metrics_layout.addWidget(self.card_fps, 1, 1)
        metrics_layout.addWidget(self.card_latency, 1, 2)

        # ==================================================
        # TABLE
        # ==================================================

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "STATE",
            "PRECISION",
            "RECALL",
            "F1-SCORE",
            "SUPPORT"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setStyleSheet("""
            QTableWidget{
                background-color: #1c2541;
                color: white;
                gridline-color: #3a506b;
                font-size: 13px;
            }

            QHeaderView::section{
                background-color: #3a506b;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)

        # ==================================================
        # BUTTONS
        # ==================================================

        button_layout = QHBoxLayout()

        self.btn_run = QPushButton("Run Evaluation")

        self.btn_confusion = QPushButton(
            "Confusion Matrix"
        )

        self.btn_metrics = QPushButton(
            "Metrics Chart"
        )

        self.btn_fps = QPushButton(
            "FPS Chart"
        )

        button_layout.addWidget(self.btn_run)
        button_layout.addWidget(self.btn_confusion)
        button_layout.addWidget(self.btn_metrics)
        button_layout.addWidget(self.btn_fps)

        # ==================================================
        # CHART AREA
        # ==================================================

        chart_group = QGroupBox("Performance Charts")

        chart_layout = QVBoxLayout()

        self.figure = Figure(facecolor="#1c2541")

        self.canvas = FigureCanvas(self.figure)

        chart_layout.addWidget(self.canvas)

        chart_group.setLayout(chart_layout)

        # ==================================================
        # ADD TO MAIN LAYOUT
        # ==================================================

        main_layout.addWidget(title)

        main_layout.addLayout(metrics_layout)

        main_layout.addWidget(self.table)

        main_layout.addLayout(button_layout)

        main_layout.addWidget(chart_group)

        self.setLayout(main_layout)

        # ==================================================
        # EVENTS
        # ==================================================

        self.btn_run.clicked.connect(
            self.run_evaluation
        )

        self.btn_confusion.clicked.connect(
            self.draw_confusion_matrix
        )

        self.btn_metrics.clicked.connect(
            self.draw_metrics_chart
        )

        self.btn_fps.clicked.connect(
            self.draw_fps_chart
        )

    # ==================================================
    # CREATE CARD
    # ==================================================

    def create_card(self, title, value):

        frame = QFrame()

        frame.setFixedHeight(90)

        frame.setStyleSheet("""
            QFrame{
                background-color: #1c2541;
                border-radius: 12px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout()

        lbl_title = QLabel(title)

        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_title.setStyleSheet("""
            font-size: 14px;
            color: #bbbbbb;
        """)

        lbl_value = QLabel(value)

        lbl_value.setAlignment(Qt.AlignCenter)

        lbl_value.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
        """)

        frame.value_label = lbl_value

        layout.addWidget(lbl_title)

        layout.addWidget(lbl_value)

        frame.setLayout(layout)

        return frame

    # ==================================================
    # RUN EVALUATION
    # ==================================================

    def run_evaluation(self):

        evaluator = PerformanceEvaluator()

        results = evaluator.evaluate_dataset("Test")

        calculator = MetricsCalculator(
            self.labels
        )

        self.metrics_data = calculator.calculate(results)

        report = self.metrics_data[
            "classification_report"
        ]

        # ==================================================
        # UPDATE OVERALL METRICS
        # ==================================================

        self.card_accuracy.value_label.setText(
            f"{self.metrics_data['accuracy'] * 100:.2f}%"
        )

        self.card_precision.value_label.setText(
            f"{self.metrics_data['precision'] * 100:.2f}%"
        )

        self.card_recall.value_label.setText(
            f"{self.metrics_data['recall'] * 100:.2f}%"
        )

        self.card_f1.value_label.setText(
            f"{self.metrics_data['f1'] * 100:.2f}%"
        )

        avg_fps = np.mean([
            r["avg_fps"]
            for r in results
        ])

        avg_latency = np.mean([
            r["avg_process_time"]
            for r in results
        ])

        self.card_fps.value_label.setText(
            f"{avg_fps:.2f}"
        )

        self.card_latency.value_label.setText(
            f"{avg_latency:.2f} ms"
        )

        # ==================================================
        # UPDATE TABLE
        # ==================================================

        self.table.setRowCount(
            len(self.labels)
        )

        for row, label in enumerate(self.labels):

            data = report[label]

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(label)
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{data['precision'] * 100:.2f}%"
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    f"{data['recall'] * 100:.2f}%"
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    f"{data['f1-score'] * 100:.2f}%"
                )
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(data['support'])
                )
            )

        self.results = results

        self.draw_confusion_matrix()

    # ==================================================
    # DRAW CONFUSION MATRIX
    # ==================================================

    def draw_confusion_matrix(self):

        if self.metrics_data is None:
            return

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        cm = self.metrics_data[
            "confusion_matrix"
        ]

        im = ax.imshow(cm)

        ax.set_xticks(
            range(len(self.labels))
        )

        ax.set_yticks(
            range(len(self.labels))
        )

        ax.set_xticklabels(
            self.labels,
            rotation=15
        )

        ax.set_yticklabels(
            self.labels
        )

        for i in range(len(self.labels)):
            for j in range(len(self.labels)):

                ax.text(
                    j,
                    i,
                    str(cm[i, j]),
                    ha="center",
                    va="center",
                    color="white"
                )

        ax.set_title(
            "Confusion Matrix",
            color="white"
        )

        ax.set_facecolor("#1c2541")

        self.figure.patch.set_facecolor(
            "#1c2541"
        )

        ax.tick_params(colors='white')

        self.figure.tight_layout()

        self.canvas.draw()

    # ==================================================
    # DRAW METRICS CHART
    # ==================================================

    def draw_metrics_chart(self):

        if self.metrics_data is None:
            return

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        report = self.metrics_data[
            "classification_report"
        ]

        precision = []
        recall = []
        f1 = []

        for label in self.labels:

            precision.append(
                report[label]['precision'] * 100
            )

            recall.append(
                report[label]['recall'] * 100
            )

            f1.append(
                report[label]['f1-score'] * 100
            )

        x = np.arange(len(self.labels))

        ax.plot(
            x,
            precision,
            marker='o',
            linewidth=3
        )

        ax.plot(
            x,
            recall,
            marker='o',
            linewidth=3
        )

        ax.plot(
            x,
            f1,
            marker='o',
            linewidth=3
        )

        ax.set_xticks(x)

        ax.set_xticklabels(
            self.labels
        )

        ax.legend([
            "Precision",
            "Recall",
            "F1-score"
        ])

        ax.set_ylabel(
            "Score (%)",
            color="white"
        )

        ax.set_title(
            "Per-Class Performance",
            color="white"
        )

        ax.set_facecolor("#1c2541")

        self.figure.patch.set_facecolor(
            "#1c2541"
        )

        ax.tick_params(colors='white')

        for spine in ax.spines.values():
            spine.set_color("white")

        ax.grid(
            True,
            linestyle='--',
            alpha=0.3
        )

        self.figure.tight_layout()

        self.canvas.draw()

    # ==================================================
    # DRAW FPS CHART
    # ==================================================

    def draw_fps_chart(self):

        if not hasattr(self, "results"):
            return

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        videos = [
            r["video"]
            for r in self.results
        ]

        fps_values = [
            r["avg_fps"]
            for r in self.results
        ]

        ax.plot(
            range(len(videos)),
            fps_values,
            marker='o',
            linewidth=3
        )

        ax.set_title(
            "FPS Performance",
            color="white"
        )

        ax.set_ylabel(
            "FPS",
            color="white"
        )

        ax.set_xlabel(
            "Videos",
            color="white"
        )

        ax.set_facecolor("#1c2541")

        self.figure.patch.set_facecolor(
            "#1c2541"
        )

        ax.tick_params(colors='white')

        for spine in ax.spines.values():
            spine.set_color("white")

        ax.grid(
            True,
            linestyle='--',
            alpha=0.3
        )

        self.figure.tight_layout()

        self.canvas.draw()