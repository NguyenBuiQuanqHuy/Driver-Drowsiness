import numpy as np
import cv2
import time
from config.config import load_config, save_config


class EyeTracker:
    def __init__(self):
        config = load_config()

        # =========================
        # CONFIG
        # =========================
        self.threshold = config["eye"]["closed_threshold"]
        self.drowsy_eye_time = config["eye"]["drowsy_time"]

        # =========================
        # STATE (runtime)
        # =========================
        self.prev_time = time.time()
        self.eye_closed_time = 0.0

        # =========================
        # CALIBRATION
        # =========================
        self.ear_buffer = []
        self.calibrated = False
        self.baseline_ear = 0.0

    def eye_aspect_ratio(self, eye):
        A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
        B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
        C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))

        if C == 0:
            return 0.0

        return (A + B) / (2.0 * C)

    def process_eye(self, frame, landmarks, indices, w, h):
        pts = [
            (int(landmarks.landmark[i].x * w),
             int(landmarks.landmark[i].y * h))
            for i in indices
        ]

        # CHỈ VẼ BOX KHI ĐÃ CALIBRATE XONG
        if self.calibrated:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]

            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)

            pad = int(0.15 * (x2 - x1))
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(w, x2 + pad), min(h, y2 + pad)

            # Khung mắt luôn luôn màu vàng tươi BGR = (0, 255, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        return self.eye_aspect_ratio(pts)

    def calibrate(self, ear_avg):
        self.ear_buffer.append(ear_avg)

        if len(self.ear_buffer) >= 45:
            self.baseline_ear = float(np.mean(self.ear_buffer))
            self.threshold = self.baseline_ear * 0.70

            config = load_config()
            config["eye"]["closed_threshold"] = round(float(self.threshold), 2)
            save_config(config)

            self.ear_buffer.clear()
            self.calibrated = True

            self.prev_time = time.time()
            return True

        return False

    def process(self, frame, lm, w, h):
        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        # Tính toán EAR mắt trái và mắt phải
        ear_left = self.process_eye(frame, lm, [33, 160, 158, 133, 153, 144], w, h)
        ear_right = self.process_eye(frame, lm, [362, 385, 387, 263, 380, 373], w, h)

        ear_avg = (ear_left + ear_right) / 2.0

        if not self.calibrated:
            self.calibrate(ear_avg)
            return {
                "ear": ear_avg,
                "eye_closed_time": 0.0,
                "drowsy_alert": False,
                "threshold": "Calibrating..."
            }

        if ear_avg < self.threshold:
            self.eye_closed_time += dt
        else:
            self.eye_closed_time = 0.0

        drowsy_alert = self.eye_closed_time > self.drowsy_eye_time

        return {
            "ear": ear_avg,
            "eye_closed_time": self.eye_closed_time,
            "drowsy_alert": drowsy_alert,
            "threshold": round(self.threshold, 2)
        }