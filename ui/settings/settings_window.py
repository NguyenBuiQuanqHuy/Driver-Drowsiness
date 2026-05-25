from PyQt5.QtWidgets import *

from .settings_dialog import (
    load_settings,
    save_settings
)

from config.config import load_config

from PyQt5.QtCore import Qt


class SettingsWindow(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Settings")

        self.setMinimumSize(400, 500)

        settings = load_settings()

        config = load_config()

        layout = QVBoxLayout()

        # =================================
        # THEME
        # =================================
        layout.addWidget(QLabel("Theme"))

        self.theme_combo = QComboBox()

        self.theme_combo.addItems([
            "Dark",
            "White"
        ])

        self.theme_combo.setCurrentText(
            settings["theme"]
        )

        layout.addWidget(self.theme_combo)

        # =================================
        # VOICE
        # =================================
        layout.addWidget(QLabel("Voice Language"))

        self.voice_combo = QComboBox()

        self.voice_combo.addItems([
            "English",
            "Vietnamese"
        ])

        self.voice_combo.setCurrentText(
            settings["voice_language"]
        )

        layout.addWidget(self.voice_combo)
        # =================================
        # THRESHOLD INFO
        # =================================
        info_title = QLabel(
            "Current Thresholds"
        )

        info_title.setStyleSheet(
            "font-weight: bold; font-size: 14px;"
        )

        layout.addWidget(info_title)

        info_text = (
            f"===== EYE =====\n"
            f"Closed Threshold: {config['eye']['closed_threshold']}\n"
            f"Drowsy Time: {config['eye']['drowsy_time']}s\n\n"

            f"===== MOUTH =====\n"
            f"MAR Threshold: {config['mouth']['mar_threshold']}\n"
            f"Yawn Time: {config['mouth']['yawn_time']}s\n\n"

            f"===== HEAD =====\n"
            f"Down: {config['head']['down_threshold']}\n"
            f"Up: {config['head']['up_threshold']}\n"
            f"Left: {config['head']['left_threshold']}\n"
            f"Right: {config['head']['right_threshold']}"
            f"Microsleep Time  : {config['time']['microsleep_time']}s\n"
            f"Distracted Time  : {config['time']['distracted_time']}s"
        )

        self.info_label = QLabel(info_text)

        self.info_label.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff99;
            padding: 10px;
            border-radius: 8px;
        """)

        layout.addWidget(self.info_label)
        # =================================
        # VOLUME
        # =================================
        layout.addWidget(QLabel("Volume"))

        self.volume_slider = QSlider(
            Qt.Horizontal
        )

        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)

        self.volume_slider.setValue(
            settings.get("volume", 100)
        )

        layout.addWidget(
            self.volume_slider
        )

        # =================================
        # SAVE
        # =================================
        btn_save = QPushButton(
            "Save"
        )

        btn_save.clicked.connect(
            self.save
        )

        layout.addWidget(btn_save)

        self.setLayout(layout)

    # =====================================
    # SAVE
    # =====================================
    def save(self):

        data = {

            "theme": self.theme_combo.currentText(),

            "voice_language": self.voice_combo.currentText(),

            "volume": self.volume_slider.value()
        }

        save_settings(data)

        QMessageBox.information(
            self,
            "Settings",
            "Saved successfully"
        )

        self.accept()