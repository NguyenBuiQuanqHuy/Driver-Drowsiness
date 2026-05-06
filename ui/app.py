# app.py
import cv2
from config.config import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from .video_thread import VideoThread
from .voice import Voice

from .styles import MAIN_STYLE, STATUS_DEFAULT
from .components import create_box
from .layout import build_right_panel, build_buttons, build_left_stack
from .handlers import update_image, update_info
from .history.history_window import HistoryWindow


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Driver Drowsiness Detection")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(MAIN_STYLE)

        self.blink = False
        self.last_speak_time = 0

        self.image_label = QLabel()
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setStyleSheet("border: 3px solid #5bc0be;")

        self.box_ear, self.lbl_ear, self.lbl_ear_time = create_box("EAR", True)
        self.box_mar, self.lbl_mar, self.lbl_mar_time = create_box("MAR", True)
        self.box_head, self.lbl_head, self.lbl_head_time = create_box("HEAD", True)
        self.box_angle, self.lbl_angle, _ = create_box("ANGLE (x,y,z)", False)

        self.lbl_status = QLabel("READY")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet(STATUS_DEFAULT)

        right_panel = build_right_panel(self)
        settings_layout, control_layout = build_buttons(self)

        left_panel = build_left_stack(self)

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(right_panel, 1)

        layout = QVBoxLayout()
        layout.addLayout(main_layout)
        layout.addLayout(settings_layout)
        layout.addLayout(control_layout)
        self.setLayout(layout)

        self.thread = VideoThread()
        self.is_paused = False

        self.thread.change_pixmap_signal.connect(lambda img: update_image(self, img))
        self.thread.data_signal.connect(lambda data: update_info(self, data))

        self.btn_camera.clicked.connect(self.start_camera)
        self.btn_video.clicked.connect(self.open_file)
        self.btn_stop.clicked.connect(self.toggle_pause)
        self.btn_stop.setText("⏸ Pause")

        self.btn_history.clicked.connect(self.toggle_history)

        self.voice = Voice()

        # ===== ALERT CONTROL =====
        self.last_alert_type = None
        self.last_alert_time = 0
        self.last_voice_time = 0

    def start_camera(self):
    # chuyển về camera view nếu đang ở history
        if hasattr(self, "stack"):
            self.stack.setCurrentIndex(0)
            self.btn_history.setText("📊 Alert History")

        self.thread.stop()
        self.thread.start_camera()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn video")
        if file_path:
            # chuyển về camera view
            if hasattr(self, "stack"):
                self.stack.setCurrentIndex(0)
                self.btn_history.setText("📊 Alert History")

            self.thread.stop()
            self.thread.start_video(file_path)

    def stop_video(self):
        self.thread.stop()
        self.is_paused = False
        self.btn_stop.setText("⏸ Pause")

    def toggle_pause(self):
        if not self.thread._run_flag:
            return

        if not self.is_paused:
            self.thread.pause()
            self.btn_stop.setText("▶ Resume")
            self.is_paused = True
        else:
            self.thread.resume()
            self.btn_stop.setText("⏸ Pause")
            self.is_paused = False  

    def toggle_history(self):
    # đang ở camera
        if self.stack.currentIndex() == 0:
            self.history_view.load_data()
            self.stack.setCurrentIndex(1)
            self.btn_history.setText("⬅ Back")
        else:
            self.stack.setCurrentIndex(0)
            self.btn_history.setText("📊 Alert History")             

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()