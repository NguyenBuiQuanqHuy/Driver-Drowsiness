import numpy as np
import cv2
import time

prev_time_eye = time.time()

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
                      eye_closed_time,
                      EYE_CLOSED_THRESHOLD, DROWSY_EYE_TIME):

    global prev_time_eye

    # ===== TIME REAL =====
    current_time = time.time()
    dt = current_time - prev_time_eye
    prev_time_eye = current_time

    # tính EAR
    ear_left = process_eye(frame, lm,
                           [33,160,158,133,153,144],
                           w, h, (0, 255, 255))

    ear_right = process_eye(frame, lm,
                            [362,385,387,263,373,380],
                            w, h, (0, 255, 255))

    ear_avg = (ear_left + ear_right) / 2

    # tính thời gian nhắm mắt
    if ear_avg < EYE_CLOSED_THRESHOLD:
        eye_closed_time += dt
    else:
        eye_closed_time = 0

    # check buồn ngủ
    drowsy_alert = False
    if eye_closed_time > DROWSY_EYE_TIME:
        drowsy_alert = True

    # ===== HIỂN THỊ CẢNH BÁO (MẮT) =====

    return eye_closed_time, drowsy_alert, ear_avg