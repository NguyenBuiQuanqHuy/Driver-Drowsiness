# layout.py
from PyQt5.QtWidgets import *
from .history.history_window import HistoryWindow


def build_right_panel(app):
    """
    Panel bên phải (EAR, MAR, HEAD, STATUS)
    """
    layout = QVBoxLayout()
    layout.addWidget(app.box_ear)
    layout.addWidget(app.box_mar)
    layout.addWidget(app.box_head)
    layout.addWidget(app.box_angle)
    layout.addWidget(app.lbl_status)
    layout.addStretch()

    panel = QWidget()
    panel.setLayout(layout)
    panel.setFixedWidth(320)

    return panel

def build_left_stack(app):
    """
    Tạo vùng bên trái gồm:
    - Camera view
    - History view
    (dùng QStackedLayout để chuyển qua lại)
    """

    app.stack = QStackedLayout()

    # ===== CAMERA VIEW =====
    camera_widget = QWidget()
    cam_layout = QVBoxLayout()
    cam_layout.addWidget(app.image_label)
    camera_widget.setLayout(cam_layout)

    # ===== HISTORY VIEW =====

    app.history_view = HistoryWindow()

    # add vào stack
    app.stack.addWidget(camera_widget)      # index 0
    app.stack.addWidget(app.history_view)   # index 1

    # wrap lại
    container = QWidget()
    container.setLayout(app.stack)

    return container    


def build_buttons(app):
    """
    Tạo các button control
    """
    app.btn_settings = QPushButton("⚙ Settings")
    app.btn_history = QPushButton("📊 Alert History")
    app.btn_performance = QPushButton("📈 Performance")

    settings_layout = QHBoxLayout()
    settings_layout.addWidget(app.btn_settings)
    settings_layout.addWidget(app.btn_history)
    settings_layout.addWidget(app.btn_performance)

    app.btn_camera = QPushButton("🎥 Camera")
    app.btn_video = QPushButton("📁 Video")
    app.btn_stop = QPushButton("⏹ Stop")

    control_layout = QHBoxLayout()
    control_layout.addWidget(app.btn_camera)
    control_layout.addWidget(app.btn_video)
    control_layout.addWidget(app.btn_stop)

    return settings_layout, control_layout