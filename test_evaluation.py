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

# IMPORT ĐỂ RESET TIMER GLOBAL
import detection.head_pose as hp
from detection.head_pose import pipelineHeadTiltPose

from config.config import load_config

config = load_config()
mp_face_mesh = mp.solutions.face_mesh


# =========================================
# LABELS
# =========================================
LABELS = [
    "Distracted",
    "EyeClosed",
    "Drowsiness",
    "Yawn",
    "Unknown"
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

    if not cap.isOpened():
        print(f"[ERROR] Không mở được video: {video_path}")
        return "Unknown"

    # =========================================
    # RESET GLOBAL TIMER HEAD POSE
    # =========================================
    hp.prev_time = time.time()
    hp.down_time = 0
    hp.distract_time = 0

    # =========================================
    # FPS LIMIT GIỐNG HỆ THỐNG THẬT
    # =========================================
    fps_limit = cap.get(cv2.CAP_PROP_FPS)

    if fps_limit <= 0:
        fps_limit = 25

    frame_time = 1.0 / fps_limit

    # =========================================
    # TRACKERS
    # =========================================
    eye_tracker = EyeTracker()
    mouth_tracker = MouthTracker()

    # =========================================
    # FALLBACK THRESHOLD
    # =========================================
    FIXED_EYE_THRESH = config["eye"]["closed_threshold"]
    FIXED_MAR_THRESH = config["mouth"]["mar_threshold"]

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

            state = "Unknown"

            # =========================================
            # FACE DETECTED
            # =========================================
            if results.multi_face_landmarks:

                face_landmarks = results.multi_face_landmarks[0]

                # =========================================
                # HEAD POSE
                # =========================================
                head_pose, head_alert, *_ = pipelineHeadTiltPose(
                    frame,
                    face_landmarks
                )

                # =========================================
                # EYE TRACKER
                # =========================================
                eye_data = eye_tracker.process(
                    frame,
                    face_landmarks,
                    w,
                    h
                )

                # =========================================
                # MOUTH TRACKER
                # =========================================
                mouth_data = mouth_tracker.process(
                    frame,
                    face_landmarks,
                    w,
                    h
                )

                # =========================================
                # CLASSIFICATION LOGIC
                # =========================================
                if eye_tracker.calibrated and mouth_tracker.calibrated:

                    # ƯU TIÊN 1
                    if head_alert == "DISTRACTED":
                        state = "Distracted"

                    elif head_alert == "DROWSINESS":
                        state = "Drowsiness"

                    elif eye_data["drowsy_alert"]:
                        state = "EyeClosed"

                    elif mouth_data["yawn_alert"]:
                        state = "Yawn"

                else:

                    # ƯU TIÊN 2 (FALLBACK)
                    if head_alert == "DISTRACTED":
                        state = "Distracted"

                    elif head_alert == "DROWSINESS":
                        state = "Drowsiness"

                    elif eye_data.get("ear", 1.0) < FIXED_EYE_THRESH:
                        state = "EyeClosed"

                    elif mouth_data.get("mar", 0.0) > FIXED_MAR_THRESH:
                        state = "Yawn"

            # =========================================
            # NO FACE
            # =========================================
            else:

                current_ts = time.time()

                eye_tracker.prev_time = current_ts
                mouth_tracker.prev_time = current_ts

                eye_tracker.eye_closed_time = 0.0
                mouth_tracker.mouth_open_time = 0.0

            # =========================================
            # SAVE PREDICTION
            # =========================================
            predictions.append(state)

            # =========================================
            # GIẢ LẬP REALTIME
            # =========================================
            elapsed = time.time() - start

            remaining = frame_time - elapsed

            if remaining > 0:
                time.sleep(remaining)

            # =========================================
            # FPS THỰC TẾ HỆ THỐNG
            # =========================================
            total_loop_time = time.time() - start

            processing_times.append(total_loop_time)

    cap.release()

    if len(predictions) == 0:
        return "Unknown"

    # =========================================
    # MAJORITY VOTING
    # =========================================
    predictions = [p for p in predictions if p != "Unknown"]

    if len(predictions) == 0:
        return "Unknown"

    return max(set(predictions), key=predictions.count)


# =========================================
# CHARTS GENERATOR
# =========================================
def draw_metrics_chart(accuracy, precision, recall, f1):

    metrics = ["Accuracy", "Precision", "Recall", "F1-score"]

    values = [
        accuracy * 100,
        precision * 100,
        recall * 100,
        f1 * 100
    ]

    plt.figure(figsize=(8, 5))

    bars = plt.bar(
        metrics,
        values,
        color=[
            '#4e73df',
            '#1cc88a',
            '#36b9cc',
            '#f6c23e'
        ]
    )

    plt.title("System Performance Metrics")
    plt.ylabel("Percentage (%)")
    plt.ylim(0, 100)

    for bar in bars:

        h = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1,
            f"{h:.2f}%",
            ha='center',
            fontweight='bold'
        )

    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


