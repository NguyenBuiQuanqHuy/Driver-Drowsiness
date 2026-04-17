import cv2
import mediapipe as mp
import numpy as np
from config import HEAD_DOWN_TIME_THRESHOLD

mp_face_mesh = mp.solutions.face_mesh

# ================== HEAD POSE → FACE NORMAL ==================
def get_face_normal(lm, w, h):
    image_points = np.array([
        (lm.landmark[1].x * w, lm.landmark[1].y * h),     # Nose
        (lm.landmark[152].x * w, lm.landmark[152].y * h), # Chin
        (lm.landmark[33].x * w, lm.landmark[33].y * h),   # Left eye
        (lm.landmark[263].x * w, lm.landmark[263].y * h), # Right eye
        (lm.landmark[61].x * w, lm.landmark[61].y * h),   # Left mouth
        (lm.landmark[291].x * w, lm.landmark[291].y * h)  # Right mouth
    ], dtype="double")

    model_points = np.array([
        (0.0, 0.0, 0.0),
        (0.0, -63.6, -12.5),
        (-43.3, 32.7, -26.0),
        (43.3, 32.7, -26.0),
        (-28.9, -28.9, -24.1),
        (28.9, -28.9, -24.1)
    ])

    focal_length = w
    center = (w / 2, h / 2)

    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")

    dist_coeffs = np.zeros((4, 1))

    success, rvec, tvec = cv2.solvePnP(
        model_points, image_points,
        camera_matrix, dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    rmat, _ = cv2.Rodrigues(rvec)

    # 👉 vector pháp tuyến (hướng mặt)
    face_normal = rmat[:, 2]

    return face_normal


# ================== CAMERA ==================
cap = cv2.VideoCapture(0)

fps = 25
frame_time = 1 / fps
delay = int(1000 / fps)

# ================== CALIBRATION ==================
base_down = None
calibration_frames = 0
MAX_CALIBRATION_FRAMES = fps * 2

head_down_time = 0
smooth_down = None

print("=== GIU DAU THANG 2 GIAY DAU ===")

with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0]

            # ===== LẤY FACE NORMAL =====
            face_normal = get_face_normal(lm, w, h)

            # 👉 trục Y = cúi/ngửa
            down_score = face_normal[1]

            # 👉 đảo dấu nếu cần (tuỳ camera)
            down_score = -down_score

            # ===== SMOOTHING =====
            if smooth_down is None:
                smooth_down = down_score
            else:
                smooth_down = 0.8 * smooth_down + 0.2 * down_score

            down_score = smooth_down

            # ===== CALIBRATION =====
            if calibration_frames < MAX_CALIBRATION_FRAMES:
                if base_down is None:
                    base_down = down_score
                else:
                    base_down = (base_down * calibration_frames + down_score) / (calibration_frames + 1)

                calibration_frames += 1

                cv2.putText(frame,
                            f"CALIBRATING {int(calibration_frames/MAX_CALIBRATION_FRAMES*100)}%",
                            (30, 50), 0, 1, (0,255,0), 2)

            else:
                # ===== SO SÁNH =====
                diff = down_score - base_down

                # ===== DETECT =====
                if diff > 0.25:   # 👈 chỉnh ở đây
                    head_down_time += frame_time
                    status = "CUI DAU"
                    color = (0,0,255)
                else:
                    head_down_time = 0
                    status = "BINH THUONG"
                    color = (0,255,0)

                # ===== HIỂN THỊ =====
                cv2.putText(frame, f"Down: {down_score:.2f}", (30,50), 0, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"Base: {base_down:.2f}", (30,80), 0, 0.7, (200,200,200), 2)
                cv2.putText(frame, f"Diff: {diff:.2f}", (30,110), 0, 0.7, color, 2)
                cv2.putText(frame, f"Status: {status}", (30,140), 0, 0.7, color, 2)
                cv2.putText(frame, f"Time: {head_down_time:.1f}s", (30,170), 0, 0.7, (0,255,255), 2)

                if head_down_time > HEAD_DOWN_TIME_THRESHOLD:
                    cv2.rectangle(frame, (0,0), (w,h), (0,0,255), 8)
                    cv2.putText(frame, "MICROSLEEP!", (w//4, h//2), 0, 1.5, (0,0,255), 4)

        cv2.imshow("Head Pose - Face Normal", frame)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()