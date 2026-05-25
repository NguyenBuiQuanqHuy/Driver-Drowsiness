import numpy as np
import cv2
import time
from config.config import load_config, save_config


class MouthTracker:

    def __init__(self):
        config = load_config()

        # =========================
        # CONFIG
        # =========================
        self.threshold = config["mouth"]["mar_threshold"]
        self.yawn_time = config["mouth"]["yawn_time"]

        # =========================
        # STATE
        # =========================
        self.prev_time = time.time()
        self.mouth_open_time = 0.0

        # =========================
        # CALIBRATION
        # =========================
        self.mar_buffer = []
        self.calibrated = False
        self.baseline_mar = 0.0

        # =========================
        # MOUTH INDEX
        # =========================
        self.MOUTH_IDX = [78, 308, 13, 14, 82, 87, 312, 317]

    def mouth_aspect_ratio(self, mouth):
        A = np.linalg.norm(np.array(mouth[2]) - np.array(mouth[3]))
        B = np.linalg.norm(np.array(mouth[4]) - np.array(mouth[5]))
        C = np.linalg.norm(np.array(mouth[6]) - np.array(mouth[7]))
        D = np.linalg.norm(np.array(mouth[0]) - np.array(mouth[1]))

        if D == 0:
            return 0.0

        return (A + B) / (3.0 * D)

    def process_mouth(self, frame, landmarks, w, h):
        pts = [
            (
                int(landmarks.landmark[i].x * w),
                int(landmarks.landmark[i].y * h)
            )
            for i in self.MOUTH_IDX
        ]

        mar = self.mouth_aspect_ratio(pts)

        # CHỈ VẼ BOX KHI ĐÃ CALIBRATE XONG
        if self.calibrated:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]

            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)

            pad = int(0.15 * (x2 - x1))
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(w, x2 + pad), min(h, y2 + pad)

            # Khung miệng luôn luôn màu xanh dương BGR = (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        return mar

    def calibrate(self, mar):
        self.mar_buffer.append(mar)

        if len(self.mar_buffer) >= 45:
            self.baseline_mar = float(np.mean(self.mar_buffer))
            self.threshold = max(0.45, self.baseline_mar * 2.5)

            config = load_config()
            config["mouth"]["mar_threshold"] = round(float(self.threshold), 2)
            save_config(config)

            self.mar_buffer.clear()
            self.calibrated = True
            
            self.prev_time = time.time()
            return True

        return False

    def process(self, frame, lm, w, h):
        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        # Tính MAR (Hàm này tự động quyết định vẽ hay ẩn box dựa vào self.calibrated)
        mar = self.process_mouth(frame, lm, w, h)

        if not self.calibrated:
            self.calibrate(mar)
            return {
                "mar": mar,
                "mouth_open_time": 0.0,
                "yawn_alert": False,
                "threshold": "Calibrating..."
            }

        if mar > self.threshold:
            self.mouth_open_time += dt
        else:
            self.mouth_open_time = 0.0

        yawn_alert = self.mouth_open_time > self.yawn_time

        return {
            "mar": mar,
            "mouth_open_time": self.mouth_open_time,
            "yawn_alert": yawn_alert,
            "threshold": round(self.threshold, 2)
        }