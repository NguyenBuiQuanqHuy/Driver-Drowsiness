import os
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    classification_report
)

import mediapipe as mp

# Tích hợp Tracker tự động Calibration
from detection.eye import EyeTracker
from detection.mouth import MouthTracker
from detection.head_pose import pipelineHeadTiltPose

from config.config import load_config

config = load_config()
mp_face_mesh = mp.solutions.face_mesh


# =========================================
# LABELS (Chỉ giữ 4 nhãn trạng thái lỗi mục tiêu)
# =========================================
LABELS = [
    "Distracted",
    "EyeClosed",
    "Drowsiness",
    "Yawn"
]


# =========================================
# STORAGE
# =========================================
y_true = []
y_pred = []

processing_times = []
total_frames = 0


# =========================================
# EVALUATE VIDEO
# =========================================
def evaluate_video(video_path):
    global total_frames

    cap = cv2.VideoCapture(video_path)

    # Khởi tạo Tracker độc lập cho từng video test
    eye_tracker = EyeTracker()
    mouth_tracker = MouthTracker()
    
    # Đọc trước ngưỡng cấu hình dự phòng từ config
    FIXED_EYE_THRESH = config.get("EYE_CLOSED_THRESHOLD", 0.2)
    FIXED_MAR_THRESH = config.get("MAR_THRESHOLD", 0.5)

    predictions = []

    with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
    ) as face_mesh:

        while True:
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            total_frames += 1
            h, w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            state = "None"

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # 1. Trích xuất hướng đầu
                head_pose, head_alert, *_ = pipelineHeadTiltPose(frame, face_landmarks)

                # 2. Xử lý qua bộ Tracker lấy ngưỡng động
                eye_data = eye_tracker.process(frame, face_landmarks, w, h)
                mouth_data = mouth_tracker.process(frame, face_landmarks, w, h)

                # ==========================================================
                # LOGIC PHÂN LOẠI THÍCH ỨNG (FALLBACK LOGIC)
                # ==========================================================
                if eye_tracker.calibrated and mouth_tracker.calibrated:
                    # ƯU TIÊN 1: Dùng ngưỡng động thông minh sau khi đã Calibrate xong
                    if head_alert == "DISTRACTED":
                        state = "Distracted"
                    elif head_alert == "DROWSINESS":
                        state = "Drowsiness"
                    elif eye_data["drowsy_alert"]:
                        state = "EyeClosed"
                    elif mouth_data["yawn_alert"]:
                        state = "Yawn"
                else:
                    # ƯU TIÊN 2 (CỨU CÁNH): Nếu video ko giữ thẳng mặt, ép dùng luôn ngưỡng cố định
                    if head_alert == "DISTRACTED":
                        state = "Distracted"
                    elif head_alert == "DROWSINESS":
                        state = "Drowsiness"
                    elif eye_data.get("ear", 1.0) < FIXED_EYE_THRESH:
                        state = "EyeClosed"
                    elif mouth_data.get("mar", 0.0) > FIXED_MAR_THRESH:
                        state = "Yawn"
            else:
                current_ts = time.time()
                eye_tracker.prev_time = current_ts
                mouth_tracker.prev_time = current_ts

            if state in LABELS:
                predictions.append(state)

            processing_times.append(time.time() - start)

    cap.release()

    if len(predictions) == 0:
        return "None"

    return max(set(predictions), key=predictions.count)


# =========================================
# CHARTS GENERATOR
# =========================================
def draw_metrics_chart(accuracy, precision, recall, f1):
    metrics = ["Accuracy", "Precision", "Recall", "F1-score"]
    values = [accuracy * 100, precision * 100, recall * 100, f1 * 100]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(metrics, values, color=['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e'])
    plt.title("System Performance Metrics (Strict 4-Class Matrix)")
    plt.ylabel("Percentage (%)")
    plt.ylim(0, 100)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, h + 1, f"{h:.2f}%", ha='center', fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def draw_confusion_matrix(cm):
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Oranges)
    plt.title("4x4 Confusion Matrix (Sót lỗi tính vào False Negative)")
    plt.colorbar()
    ticks = np.arange(len(LABELS))
    plt.xticks(ticks, LABELS, rotation=45)
    plt.yticks(ticks, LABELS)

    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="white" if cm[i, j] > thresh else "black", fontweight='bold')
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    plt.show()


