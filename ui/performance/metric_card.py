from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

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

        layout = QVBoxLayout()

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)

        self.value = QLabel(value)
        self.value.setAlignment(Qt.AlignCenter)

        self.value.setStyleSheet("font-size: 22px; color: #66fcf1;")

        layout.addWidget(self.title)
        layout.addWidget(self.value)

        self.setLayout(layout)

    def setValue(self, v):
        self.value.setText(str(v))