import cv2
import mediapipe as mp

# Khởi tạo module Face Mesh của MediaPipe
mp_face_mesh = mp.solutions.face_mesh


class FaceMeshDetector:
    def __init__(self):
        # Khởi tạo bộ phát hiện Face Mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,              # Chỉ phát hiện 1 khuôn mặt
            refine_landmarks=True,        # Tăng độ chính xác landmark (mắt, môi, mống mắt)
            min_detection_confidence=0.7, # Ngưỡng tin cậy phát hiện khuôn mặt
            min_tracking_confidence=0.8   # Ngưỡng tin cậy theo dõi khuôn mặt
        )

    def process(self, frame):
        # Chuyển ảnh từ định dạng BGR (OpenCV)
        # sang RGB (MediaPipe yêu cầu)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Thực hiện phát hiện khuôn mặt và landmark
        results = self.face_mesh.process(rgb)

        # Nếu phát hiện được khuôn mặt
        if results.multi_face_landmarks:
            # Trả về landmark của khuôn mặt đầu tiên
            return results.multi_face_landmarks[0]

        # Không phát hiện khuôn mặt
        return None

    def release(self):
        # Giải phóng tài nguyên Face Mesh
        self.face_mesh.close()