def draw_confusion_matrix(cm):

    plt.figure(figsize=(8, 6))

    plt.imshow(
        cm,
        interpolation='nearest',
        cmap=plt.cm.Oranges
    )

    plt.title("Confusion Matrix")
    plt.colorbar()

    ticks = np.arange(len(LABELS))

    plt.xticks(ticks, LABELS, rotation=45)
    plt.yticks(ticks, LABELS)

    thresh = cm.max() / 2.0 if cm.max() > 0 else 1

    for i in range(cm.shape[0]):

        for j in range(cm.shape[1]):

            plt.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontweight='bold'
            )

    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    plt.tight_layout()
    plt.show()


# =========================================
# MAIN EXECUTION
# =========================================
def main():

    global y_true
    global y_pred
    global processing_times

    dataset_path = "Test"

    if not os.path.exists(dataset_path):
        print(f"[ERROR] Thư mục '{dataset_path}' không tồn tại!")
        return

    print("\n========== BẮT ĐẦU ĐÁNH GIÁ ==========\n")

    # =========================================
    # LOOP TỪNG NHÃN
    # =========================================
    for label in os.listdir(dataset_path):

        label_path = os.path.join(dataset_path, label)

        if not os.path.isdir(label_path):
            continue

        if label not in LABELS:
            continue

        if label == "Unknown":
            continue

        print("\n" + "=" * 60)
        print(f"TRUE LABEL: {label}")
        print("=" * 60)

        # =========================================
        # TABLE CHO RIÊNG FOLDER
        # =========================================
        folder_rows = []

        stt = 1

        for video in os.listdir(label_path):

            if not video.lower().endswith(
                    ('.mp4', '.avi', '.mov', '.mkv')):
                continue

            video_path = os.path.join(label_path, video)

            print(f"\n -> Đang xử lý: {video}")

            pred = evaluate_video(video_path)

            print(f"    Dự đoán hệ thống: {pred}")

            # =========================================
            # SAVE LABELS
            # =========================================
            y_true.append(label)
            y_pred.append(pred)

            # =========================================
            # TP FP FN CHO TỪNG VIDEO
            # =========================================
            TP = 1 if pred == label else 0

            FP = 1 if (
                pred != label and
                pred in LABELS
            ) else 0

            FN = 1 if pred != label else 0

            folder_rows.append([
                stt,
                video,
                pred,
                TP,
                FP,
                FN
            ])

            stt += 1

        # =========================================
        # IN BẢNG CHO FOLDER HIỆN TẠI
        # =========================================
        folder_df = pd.DataFrame(
            folder_rows,
            columns=[
                "STT",
                "Video",
                "Predict",
                "TP",
                "FP",
                "FN"
            ]
        )

        print("\n")
        print(folder_df.to_string(index=False))

    if not y_true:
        print("[WARNING] Không có dữ liệu để đánh giá.")
        return

    # =========================================
    # METRICS
    # =========================================
    accuracy = accuracy_score(y_true, y_pred)

    precision = precision_score(
        y_true,
        y_pred,
        labels=LABELS,
        average='macro',
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        labels=LABELS,
        average='macro',
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        labels=LABELS,
        average='macro',
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS
    )

    # =========================================
    # PERFORMANCE
    # =========================================
    total_time = sum(processing_times)

    total_processed_frames = len(processing_times)

    fps = (
        total_processed_frames / total_time
        if total_time > 0 else 0
    )

    latency = (
        (total_time / total_processed_frames) * 1000
        if total_processed_frames > 0 else 0
    )

    # =========================================
    # SUMMARY
    # =========================================
    print("\n" + "=" * 60)
    print("KẾT QUẢ CHUNG")
    print("=" * 60)

    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"F1-score  : {f1 * 100:.2f}%")

    print("-" * 60)

    print(f"Tốc độ xử lý (FPS) : {fps:.2f}")
    print(f"Độ trễ trung bình  : {latency:.2f} ms")
    print(f"Tổng frame test    : {total_frames}")

    # =========================================
    # CLASSIFICATION REPORT
    # =========================================
    print("\n" + "=" * 60)
    print("BÁO CÁO PHÂN LỚP")
    print("=" * 60)

    print(classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0
    ))

    # =========================================
    # DETAIL TABLE THEO NHÃN
    # =========================================
    print("\n" + "=" * 60)
    print("CHI TIẾT TỪNG NHÃN")
    print("=" * 60)

    rows = []

    for i, label in enumerate(LABELS):

        TP = cm[i, i]

        FP = np.sum(cm[:, i]) - TP

        FN = np.sum(cm[i, :]) - TP

        precision_c = TP / (TP + FP) if (TP + FP) else 0

        recall_c = TP / (TP + FN) if (TP + FN) else 0

        f1_c = (
            2 * precision_c * recall_c /
            (precision_c + recall_c)
        ) if (precision_c + recall_c) else 0

        rows.append([
            label,
            TP,
            FP,
            FN,
            f"{precision_c * 100:.1f}%",
            f"{recall_c * 100:.1f}%",
            f"{f1_c * 100:.1f}%"
        ])

    df = pd.DataFrame(
        rows,
        columns=[
            "Label",
            "TP",
            "FP",
            "FN",
            "Precision",
            "Recall",
            "F1-score"
        ]
    )

    print(df.to_string(index=False))

    # =========================================
    # DRAW CHARTS
    # =========================================
    draw_metrics_chart(
        accuracy,
        precision,
        recall,
        f1
    )

    draw_confusion_matrix(cm)


if __name__ == "__main__":
    main()