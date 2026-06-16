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

        # Ngưỡng MAR xác định miệng mở
        self.threshold = config["mouth"]["mar_threshold"]

        # Thời gian miệng mở liên tục để xác định ngáp
        self.yawn_time = config["mouth"]["yawn_time"]

        # =========================
        # STATE
        # =========================

        # Thời điểm xử lý frame trước đó
        self.prev_time = time.time()

        # Tổng thời gian miệng mở liên tục
        self.mouth_open_time = 0.0

        # =========================
        # CALIBRATION
        # =========================

        # Bộ đệm lưu các giá trị MAR trong giai đoạn hiệu chỉnh
        self.mar_buffer = []

        # Trạng thái đã hiệu chỉnh hay chưa
        self.calibrated = False

        # Giá trị MAR chuẩn của người dùng
        self.baseline_mar = 0.0

        # =========================
        # MOUTH INDEX
        # =========================

        # Các landmark của miệng sử dụng để tính MAR
        self.MOUTH_IDX = [78, 308, 13, 14, 82, 87, 312, 317]

    def mouth_aspect_ratio(self, mouth):

        # Khoảng cách dọc chính giữa môi
        A = np.linalg.norm(np.array(mouth[2]) - np.array(mouth[3]))

        # Khoảng cách dọc bên trái
        B = np.linalg.norm(np.array(mouth[4]) - np.array(mouth[5]))

        # Khoảng cách dọc bên phải
        C = np.linalg.norm(np.array(mouth[6]) - np.array(mouth[7]))

        # Khoảng cách ngang của miệng
        D = np.linalg.norm(np.array(mouth[0]) - np.array(mouth[1]))

        # Tránh chia cho 0
        if D == 0:
            return 0.0

        # Công thức tính MAR (Mouth Aspect Ratio)
        return (A + B) / (3.0 * D)

    def process_mouth(self, frame, landmarks, w, h):

        # Lấy tọa độ pixel của các landmark miệng
        pts = [
            (
                int(landmarks.landmark[i].x * w),
                int(landmarks.landmark[i].y * h)
            )
            for i in self.MOUTH_IDX
        ]

        # Tính giá trị MAR
        mar = self.mouth_aspect_ratio(pts)

        # CHỈ VẼ BOX KHI ĐÃ CALIBRATE XONG
        if self.calibrated:

            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]

            # Tìm vùng bao quanh miệng
            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)

            # Thêm khoảng đệm quanh miệng
            pad = int(0.15 * (x2 - x1))

            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(w, x2 + pad), min(h, y2 + pad)

            # Khung miệng màu xanh dương
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

        return mar

    def calibrate(self, mar):

        # Lưu giá trị MAR hiện tại vào bộ đệm
        self.mar_buffer.append(mar)

        # Sau 45 frame tiến hành hiệu chỉnh
        if len(self.mar_buffer) >= 45:

            # Tính MAR trung bình
            self.baseline_mar = float(np.mean(self.mar_buffer))

            # Thiết lập ngưỡng phát hiện ngáp
            self.threshold = max(
                0.45,
                self.baseline_mar * 2.5
            )

            # Lưu ngưỡng vào file cấu hình
            config = load_config()
            config["mouth"]["mar_threshold"] = round(
                float(self.threshold), 2
            )
            save_config(config)

            # Xóa dữ liệu calibration
            self.mar_buffer.clear()

            # Đánh dấu đã hiệu chỉnh
            self.calibrated = True

            # Reset thời gian
            self.prev_time = time.time()

            return True

        return False

    def process(self, frame, lm, w, h):

        # Tính thời gian giữa hai frame
        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        # Tính MAR
        # Hàm này tự quyết định vẽ hoặc ẩn box
        mar = self.process_mouth(frame, lm, w, h)

        # Nếu chưa calibration
        if not self.calibrated:

            self.calibrate(mar)

            return {
                "mar": mar,
                "mouth_open_time": 0.0,
                "yawn_alert": False,
                "threshold": "Calibrating..."
            }

        # Nếu MAR vượt ngưỡng => miệng đang mở
        if mar > self.threshold:
            self.mouth_open_time += dt
        else:
            # Miệng đóng lại -> reset thời gian
            self.mouth_open_time = 0.0

        # Kiểm tra có ngáp hay không
        yawn_alert = self.mouth_open_time > self.yawn_time

        # Trả kết quả xử lý
        return {
            "mar": mar,
            "mouth_open_time": self.mouth_open_time,
            "yawn_alert": yawn_alert,
            "threshold": round(self.threshold, 2)
        }