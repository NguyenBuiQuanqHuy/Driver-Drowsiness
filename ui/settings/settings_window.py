from PyQt5.QtWidgets import *

from .settings_manager import (
    load_settings,
    save_settings
)


class SettingsWindow(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Settings")

        self.resize(300, 200)

        settings = load_settings()

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

            "voice_language": self.voice_combo.currentText()
        }

        save_settings(data)

        QMessageBox.information(
            self,
            "Settings",
            "Saved successfully"
        )

        self.accept()