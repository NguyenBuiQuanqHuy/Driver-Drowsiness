import cv2


# =========================================
# SCAN CAMERAS
# =========================================
# Hàm này dùng để tìm tất cả camera
# đang kết nối với máy tính.
#
# Ví dụ kết quả:
# [0, 1]
#
# nghĩa là:
# - camera laptop
# - webcam ngoài
# =========================================
def scan_cameras(max_cameras=5):

    cameras = []

    # =====================================
    # Scan từ camera ID 0 -> max_cameras
    # =====================================
    for i in range(max_cameras):

        cap = cv2.VideoCapture(i)

        # =================================
        # Nếu camera mở được
        # =================================
        if cap.isOpened():

            cameras.append(i)

            cap.release()

    return cameras


# =========================================
# GET CAMERA INFO
# =========================================
# Lấy thông tin camera:
# - resolution
# - fps
# - brightness
# - contrast
# =========================================
def get_camera_info(camera_id=0):

    cap = cv2.VideoCapture(camera_id)

    # =====================================
    # Nếu camera không mở được
    # =====================================
    if not cap.isOpened():

        return {
            "status": "Disconnected"
        }

    # =====================================
    # Resolution
    # =====================================
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # =====================================
    # FPS
    # =====================================
    fps = cap.get(cv2.CAP_PROP_FPS)

    # =====================================
    # Brightness
    # =====================================
    brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)

    # =====================================
    # Contrast
    # =====================================
    contrast = cap.get(cv2.CAP_PROP_CONTRAST)

    cap.release()

    # =====================================
    # Return data
    # =====================================
    return {

        "status": "Connected",

        "camera_id": camera_id,

        "resolution": f"{width}x{height}",

        "fps": round(fps, 2),

        "brightness": round(brightness, 2),

        "contrast": round(contrast, 2)
    }