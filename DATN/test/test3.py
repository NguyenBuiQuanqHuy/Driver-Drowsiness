import cv2
import mediapipe as mp
import numpy as np
from config import HEAD_DOWN_TIME_THRESHOLD

mp_face_mesh = mp.solutions.face_mesh

# ================== TÍNH GÓC PITCH (CÚI/NGỬA) ==================
def get_head_pitch(lm, w, h):
    # 6 điểm mốc
    image_points = np.array([
        (lm.landmark[1].x * w, lm.landmark[1].y * h),     # Mũi
        (lm.landmark[152].x * w, lm.landmark[152].y * h), # Cằm
        (lm.landmark[33].x * w, lm.landmark[33].y * h),   # Mắt trái
        (lm.landmark[263].x * w, lm.landmark[263].y * h), # Mắt phải
        (lm.landmark[61].x * w, lm.landmark[61].y * h),   # Miệng trái
        (lm.landmark[291].x * w, lm.landmark[291].y * h)  # Miệng phải
    ], dtype="double")

    # Sử dụng tọa độ 3D thu nhỏ để giá trị rvec ổn định hơn
    model_points = np.array([
        (0.0, 0.0, 0.0),            # Mũi
        (0.0, -33.0, -6.5),         # Cằm
        (-22.5, 17.0, -13.5),       # Mắt trái
        (22.5, 17.0, -13.5),        # Mắt phải
        (-15.0, -15.0, -12.5),      # Miệng trái
        (15.0, -15.0, -12.5)        # Miệng phải
    ])

    focal_length = w
    center = (w / 2, h / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")

    success, rvec, tvec = cv2.solvePnP(
        model_points, image_points, camera_matrix, 
        np.zeros((4, 1)), flags=cv2.SOLVEPNP_ITERATIVE
    )

    # KHÔNG nhân 180/pi để giữ giá trị ở dạng Radian (nhỏ và mịn)
    # rvec[0][0] là góc Pitch
    return rvec[0][0]

# ================== MAIN ==================
cap = cv2.VideoCapture(0)
fps = 25
frame_time = 1 / fps

base_pitch = None
calibration_frames = 0
MAX_CALIBRATION = 50 
head_down_timer = 0
smooth_pitch = None

with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.multi_face_landmarks:
            raw_pitch = get_head_pitch(results.multi_face_landmarks[0], w, h)

            # Bộ lọc làm mượt (EMA)
            if smooth_pitch is None: smooth_pitch = raw_pitch
            else: smooth_pitch = (smooth_pitch * 0.85) + (raw_pitch * 0.15)

            # CALIBRATION
            if calibration_frames < MAX_CALIBRATION:
                if base_pitch is None: base_pitch = smooth_pitch
                else: base_pitch = (base_pitch * calibration_frames + smooth_pitch) / (calibration_frames + 1)
                calibration_frames += 1
                cv2.putText(frame, f"CALIBRATING: {int(calibration_frames/MAX_CALIBRATION*100)}%", (30, 50), 0, 0.7, (0, 255, 255), 2)
            else:
                # Đảo dấu nếu cần thiết: Mục tiêu Cúi = Dương, Ngửa = Âm
                # Thông thường với solvePnP, rvec[0] tăng khi cúi
                diff = smooth_pitch - base_pitch

                # --- ĐIỀU CHỈNH NGƯỠNG TẠI ĐÂY ---
                # Thử cúi đầu nhẹ xem diff lên bao nhiêu, thường sẽ là 0.2 - 0.5
                if diff > 0.25:  
                    status = "CUI DAU"
                    head_down_timer += frame_time
                    color = (0, 0, 255)
                elif diff < -0.20: 
                    status = "NGUA DAU"
                    head_down_timer = 0
                    color = (255, 255, 0)
                else:
                    status = "NORMAL"
                    head_down_timer = 0
                    color = (0, 255, 0)

                # Hiển thị UI
                cv2.putText(frame, f"Pitch: {smooth_pitch:.2f}", (30, 50), 0, 0.6, (255,255,255), 1)
                cv2.putText(frame, f"Diff: {diff:.2f}", (30, 80), 0, 0.7, color, 2)
                cv2.putText(frame, f"Status: {status}", (30, 110), 0, 0.7, color, 2)
                cv2.putText(frame, f"Timer: {head_down_timer:.1f}s", (30, 140), 0, 0.7, (0, 255, 255), 2)
                
                if head_down_timer > HEAD_DOWN_TIME_THRESHOLD:
                    cv2.rectangle(frame, (0,0), (w,h), (0,0,255), 10)
                    cv2.putText(frame, "MICROSLEEP!", (w//4, h//2), 0, 1.5, (0,0,255), 4)

        cv2.imshow("Head Pose Monitoring", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()