import numpy as np
import cv2
import time

prev_time_mouth = time.time()

# index cố định của miệng
MOUTH_IDX = [78, 308, 13, 14, 82, 87, 312, 317]

def mouth_aspect_ratio(lm, w, h):
    # lấy điểm ngay trong đây
    mouth = [(int(lm.landmark[i].x * w),
              int(lm.landmark[i].y * h)) for i in MOUTH_IDX]

    A = np.linalg.norm(np.array(mouth[2]) - np.array(mouth[3]))  # 13-14
    B = np.linalg.norm(np.array(mouth[4]) - np.array(mouth[5]))  # 82-87
    C = np.linalg.norm(np.array(mouth[6]) - np.array(mouth[7]))  # 312-317
    D = np.linalg.norm(np.array(mouth[0]) - np.array(mouth[1]))  # 78-308

    if D == 0:
        return 0, mouth

    mar = (A + B + C) / (3.0 * D)
    return mar, mouth


# ===== GỘP TOÀN BỘ LOGIC MIỆNG =====
def process_mouth_state(frame, lm, w, h,
                       mouth_open_time,
                       MAR_THRESHOLD, YAWN_TIME):

    global prev_time_mouth

    # ===== TIME REAL =====
    current_time = time.time()
    dt = current_time - prev_time_mouth
    prev_time_mouth = current_time

    mar, mouth_pts = mouth_aspect_ratio(lm, w, h)

    # vẽ box (giữ nguyên)
    xs = [p[0] for p in mouth_pts]
    ys = [p[1] for p in mouth_pts]
    cv2.rectangle(frame, (min(xs), min(ys)),
                  (max(xs), max(ys)), (255, 0, 0), 2)

    # tính thời gian há miệng
    if mar > MAR_THRESHOLD:
        mouth_open_time += dt
    else:
        mouth_open_time = 0

    # check ngáp
    yawn_alert = False
    if mouth_open_time > YAWN_TIME:
        yawn_alert = True

    # ===== HIỂN THỊ CẢNH BÁO =====

    return mouth_open_time, yawn_alert, mar