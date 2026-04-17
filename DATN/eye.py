import numpy as np
import cv2

def eye_aspect_ratio(eye):
    A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
    B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
    C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
    return (A + B) / (2.0 * C)

def process_eye(frame, landmarks, indices, w, h, color):
    pts = [(int(landmarks.landmark[i].x * w),
            int(landmarks.landmark[i].y * h)) for i in indices]

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)

    pad = int(0.1 * (x2 - x1))
    x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
    x2, y2 = min(w, x2 + pad), min(h, y2 + pad)

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    ear = eye_aspect_ratio(pts)
    return ear


# ===== GỘP TOÀN BỘ LOGIC MẮT =====
def process_eye_state(frame, lm, w, h,
                      eye_closed_time, frame_time,
                      EYE_CLOSED_THRESHOLD, DROWSY_EYE_TIME):

    # tính EAR
    ear_left = process_eye(frame, lm,
                           [33,160,158,133,153,144],
                           w, h, (0,255,0))

    ear_right = process_eye(frame, lm,
                            [362,385,387,263,373,380],
                            w, h, (255,0,0))

    ear_avg = (ear_left + ear_right) / 2

    # tính thời gian nhắm mắt
    if ear_avg < EYE_CLOSED_THRESHOLD:
        eye_closed_time += frame_time
    else:
        eye_closed_time = 0

    # check buồn ngủ
    drowsy_alert = False
    if eye_closed_time > DROWSY_EYE_TIME:
        drowsy_alert = True

    # ===== HIỂN THỊ DEBUG (GIỮ NGUYÊN) =====
    cv2.putText(frame, f"EAR: {ear_avg:.2f}", (30,50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    cv2.putText(frame, f"EyeTime: {eye_closed_time:.2f}s", (30,80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    # ===== HIỂN THỊ CẢNH BÁO (MẮT) =====

    return eye_closed_time, drowsy_alert