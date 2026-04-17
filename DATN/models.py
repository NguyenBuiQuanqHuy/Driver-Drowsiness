# models.py
from tensorflow.keras.models import load_model
import numpy as np
import cv2

# Load model
eye_model = load_model("eye_model.h5")
mouth_model = load_model("mouth_model.h5")

# =========================
# Preprocess nâng cao
# =========================
def preprocess_image(img):
    if img is None or img.size == 0:
        return np.zeros((1,224,224,3), dtype=np.float32)

    # ===== Resize =====
    img = cv2.resize(img, (224,224))

    # ===== Tăng tương phản (CLAHE) =====
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])
    img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    # ===== Làm mượt (giảm noise nhẹ) =====
    img = cv2.GaussianBlur(img, (3,3), 0)

    # ===== Normalize =====
    img = img.astype(np.float32) / 255.0

    # ===== Expand dim =====
    img = np.expand_dims(img, axis=0)

    return img

# =========================
# Dự đoán mắt
# =========================
def predict_eye(img):
    return eye_model.predict(preprocess_image(img))[0][0]

# =========================
# Dự đoán miệng
# =========================
def predict_mouth(img):
    return mouth_model.predict(preprocess_image(img))[0][0]