import cv2
import numpy as np

class HeadPoseTracker:
    def __init__(self):
        # Tọa độ 3D chuẩn của một khuôn mặt (Generic 3D model points)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Mũi (Nose tip)
            (0.0, -330.0, -65.0),        # Cằm (Chin)
            (-225.0, 170.0, -135.0),     # Mắt trái (Left eye corner)
            (225.0, 170.0, -135.0),      # Mắt phải (Right eye corner)
            (-150.0, -150.0, -125.0),    # Mép miệng trái (Left mouth corner)
            (150.0, -150.0, -125.0)      # Mép miệng phải (Right mouth corner)
        ])

    def get_pose(self, landmarks, w, h):
        if not landmarks:
            return None

        # Trích xuất 6 điểm tương ứng từ landmarks của MediaPipe (tỉ lệ 0-1 sang pixel)
        # Chỉ số: Mũi(1), Cằm(152), Mắt trái(33), Mắt phải(263), Miệng trái(61), Miệng phải(291)
        image_points = np.array([
            (landmarks[1][0] * w, landmarks[1][1] * h),     
            (landmarks[152][0] * w, landmarks[152][1] * h), 
            (landmarks[33][0] * w, landmarks[33][1] * h),   
            (landmarks[263][0] * w, landmarks[263][1] * h), 
            (landmarks[61][0] * w, landmarks[61][1] * h),   
            (landmarks[291][0] * w, landmarks[291][1] * h)  
        ], dtype="double")

        # Giả định thông số Camera (Camera Matrix)
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )

        dist_coeffs = np.zeros((4, 1)) # Giả định không có biến dạng ống kính

        # Giải bài toán PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        # Chuyển ma trận xoay sang góc Euler (Pitch, Yaw, Roll)
        rmat, _ = cv2.Rodrigues(rotation_vector)
        angles, _, _, _, _, _ = cv2.decomposeProjectionMatrix(np.hstack((rmat, translation_vector)))
        
        pitch, yaw, roll = angles.flatten()
        
        # Chuẩn hóa lại góc Pitch (tùy thuộc vào tọa độ thế giới)
        # Thường Pitch > 0 là ngửa, Pitch < 0 là cúi (hoặc ngược lại tùy trục)
        return pitch, yaw, roll

    def update(self, current_pitch, dt):
        """
        Dùng để tính tốc độ thay đổi hoặc lọc nhiễu nếu cần.
        Trong code chính của bạn, 'diff' đang được dùng như độ lệch so với vị trí thẳng.
        """
        # Giả sử tư thế thẳng là 0 độ. Bạn có thể calibrate lại giá trị này.
        baseline = 0 
        diff = current_pitch - baseline
        return diff