# =========================================
# MAIN EXECUTION
# =========================================
def main():
    global y_true, y_pred, processing_times

    dataset_path = "Test"

    if not os.path.exists(dataset_path):
        print(f"[ERROR] Thư mục '{dataset_path}' không tồn tại!")
        return

    print("\n========== BẮT ĐẦU ĐÁNH GIÁ (MA TRẬN 4 LỚP NGHIÊM NGẶT) ==========\n")

    for label in os.listdir(dataset_path):
        label_path = os.path.join(dataset_path, label)

        if not os.path.isdir(label_path):
            continue

        if label not in LABELS:
            continue

        print(f"\n▶️ THƯ MỤC THẬT (TRUE LABEL): {label}")

        for video in os.listdir(label_path):
            if not video.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                continue

            video_path = os.path.join(label_path, video)
            print(f" -> Đang xử lý: {video}")

            pred = evaluate_video(video_path)
            print(f"    Dự đoán hệ thống: {pred}")

            y_true.append(label)
            
            if pred == "None":
                y_pred.append("Sot_Loi_Chua_Phan_Loai")
            else:
                y_pred.append(pred)

    if not y_true:
        print("[WARNING] Không có dữ liệu để đánh giá.")
        return

    # Tính toán chỉ số tổng quan
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
    recall = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)

    # ĐO HIỆU NĂNG PHẦN CỨNG (FPS & LATENCY)
    total_time = sum(processing_times)
    total_processed_frames = len(processing_times)
    fps = total_processed_frames / total_time if total_time > 0 else 0
    latency = (total_time / total_processed_frames) * 1000 if total_processed_frames > 0 else 0

    print("\n" + "=" * 40 + "\n          KẾT QUẢ CHUNG          \n" + "=" * 40)
    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"F1-score  : {f1 * 100:.2f}%")
    print("-" * 40)
    print(f"Tốc độ xử lý (FPS)   : {fps:.2f} khung hình/giây")
    print(f"Độ trễ trung bình     : {latency:.2f} ms mỗi khung hình")
    print(f"Tổng số khung hình test: {total_frames}")

    print("\n" + "=" * 40 + "\n       BÁO CÁO CHI TIẾT PHÂN LỚP     \n" + "=" * 40)
    print(classification_report(y_true, y_pred, labels=LABELS, zero_division=0))

    print("\n" + "=" * 40 + "\n        CHỈ SỐ TỪNG NHÃN (CHI TIẾT)       \n" + "=" * 40)
    rows = []
    for i, label in enumerate(LABELS):
        TP = cm[i, i]
        FP = np.sum(cm[:, i]) - TP
        FN = np.sum(np.array(y_true) == label) - TP 

        precision_c = TP / (TP + FP) if (TP + FP) else 0
        recall_c = TP / (TP + FN) if (TP + FN) else 0
        f1_c = (2 * precision_c * recall_c / (precision_c + recall_c)) if (precision_c + recall_c) else 0

        rows.append([label, TP, FP, FN, f"{precision_c * 100:.1f}%", f"{recall_c * 100:.1f}%", f"{f1_c * 100:.1f}%"])

    df = pd.DataFrame(rows, columns=["Label", "TP", "FP", "FN", "Precision", "Recall", "F1-score"])
    print(df.to_string(index=False))

    draw_metrics_chart(accuracy, precision, recall, f1)
    draw_confusion_matrix(cm)


if __name__ == "__main__":
    main()