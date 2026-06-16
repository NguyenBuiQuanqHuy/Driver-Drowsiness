import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from config.config import load_config
config = load_config()
from .history.history_manager import save_alert

EYE_CLOSED_THRESHOLD = config["eye"]["closed_threshold"]
DROWSY_EYE_TIME = config["eye"]["drowsy_time"]

MAR_THRESHOLD = config["mouth"]["mar_threshold"]
YAWN_TIME = config["mouth"]["yawn_time"]

MICROSLEEP_TIME = config["time"]["microsleep_time"]
DISTRACTED_TIME = config["time"]["distracted_time"]


# =========================
# IMAGE UPDATE (GIỮ NGUYÊN)
# =========================
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


# =========================
# INFO UPDATE (ĐÃ FIX THEME)
# =========================
def update_info(app, data):

    # -------------------------
    # TEXT UPDATE (GIỮ NGUYÊN)
    # -------------------------
    app.lbl_ear.setText(str(data["ear"]))
    app.lbl_ear_time.setText(f"{round(data.get('ear_time',0),1)} s")

    app.lbl_mar.setText(str(data["mar"]))
    app.lbl_mar_time.setText(f"{round(data.get('mar_time',0),1)} s")

    head_text = data["head"]
    app.lbl_head.setText(head_text)

    if data["head"] == "Down":
        head_timer = data.get("head_time", 0)
    elif data["head"] in ["Left", "Right", "Up"]:
        head_timer = data.get("focus_time", 0)
    else:
        head_timer = 0

    app.lbl_head_time.setText(f"{round(head_timer,1)} s")

    app.lbl_angle.setText(
        f"x: {data['x']}\ny: {data['y']}\nz: {data['z']}"
    )

    status = data["status"] 
    app.lbl_status.setText(status)

    # =========================
    # NO FACE STATE
    # =========================
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
        return

    # =========================
    # ❌ FIX: KHÔNG SET STYLE WHITE/RED INLINE NỮA
    # 👉 CHỈ SET PROPERTY
    # =========================

    # EAR
    app.lbl_ear.setProperty(
    "alert",
    "true" if data["ear"] < EYE_CLOSED_THRESHOLD else "false"
    )

    # MAR
    app.lbl_mar.setProperty(
    "alert",
    "true" if data["mar"] > MAR_THRESHOLD else "false"
    )

    # HEAD ALERT
    app.lbl_head.setProperty("alert", data["head_alert"])

    # ANGLE ALERT
    app.lbl_angle.setProperty(
        "alert",
        abs(data["x"]) > 15 or abs(data["y"]) > 15
    )

    # TIME ALERTS
    app.lbl_ear_time.setProperty("alert", data["ear_time"] > DROWSY_EYE_TIME)
    app.lbl_mar_time.setProperty("alert", data["mar_time"] > YAWN_TIME)

    app.lbl_head_time.setProperty(
        "alert",
        (data["head"] == "Down" and data["head_time"] > MICROSLEEP_TIME)
        or
        (data["head"] in ["Left", "Right", "Up"] and data.get("focus_time", 0) > DISTRACTED_TIME)
    )

    # refresh style
    for lbl in [
        app.lbl_ear, app.lbl_mar, app.lbl_head, app.lbl_angle,
        app.lbl_ear_time, app.lbl_mar_time, app.lbl_head_time
    ]:
        lbl.style().unpolish(lbl)
        lbl.style().polish(lbl)

    # =========================
    # STATUS LOGIC (GIỮ NGUYÊN)
    # =========================
    level = 0

    if data["head_time"] > MICROSLEEP_TIME:
        level = 2
    elif (
        data["eye_time"] > DROWSY_EYE_TIME or
        data.get("yawn_alert", False) or
        data.get("focus_time", 0) > DISTRACTED_TIME
    ):
        level = 1

    # =========================
    # MICROSLEEP
    # =========================
    if level == 2:
        if app.voice.speak_warning("Warning! You are falling asleep. Wake up immediately!"):
            save_alert("DROWSINESS", data)

        app.blink = not app.blink
        blink_color = "red" if app.blink else "#660000"

        app.lbl_status.setText("DROWSINESS ⚠️")
        app.lbl_status.setStyleSheet(f"""
            background-color: {blink_color};
            border: 3px solid red;
            color: white;
            padding: 15px;
            font-size: 22px;
            font-weight: bold;
        """)

    # =========================
    # LEVEL 1 ALERTS
    # =========================
    elif level == 1:
        app.blink = not app.blink   
        if data["eye_time"] > DROWSY_EYE_TIME:
            if app.voice.speak_warning("Your eyes are closing! Stay alert!"):
                save_alert("EYES CLOSED", data)

            blink_color = "#ff8c00" if app.blink else "#663300"

            app.lbl_status.setText("EYES CLOSED 😴")
            app.lbl_status.setStyleSheet(f"""
                background-color: {blink_color};
                border: 3px solid orange;
                color: white;
                padding: 15px;
                font-size: 22px;
                font-weight: bold;
            """)

        elif data.get("yawn_alert", False):
            if app.voice.speak_warning("You are yawning! Stay alert!"):
                save_alert("YAWN", data)
            blink_color = "#ffcc00" if app.blink else "#665500"

            app.lbl_status.setText("YAWN 😪")
            app.lbl_status.setStyleSheet(f"""
                background-color: {blink_color};
                border: 3px solid yellow;
                color: black;
                padding: 15px;
                font-size: 22px;
                font-weight: bold;
            """)

        elif data.get("focus_time", 0) > DISTRACTED_TIME:
            if app.voice.speak_warning("Please focus on the road!"):
                save_alert("DISTRACTED", data)

            blink_color = "#0066cc" if app.blink else "#001f4d"

            app.lbl_status.setText("DISTRACTED ⚠️")
            app.lbl_status.setStyleSheet(f"""
                background-color: {blink_color};
                border: 3px solid cyan;
                color: white;
                padding: 15px;
                font-size: 22px;
                font-weight: bold;
            """)

    # =========================
    # AWAKE
    # =========================
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