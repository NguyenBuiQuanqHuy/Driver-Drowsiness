import cv2
import mediapipe as mp
import numpy as np
from config.config import load_config
config = load_config()
import time

# Ngưỡng góc đầu theo từng hướng
HEAD_DOWN_THRESHOLD = config["head"]["down_threshold"]
HEAD_UP_THRESHOLD = config["head"]["up_threshold"]
HEAD_LEFT_THRESHOLD = config["head"]["left_threshold"]
HEAD_RIGHT_THRESHOLD = config["head"]["right_threshold"]

# Thời gian cảnh báo
MICROSLEEP_TIME = config["time"]["microsleep_time"]
DISTRACTED_TIME = config["time"]["distracted_time"]

# Thời gian frame trước đó (dùng để tính thời gian realtime)
prev_time = time.time()

# Tổng thời gian cúi đầu liên tục
down_time = 0

# Tổng thời gian mất tập trung liên tục
distract_time = 0

# Khởi tạo các module MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


# ==============================
# VẼ KHUNG BAO QUANH KHUÔN MẶT
# ==============================
def draw_face_bbox_fp(image, face_landmarks, img_w, img_h):
    # Khởi tạo giá trị min/max
    x_min, y_min = img_w, img_h
    x_max, y_max = 0, 0

    # Duyệt toàn bộ landmark để tìm bounding box
    for lm in face_landmarks.landmark:
        x, y = int(lm.x * img_w), int(lm.y * img_h)

        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x)
        y_max = max(y_max, y)

    # Vẽ hình chữ nhật bao quanh khuôn mặt
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max),
                  (0, 0, 255), 2)


# ==============================
# LẤY TOẠ ĐỘ 2D & 3D CÁC ĐIỂM QUAN TRỌNG
# ==============================
def getCoordinates_fp(face_landmarks, img_h, img_w):
    face_3d = []
    face_2d = []

    # Chỉ lấy 6 landmark phục vụ Head Pose Estimation
    for idx, lm in enumerate(face_landmarks.landmark):
        if idx in [33, 263, 1, 61, 291, 199]:

            # Landmark mũi dùng để vẽ vector hướng đầu
            if idx == 1:
                nose_2d = (lm.x * img_w, lm.y * img_h)
                nose_3d = (lm.x * img_w,
                           lm.y * img_h,
                           lm.z * 3000)

            x, y = int(lm.x * img_w), int(lm.y * img_h)

            # Lưu điểm ảnh 2D
            face_2d.append([x, y])

            # Lưu điểm không gian 3D
            face_3d.append([x, y, lm.z])

    # Chuyển sang numpy array
    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)

    return face_2d, face_3d, nose_2d, nose_3d


# ==============================
# TÍNH GÓC XOAY ĐẦU
# ==============================
def projectCameraAngle_fp(face_2d, face_3d, img_h, img_w):

    # Xây dựng ma trận camera giả lập
    focal_length = 1 * img_w

    cam_matrix = np.array([
        [focal_length, 0, img_w / 2],
        [0, focal_length, img_h / 2],
        [0, 0, 1]
    ])

    # Giả định camera không có méo ảnh
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    # Giải bài toán Perspective-n-Point (PnP)
    success, rot_vec, trans_vec = cv2.solvePnP(
        face_3d,
        face_2d,
        cam_matrix,
        dist_matrix
    )

    # Chuyển rotation vector sang ma trận xoay
    rmat, jac = cv2.Rodrigues(rot_vec)

    # Chuyển sang góc Euler
    angles, *_ = cv2.RQDecomp3x3(rmat)

    # Đổi sang đơn vị độ
    x = angles[0] * 360   # Pitch (lên/xuống)
    y = angles[1] * 360   # Yaw (trái/phải)
    z = angles[2] * 360   # Roll (nghiêng)

    return x, y, z, rot_vec, trans_vec, cam_matrix, dist_matrix


