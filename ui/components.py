# components.py
from PyQt5.QtWidgets import QFrame, QLabel, QGridLayout
from .styles import BOX_STYLE


def create_box(title, has_time=False):
    """
    Tạo 1 box hiển thị thông tin (EAR, MAR, HEAD...)
    Nếu has_time=True thì có thêm cột TIME
    """
    box = QFrame()
    box.setStyleSheet(BOX_STYLE)

    layout = QGridLayout()

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet("color: #5bc0be; font-weight: bold;")

    lbl_value = QLabel("---")
    lbl_value.setStyleSheet("font-size: 18px; font-weight: bold;")

    if has_time:
        lbl_time_title = QLabel("TIME")
        lbl_time_title.setStyleSheet("color: #5bc0be; font-weight: bold;")

        lbl_time_value = QLabel("---")
        lbl_time_value.setStyleSheet("font-size: 18px; font-weight: bold;")

        layout.addWidget(lbl_title, 0, 0)
        layout.addWidget(lbl_time_title, 0, 1)

        layout.addWidget(lbl_value, 1, 0)
        layout.addWidget(lbl_time_value, 1, 1)

        box.setLayout(layout)
        return box, lbl_value, lbl_time_value
    else:
        layout.addWidget(lbl_title, 0, 0)
        layout.addWidget(lbl_value, 1, 0)

        box.setLayout(layout)
        return box, lbl_value, None