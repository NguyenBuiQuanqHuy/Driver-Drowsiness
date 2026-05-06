# handlers.py
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from config.config import *
from .history.history_manager import save_alert


def update_image(app, cv_img):
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

    app.image_label.setAlignment(Qt.AlignCenter)
    app.image_label.setPixmap(
        QPixmap.fromImage(qt_img).scaled(
            app.image_label.width(),
            app.image_label.height(),
            Qt.KeepAspectRatio
        )
    )


def update_info(app, data):
    app.lbl_ear.setText(str(data["ear"]))
    app.lbl_ear_time.setText(f"{round(data.get('ear_time',0),1)} s")

    app.lbl_mar.setText(str(data["mar"]))
    app.lbl_mar_time.setText(f"{round(data.get('mar_time',0),1)} s")

    head_text = data["head"]
    if data["head_alert"]:
        app.lbl_head.setText(data["head"])
    app.lbl_head.setText(head_text)
    app.lbl_head_time.setText(f"{round(data.get('head_time',0),1)} s")

    if data["ear_time"] > DROWSY_EYE_TIME:
        app.lbl_ear_time.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
    else:
        app.lbl_ear_time.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

    if data["mar_time"] > YAWN_TIME:
        app.lbl_mar_time.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
    else:
        app.lbl_mar_time.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

    if data["head_time"] > MICROSLEEP_TIME:
        app.lbl_head_time.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
    else:
        app.lbl_head_time.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

    app.lbl_angle.setText(
        f"x: {data['x']}\ny: {data['y']}\nz: {data['z']}"
    )

    status = data["status"]
    app.lbl_status.setText(status)

    if status == "NO FACE":
        app.lbl_status.setText("NO FACE 🚫")
        app.lbl_status.setStyleSheet("""
            background-color: #444;
            border: 2px solid gray;
            color: white;
            padding: 15px;
            font-size: 22px;
            font-weight: bold;
        """)

        app.setStyleSheet("""
            QWidget {
                background-color: #0b132b;
                color: white;
            }
            QPushButton {
                background-color: #1c2541;
                border: 2px solid #5bc0be;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5bc0be;
                color: black;
            }
        """)
        return

    if data["ear"] < EYE_CLOSED_THRESHOLD:
        app.lbl_ear.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
    else:
        app.lbl_ear.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

    if data["mar"] > MAR_THRESHOLD:
        app.lbl_mar.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
    else:
        app.lbl_mar.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

    if data["head_alert"]:
        app.lbl_head.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
    else:
        app.lbl_head.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

    if abs(data["x"]) > 15 or abs(data["y"]) > 15:
        app.lbl_angle.setStyleSheet("color: red; font-size: 16px;")
    else:
        app.lbl_angle.setStyleSheet("color: white; font-size: 16px;")

    level = 0

    if data["head_time"] > MICROSLEEP_TIME:
        level = 2
    elif (
        data["eye_time"] > DROWSY_EYE_TIME or
        data.get("yawn_alert", False)
    ):
        level = 1

    if level == 2:
        if app.voice.speak_warning("Warning! Microsleep detected! Wake up immediately!"):
            save_alert("MICROSLEEP", data)
        
        app.blink = not app.blink
        blink_color = "red" if app.blink else "#660000"

        app.lbl_status.setText("MICROSLEEP ⚠️")
        app.lbl_status.setStyleSheet(f"""
            background-color: {blink_color};
            border: 3px solid red;
            color: white;
            padding: 15px;
            font-size: 22px;
            font-weight: bold;
        """)

        app.setStyleSheet("""
            QWidget {
                background-color: #2b0000;
                color: white;
            }
            QPushButton {
                background-color: #1c2541;
                border: 2px solid #5bc0be;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5bc0be;
                color: black;
            }
        """)

    elif level == 1:
        if data["eye_time"] > DROWSY_EYE_TIME:
            if  app.voice.speak_warning("Your eyes are closing! Stay alert!"):
                save_alert("EYES CLOSED", data)          

            app.lbl_status.setText("EYES CLOSED 😴")
            app.lbl_status.setStyleSheet("""
                background-color: #ff8c00;
                border: 3px solid orange;
                color: white;
                padding: 15px;
                font-size: 22px;
                font-weight: bold;
            """)

        elif data.get("yawn_alert", False):
            if  app.voice.speak_warning("You are yawning! Stay alert!"):
                save_alert("YAWN", data)          

            app.lbl_status.setText("YAWN 😪")
            app.lbl_status.setStyleSheet("""
                background-color: #ffcc00;
                border: 3px solid yellow;
                color: black;
                padding: 15px;
                font-size: 22px;
                font-weight: bold;
            """)

        app.setStyleSheet("""
            QWidget {
                background-color: #332000;
                color: white;
            }
            QPushButton {
                background-color: #1c2541;
                border: 2px solid #5bc0be;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5bc0be;
                color: black;
            }
        """)

    else:
        app.lbl_status.setText("AWAKE")
        app.lbl_status.setStyleSheet("""
            background-color: #0d3a2f;
            border: 2px solid #00ff9c;
            color: #00ff9c;
            padding: 15px;
            font-size: 22px;
            font-weight: bold;
        """)

        app.setStyleSheet("""
            QWidget {
                background-color: #0b132b;
                color: white;
            }
            QPushButton {
                background-color: #1c2541;
                border: 2px solid #5bc0be;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5bc0be;
                color: black;
            }
        """)