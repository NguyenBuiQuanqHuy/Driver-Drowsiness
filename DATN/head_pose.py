import cv2
import mediapipe as mp
import numpy as np
from config import *
import time

# Thời gian frame trước đó (dùng để tính thời gian realtime)
prev_time = time.time()

# Biến lưu tổng thời gian cúi đầu liên tục
down_time = 0

# Khởi tạo các module của mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


# ==============================
# VẼ KHUNG BAO QUANH KHUÔN MẶT
# ==============================
def draw_face_bbox_fp(image, face_landmarks, img_w, img_h):
    x_min, y_min = img_w, img_h   # khởi tạo min
    x_max, y_max = 0, 0           # khởi tạo max

    # Duyệt tất cả điểm landmark để tìm bounding box
    for lm in face_landmarks.landmark:
        x, y = int(lm.x * img_w), int(lm.y * img_h)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x)
        y_max = max(y_max, y)

    # Vẽ hình chữ nhật quanh mặt
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)


# ==============================
# LẤY TOẠ ĐỘ 2D & 3D CÁC ĐIỂM QUAN TRỌNG
# ==============================
def getCoordinates_fp(face_landmarks, img_h, img_w):
    face_3d = []
    face_2d = []

    # Chỉ lấy 6 điểm quan trọng trên mặt
    for idx, lm in enumerate(face_landmarks.landmark):
        if idx in [33, 263, 1, 61, 291, 199]:

            # Điểm mũi (dùng để vẽ hướng)
            if idx == 1:
                nose_2d = (lm.x * img_w, lm.y * img_h)
                nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

            x, y = int(lm.x * img_w), int(lm.y * img_h)

            # Lưu vào danh sách 2D và 3D
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])

    # Chuyển sang numpy array
    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)

    return face_2d, face_3d, nose_2d, nose_3d


# ==============================
# TÍNH GÓC XOAY ĐẦU (HEAD POSE)
# ==============================
def projectCameraAngle_fp(face_2d, face_3d, img_h, img_w):

    # Ma trận camera (giả lập)
    focal_length = 1 * img_w
    cam_matrix = np.array([
        [focal_length, 0, img_h / 2],
        [0, focal_length, img_w / 2],
        [0, 0, 1]
    ])

    # Không dùng distortion
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    # Giải bài toán PnP để tìm rotation vector
    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

    # Chuyển sang ma trận xoay
    rmat, jac = cv2.Rodrigues(rot_vec)

    # Lấy góc Euler
    angles, *_ = cv2.RQDecomp3x3(rmat)

    # Đổi sang độ
    x = angles[0] * 360  # lên/xuống
    y = angles[1] * 360  # trái/phải
    z = angles[2] * 360  # nghiêng

    return x, y, z, rot_vec, trans_vec, cam_matrix, dist_matrix


# ==============================
# XÁC ĐỊNH HƯỚNG ĐẦU
# ==============================
def getHeadTilt_fp(x, y, z):

    if y < HEAD_LEFT_THRESHOLD:
        return "Left"
    elif y > HEAD_RIGHT_THRESHOLD:
        return "Right"
    elif x < HEAD_DOWN_THRESHOLD:
        return "Down"
    elif x > HEAD_UP_THRESHOLD:
        return "Up"
    else:
        return "Forward"


# ==============================
# VẼ VECTOR HƯỚNG MŨI
# ==============================
def draw_nose_projection_fp(image, x, y, nose_2d, nose_3d,
                           rot_vec, trans_vec, cam_matrix, dist_matrix):

    # Chiếu điểm 3D ra 2D
    nose_3d_projection, _ = cv2.projectPoints(
        nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix
    )

    p1 = (int(nose_2d[0]), int(nose_2d[1]))  # điểm mũi
    p2 = (int(nose_2d[0] + y * 10),
          int(nose_2d[1] - x * 10))          # hướng

    cv2.line(image, p1, p2, (255, 0, 0), 3)


# ==============================
# HIỂN THỊ TEXT HƯỚNG ĐẦU
# ==============================
def draw_head_tilt_pose_fp(image, text):
    cv2.putText(image, f"HEAD: {text}", (20, 225),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)


# ==============================
# HIỂN THỊ GÓC X, Y, Z
# ==============================
def draw_head_tilt_angle_fp(image, x, y, z):
    h, w, _ = image.shape  # lấy width

    cv2.putText(image, "x: " + str(np.round(x, 2)), (w - 180, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.putText(image, "y: " + str(np.round(y, 2)), (w - 180, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.putText(image, "z: " + str(np.round(z, 2)), (w - 180, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# ==============================
# PIPELINE CHÍNH
# ==============================
def pipelineHeadTiltPose(image, face_landmarks):
    global prev_time, down_time

    # Lấy kích thước ảnh
    img_h, img_w, img_c = image.shape

    # Lấy toạ độ
    face_2d, face_3d, nose_2d, nose_3d = getCoordinates_fp(
        face_landmarks, img_h, img_w
    )

    # Tính góc đầu
    x, y, z, rot_vec, trans_vec, cam_matrix, dist_matrix = \
        projectCameraAngle_fp(face_2d, face_3d, img_h, img_w)

    # Xác định hướng đầu
    head_pose = getHeadTilt_fp(x, y, z)

    # ==============================
    # TÍNH THỜI GIAN REALTIME
    # ==============================
    current_time = time.time()
    dt = current_time - prev_time
    prev_time = current_time

    # Nếu cúi đầu -> cộng thời gian
    if head_pose == "Down":
        down_time += dt
    else:
        down_time = 0  # reset nếu ngẩng lên

    # ==============================
    # PHÂN MỨC CẢNH BÁO
    # ==============================
    if down_time > MICROSLEEP_TIME:
        alert = "MICROSLEEP"
    elif down_time > DROWSY_TIME:
        alert = "DROWSY"
    elif down_time > WARNING_TIME:
        alert = "WARNING"
    else:
        alert = ""

    # ==============================
    # HIỂN THỊ
    # ==============================
    draw_nose_projection_fp(image, x, y, nose_2d, nose_3d,
                            rot_vec, trans_vec, cam_matrix, dist_matrix)

    draw_head_tilt_pose_fp(image, head_pose)
    draw_head_tilt_angle_fp(image, x, y, z)

    # Nếu có cảnh báo thì hiển thị đỏ
    if alert != "":
        cv2.putText(image, alert, (20, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

    return head_pose