# ==============================
# XÁC ĐỊNH HƯỚNG ĐẦU
# ==============================
def getHeadTilt_fp(x, y, z):

    # Quay sang trái
    if y < HEAD_LEFT_THRESHOLD:
        return "Left"

    # Quay sang phải
    elif y > HEAD_RIGHT_THRESHOLD:
        return "Right"

    # Cúi đầu
    elif x < HEAD_DOWN_THRESHOLD:
        return "Down"

    # Ngẩng đầu
    elif x > HEAD_UP_THRESHOLD:
        return "Up"

    # Nhìn thẳng
    else:
        return "Forward"


# ==============================
# VẼ VECTOR HƯỚNG MŨI
# ==============================
def draw_nose_projection_fp(image, x, y, nose_2d, nose_3d,
                           rot_vec, trans_vec,
                           cam_matrix, dist_matrix):

    # Chiếu điểm mũi từ không gian 3D xuống ảnh 2D
    nose_3d_projection, _ = cv2.projectPoints(
        nose_3d,
        rot_vec,
        trans_vec,
        cam_matrix,
        dist_matrix
    )

    # Điểm gốc tại mũi
    p1 = (int(nose_2d[0]), int(nose_2d[1]))

    # Điểm cuối biểu diễn hướng đầu
    p2 = (
        int(nose_2d[0] + y * 10),
        int(nose_2d[1] - x * 10)
    )

    # Vẽ vector hướng đầu
    cv2.line(image, p1, p2, (0, 255, 0), 3)


# ==============================
# HIỂN THỊ HƯỚNG ĐẦU
# ==============================
def draw_head_tilt_pose_fp(image, text):
    cv2.putText(
        image,
        f"HEAD: {text}",
        (20, 225),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 0),
        2
    )


# ==============================
# HIỂN THỊ GÓC X, Y, Z
# ==============================
def draw_head_tilt_angle_fp(image, x, y, z):

    h, w, _ = image.shape

    # Hiển thị góc Pitch
    cv2.putText(image, "x: " + str(np.round(x, 2)),
                (w - 180, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)

    # Hiển thị góc Yaw
    cv2.putText(image, "y: " + str(np.round(y, 2)),
                (w - 180, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)

    # Hiển thị góc Roll
    cv2.putText(image, "z: " + str(np.round(z, 2)),
                (w - 180, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)


# ==============================
# PIPELINE CHÍNH
# ==============================
def pipelineHeadTiltPose(image, face_landmarks):

    global prev_time, down_time, distract_time

    # Lấy kích thước ảnh
    img_h, img_w, img_c = image.shape

    # Trích xuất các điểm đặc trưng khuôn mặt
    face_2d, face_3d, nose_2d, nose_3d = getCoordinates_fp(
        face_landmarks,
        img_h,
        img_w
    )

    # Tính toán góc đầu bằng Head Pose Estimation
    x, y, z, rot_vec, trans_vec, cam_matrix, dist_matrix = \
        projectCameraAngle_fp(
            face_2d,
            face_3d,
            img_h,
            img_w
        )

    # Xác định hướng đầu hiện tại
    head_pose = getHeadTilt_fp(x, y, z)

    # ==============================
    # TÍNH THỜI GIAN REALTIME
    # ==============================
    current_time = time.time()
    dt = current_time - prev_time
    prev_time = current_time

    # Nếu đang cúi đầu thì cộng dồn thời gian
    if head_pose == "Down":
        down_time += dt
    else:
        down_time = 0

    # Nếu không nhìn phía trước thì cộng dồn thời gian mất tập trung
    if head_pose in ["Left", "Right", "Up"]:
        distract_time += dt
    else:
        distract_time = 0

    # ==============================
    # PHÁT HIỆN TRẠNG THÁI
    # ==============================
    if down_time > MICROSLEEP_TIME:
        alert = "DROWSINESS"

    elif distract_time > DISTRACTED_TIME:
        alert = "DISTRACTED"

    else:
        alert = ""

    # Vẽ vector hướng đầu lên ảnh
    draw_nose_projection_fp(
        image,
        x, y,
        nose_2d,
        nose_3d,
        rot_vec,
        trans_vec,
        cam_matrix,
        dist_matrix
    )

    # Trả kết quả cho module chính
    return (
        head_pose,
        alert,
        x,
        y,
        z,
        down_time,
        distract_time
    )