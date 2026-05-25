# settings_dialog.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from config.config import load_config


class SettingsDialog(QDialog):

    def __init__(self, app):
        super().__init__()

        config = load_config()

        self.app = app

        self.setWindowTitle("Settings")
        self.setFixedSize(400, 500)

        self.theme_box = QComboBox()
        self.theme_box.addItems(["Dark", "Light"])

        if self.app.current_theme == "dark":
            self.theme_box.setCurrentText("Dark")
        else:
            self.theme_box.setCurrentText("Light")
        
        # =================================
        # VOLUME
        # =================================
        self.volume_slider = QSlider(
            Qt.Horizontal
        )

        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)

        self.volume_slider.setValue(100)

        btn_apply = QPushButton("Apply")

        btn_apply.clicked.connect(self.apply_settings)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Theme"))
        layout.addWidget(self.theme_box)
        # =================================
        # THRESHOLD INFO
        # =================================
        title = QLabel("Current Thresholds")

        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        info_text = (
            f"EYE\n"
            f"Closed Threshold: {config['eye']['closed_threshold']}\n"
            f"Drowsy Time: {config['eye']['drowsy_time']}s\n\n"

            f"MOUTH\n"
            f"MAR Threshold: {config['mouth']['mar_threshold']}\n"
            f"Yawn Time: {config['mouth']['yawn_time']}s\n\n"

            f"HEAD\n"
            f"Down: {config['head']['down_threshold']}\n"
            f"Up: {config['head']['up_threshold']}\n"
            f"Left: {config['head']['left_threshold']}\n"
            f"Right: {config['head']['right_threshold']}"
        )

        info_label = QLabel(info_text)

        info_label.setWordWrap(True)

        info_label.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff99;
            padding: 10px;
            border-radius: 8px;
        """)

        layout.addWidget(info_label)
        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.volume_slider)
        layout.addStretch()
        layout.addWidget(btn_apply)

        self.setLayout(layout)

    def apply_settings(self):

        theme = self.theme_box.currentText().lower()

        self.app.change_theme(theme)

        # =============================
        # APPLY VOLUME
        # =============================
        volume = self.volume_slider.value()

        self.app.voice.set_volume(
            volume / 100
        )

        self.accept()