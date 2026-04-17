# ===== EYE =====
EYE_CLOSED_THRESHOLD = 0.2
DROWSY_EYE_TIME = 1

# ===== MOUTH =====
MAR_THRESHOLD = 0.45
YAWN_TIME = 1

# # ===== HEAD POSE =====
# PITCH_DOWN_THRESHOLD = 0.25
# PITCH_UP_THRESHOLD = -0.20  # (giữ nếu sau này cần debug)
# PITCH_DOWN_THRESHOLD = 3.0
# HEAD_DOWN_TIME_THRESHOLD = 2.0

# # ===== MICROSLEEP =====
# MICROSLEEP_TIME_THRESHOLD = 0.7  # 👈 THÊM QUAN TRỌNG

# # ===== FILTER =====
# EMA_ALPHA = 0.15
# CALIBRATION_FRAMES = 50
# ==============================
# NGƯỠNG HEAD POSE (ĐỘ)
# ==============================

HEAD_DOWN_THRESHOLD = -10     # cúi đầu (x > 15)
HEAD_UP_THRESHOLD = 20       # ngửa đầu
HEAD_LEFT_THRESHOLD = -20    # quay trái (y < -20)
HEAD_RIGHT_THRESHOLD = 15    # quay phải (y > 15)


# ==============================
# NGƯỠNG THỜI GIAN (GIÂY)
# ==============================

WARNING_TIME = 1.0       # cảnh báo nhẹ
DROWSY_TIME = 2.0        # buồn ngủ
MICROSLEEP_TIME = 3.0    # microsleep


# ==============================
# NGƯỠNG GẬT GÙ (NODDING)
# ==============================

NOD_COUNT_THRESHOLD = 3   # số lần gật liên tiếp để coi là buồn ngủ


# ==============================
# NGƯỠNG DAO ĐỘNG (OPTIONAL)
# ==============================

HEAD_STABLE_THRESHOLD = 5   # độ thay đổi nhỏ để coi là đứng yên bất thường


# ==============================
# FPS (để tính thời gian nếu cần)
# ==============================

FPS = 30   # camera 30fps (có thể chỉnh theo máy)