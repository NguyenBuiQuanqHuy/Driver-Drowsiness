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

        # Ngưỡng EAR xác định mắt nhắm
        self.threshold = config["eye"]["closed_threshold"]

        # Thời gian mắt đóng liên tục để cảnh báo buồn ngủ
        self.drowsy_eye_time = config["eye"]["drowsy_time"]

        # =========================
        # STATE (runtime)
        # =========================

        # Thời điểm xử lý frame trước đó
        self.prev_time = time.time()

        # Tổng thời gian mắt đang đóng
        self.eye_closed_time = 0.0

        # =========================
        # CALIBRATION
        # =========================

        # Bộ đệm lưu các giá trị EAR dùng cho hiệu chỉnh
        self.ear_buffer = []

        # Trạng thái đã hiệu chỉnh hay chưa
        self.calibrated = False

        # Giá trị EAR chuẩn của người dùng
        self.baseline_ear = 0.0

    def eye_aspect_ratio(self, eye):
        # Khoảng cách dọc thứ nhất
        A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))

        # Khoảng cách dọc thứ hai
        B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))

        # Khoảng cách ngang của mắt
        C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))

        # Tránh lỗi chia cho 0
        if C == 0:
            return 0.0

        # Công thức tính EAR
        return (A + B) / (2.0 * C)

    def process_eye(self, frame, landmarks, indices, w, h):
        # Chuyển landmark từ tọa độ chuẩn hóa sang tọa độ ảnh
        pts = [
            (int(landmarks.landmark[i].x * w),
             int(landmarks.landmark[i].y * h))
            for i in indices
        ]

        # CHỈ VẼ BOX KHI ĐÃ CALIBRATE XONG
        if self.calibrated:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]

            # Tìm giới hạn của vùng mắt
            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)

            # Thêm padding để khung nhìn đẹp hơn
            pad = int(0.15 * (x2 - x1))
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(w, x2 + pad), min(h, y2 + pad)

            # Vẽ khung mắt màu vàng
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        # Trả về giá trị EAR của mắt
        return self.eye_aspect_ratio(pts)

    def calibrate(self, ear_avg):
        # Lưu EAR hiện tại vào bộ đệm
        self.ear_buffer.append(ear_avg)

        # Sau 45 frame thì thực hiện hiệu chỉnh
        if len(self.ear_buffer) >= 45:

            # Tính EAR trung bình làm baseline
            self.baseline_ear = float(np.mean(self.ear_buffer))

            # Thiết lập ngưỡng mắt nhắm bằng 70% baseline
            self.threshold = self.baseline_ear * 0.70

            # Lưu ngưỡng mới vào file cấu hình
            config = load_config()
            config["eye"]["closed_threshold"] = round(float(self.threshold), 2)
            save_config(config)

            # Xóa dữ liệu calibration
            self.ear_buffer.clear()

            # Đánh dấu hoàn tất calibration
            self.calibrated = True

            # Reset thời gian xử lý
            self.prev_time = time.time()
            return True

        return False

    def process(self, frame, lm, w, h):
        # Tính thời gian giữa 2 frame liên tiếp
        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        # Tính EAR mắt trái
        ear_left = self.process_eye(frame, lm, [33, 160, 158, 133, 153, 144], w, h)

        # Tính EAR mắt phải
        ear_right = self.process_eye(frame, lm, [362, 385, 387, 263, 380, 373], w, h)

        # EAR trung bình của hai mắt
        ear_avg = (ear_left + ear_right) / 2.0

        # Nếu chưa hiệu chỉnh thì thực hiện calibration
        if not self.calibrated:
            self.calibrate(ear_avg)
            return {
                "ear": ear_avg,
                "eye_closed_time": 0.0,
                "drowsy_alert": False,
                "threshold": "Calibrating..."
            }

        # Nếu EAR nhỏ hơn ngưỡng => mắt đang đóng
        if ear_avg < self.threshold:
            self.eye_closed_time += dt
        else:
            # Mắt mở lại => reset thời gian đóng mắt
            self.eye_closed_time = 0.0

        # Kiểm tra có vượt ngưỡng cảnh báo buồn ngủ hay không
        drowsy_alert = self.eye_closed_time > self.drowsy_eye_time

        # Trả về kết quả xử lý
        return {
            "ear": ear_avg,
            "eye_closed_time": self.eye_closed_time,
            "drowsy_alert": drowsy_alert,
            "threshold": round(self.threshold, 2)
        }