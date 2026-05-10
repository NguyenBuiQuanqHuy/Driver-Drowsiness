# performance/performance_window.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PerformanceWindow(QWidget):

    def __init__(self):
        super().__init__()

        # =========================================
        # MAIN LAYOUT
        # =========================================
        main_layout = QVBoxLayout()

        # =========================================
        # TITLE
        # =========================================
        #
        # Màn hình đánh giá hiệu suất hệ thống
        # Driver Drowsiness Detection
        #
        # =========================================

        title = QLabel("Performance Evaluation")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)

        # =========================================
        # CLASSIFICATION METRICS
        # =========================================
        #
        # Accuracy:
        #   Độ chính xác tổng thể
        #
        # Precision:
        #   Trong các cảnh báo hệ thống đưa ra,
        #   bao nhiêu cảnh báo là đúng
        #
        # Recall:
        #   Khả năng phát hiện đúng trạng thái buồn ngủ
        #
        # F1-score:
        #   Cân bằng giữa Precision và Recall
        #
        # =========================================

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

        metrics_layout.addWidget(self.card_accuracy, 0, 0)
        metrics_layout.addWidget(self.card_precision, 0, 1)
        metrics_layout.addWidget(self.card_recall, 1, 0)
        metrics_layout.addWidget(self.card_f1, 1, 1)

        # =========================================
        # CONFUSION MATRIX STATS
        # =========================================
        #
        # TP (True Positive):
        #   Detect đúng buồn ngủ
        #
        # FP (False Positive):
        #   Báo động giả
        #
        # FN (False Negative):
        #   Bỏ sót buồn ngủ
        #
        # TN (True Negative):
        #   Detect đúng trạng thái bình thường
        #
        # =========================================

        confusion_layout = QGridLayout()

        self.card_tp = self.create_card(
            "TRUE POSITIVE",
            "0"
        )

        self.card_fp = self.create_card(
            "FALSE POSITIVE",
            "0"
        )

        self.card_fn = self.create_card(
            "FALSE NEGATIVE",
            "0"
        )

        self.card_tn = self.create_card(
            "TRUE NEGATIVE",
            "0"
        )

        confusion_layout.addWidget(self.card_tp, 0, 0)
        confusion_layout.addWidget(self.card_fp, 0, 1)
        confusion_layout.addWidget(self.card_fn, 1, 0)
        confusion_layout.addWidget(self.card_tn, 1, 1)

        # =========================================
        # BUTTONS
        # =========================================
        #
        # Các nút chuyển đổi biểu đồ
        #
        # =========================================

        button_layout = QHBoxLayout()

        self.btn_metrics = QPushButton(
            "Classification Metrics"
        )

        self.btn_confusion = QPushButton(
            "Confusion Matrix"
        )

        button_layout.addWidget(self.btn_metrics)
        button_layout.addWidget(self.btn_confusion)

        # =========================================
        # CHART AREA
        # =========================================
        #
        # Khu vực hiển thị biểu đồ đánh giá
        #
        # =========================================

        chart_group = QGroupBox("Performance Chart")

        chart_layout = QVBoxLayout()

        self.figure = Figure(facecolor="#1c2541")

        self.canvas = FigureCanvas(self.figure)

        chart_layout.addWidget(self.canvas)

        chart_group.setLayout(chart_layout)

        # =========================================
        # ADD TO MAIN LAYOUT
        # =========================================

        main_layout.addWidget(title)

        main_layout.addLayout(metrics_layout)

        main_layout.addLayout(confusion_layout)

        main_layout.addLayout(button_layout)

        main_layout.addWidget(chart_group)

        self.setLayout(main_layout)

        # =========================================
        # BUTTON EVENTS
        # =========================================

        self.btn_metrics.clicked.connect(
            self.draw_metrics_chart
        )

        self.btn_confusion.clicked.connect(
            self.draw_confusion_chart
        )

    # =============================================
    # CREATE CARD
    # =============================================
    #
    # Tạo card hiển thị metric
    #
    # =============================================

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

        # =========================
        # TITLE
        # =========================

        lbl_title = QLabel(title)

        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_title.setStyleSheet("""
            font-size: 14px;
            color: #bbbbbb;
        """)

        # =========================
        # VALUE
        # =========================

        lbl_value = QLabel(value)

        lbl_value.setAlignment(Qt.AlignCenter)

        lbl_value.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
        """)

        # lưu label value
        frame.value_label = lbl_value

        layout.addWidget(lbl_title)

        layout.addWidget(lbl_value)

        frame.setLayout(layout)

        return frame

    # =============================================
    # LOAD DATA
    # =============================================
    #
    # Giả lập dữ liệu đánh giá classification
    #
    # =============================================

    def load_data(self):

        # =========================================
        # CONFUSION MATRIX VALUES
        # =========================================
        #
        # TP:
        #   detect đúng buồn ngủ
        #
        # FP:
        #   báo động giả
        #
        # FN:
        #   bỏ sót buồn ngủ
        #
        # TN:
        #   detect đúng bình thường
        #
        # =========================================

        TP = 94
        FP = 7
        FN = 5
        TN = 88

        # =========================================
        # CLASSIFICATION METRICS
        # =========================================

        accuracy = (
            (TP + TN) /
            (TP + TN + FP + FN)
        ) * 100

        precision = (
            TP /
            (TP + FP)
        ) * 100

        recall = (
            TP /
            (TP + FN)
        ) * 100

        f1_score = (
            2 * precision * recall
        ) / (
            precision + recall
        )

        # =========================================
        # UPDATE UI
        # =========================================

        self.card_accuracy.value_label.setText(
            f"{accuracy:.2f}%"
        )

        self.card_precision.value_label.setText(
            f"{precision:.2f}%"
        )

        self.card_recall.value_label.setText(
            f"{recall:.2f}%"
        )

        self.card_f1.value_label.setText(
            f"{f1_score:.2f}%"
        )

        self.card_tp.value_label.setText(str(TP))

        self.card_fp.value_label.setText(str(FP))

        self.card_fn.value_label.setText(str(FN))

        self.card_tn.value_label.setText(str(TN))

        # =========================================
        # DEFAULT CHART
        # =========================================

        self.draw_metrics_chart()

    # =============================================
    # DRAW METRICS LINE CHART
    # =============================================
    #
    # Biểu đồ đường đánh giá:
    #
    # - Accuracy
    # - Precision
    # - Recall
    # - F1-score
    #
    # Đây là các metric quan trọng
    # trong bài toán classification
    #
    # =============================================

    def draw_metrics_chart(self):

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        metrics = [
            "Accuracy",
            "Precision",
            "Recall",
            "F1-score"
        ]

        values = [
            float(
                self.card_accuracy.value_label.text().replace("%", "")
            ),
            float(
                self.card_precision.value_label.text().replace("%", "")
            ),
            float(
                self.card_recall.value_label.text().replace("%", "")
            ),
            float(
                self.card_f1.value_label.text().replace("%", "")
            )
        ]

        # =========================================
        # LINE CHART
        # =========================================

        ax.plot(
            metrics,
            values,
            marker='o',
            linewidth=3
        )

        # =========================================
        # TITLE
        # =========================================

        ax.set_title(
            "Classification Performance Metrics",
            color="white",
            fontsize=15,
            fontweight='bold'
        )

        ax.set_ylabel(
            "Score (%)",
            color="white"
        )

        # =========================================
        # DARK THEME
        # =========================================

        ax.set_facecolor("#1c2541")

        self.figure.patch.set_facecolor("#1c2541")

        ax.tick_params(axis='x', colors='white')

        ax.tick_params(axis='y', colors='white')

        for spine in ax.spines.values():
            spine.set_color("white")

        ax.grid(
            True,
            linestyle='--',
            alpha=0.3
        )

        # =========================================
        # SHOW VALUE
        # =========================================

        for i, v in enumerate(values):

            ax.text(
                i,
                v + 0.5,
                f"{v:.1f}",
                color='white',
                ha='center'
            )

        self.figure.tight_layout()

        self.canvas.draw()

    # =============================================
    # DRAW CONFUSION MATRIX CHART
    # =============================================
    #
    # Biểu đồ đường confusion matrix
    #
    # TP:
    #   detect đúng buồn ngủ
    #
    # FP:
    #   báo động giả
    #
    # FN:
    #   bỏ sót buồn ngủ
    #
    # TN:
    #   detect đúng bình thường
    #
    # =============================================

    def draw_confusion_chart(self):

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        labels = [
            "TP",
            "FP",
            "FN",
            "TN"
        ]

        values = [
            int(self.card_tp.value_label.text()),
            int(self.card_fp.value_label.text()),
            int(self.card_fn.value_label.text()),
            int(self.card_tn.value_label.text())
        ]

        # =========================================
        # LINE CHART
        # =========================================

        ax.plot(
            labels,
            values,
            marker='o',
            linewidth=3
        )

        # =========================================
        # TITLE
        # =========================================

        ax.set_title(
            "Confusion Matrix Statistics",
            color='white',
            fontsize=15,
            fontweight='bold'
        )

        ax.set_ylabel(
            "Count",
            color='white'
        )

        # =========================================
        # DARK THEME
        # =========================================

        ax.set_facecolor("#1c2541")

        self.figure.patch.set_facecolor("#1c2541")

        ax.tick_params(axis='x', colors='white')

        ax.tick_params(axis='y', colors='white')

        for spine in ax.spines.values():
            spine.set_color("white")

        ax.grid(
            True,
            linestyle='--',
            alpha=0.3
        )

        # =========================================
        # SHOW VALUE
        # =========================================

        for i, v in enumerate(values):

            ax.text(
                i,
                v + 1,
                str(v),
                color='white',
                ha='center'
            )

        self.figure.tight_layout()

        self.canvas.draw()