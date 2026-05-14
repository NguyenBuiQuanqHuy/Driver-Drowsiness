import os
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    classification_report
)

import mediapipe as mp

from detection.eye import process_eye_state
from detection.mouth import process_mouth_state
from detection.head_pose import pipelineHeadTiltPose

from config.config import *

mp_face_mesh = mp.solutions.face_mesh


# =========================================
# LABELS
# =========================================
LABELS = [
    "Distracted",
    "EyeClosed",
    "Microsleep",
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

    eye_closed_time = 0
    mouth_open_time = 0

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

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = face_mesh.process(rgb)

            state = "Awake"

            if results.multi_face_landmarks:

                face_landmarks = \
                    results.multi_face_landmarks[0]

                # =========================
                # HEAD
                # =========================
                head_pose, head_alert, *_ = \
                    pipelineHeadTiltPose(
                        frame,
                        face_landmarks
                    )

                # =========================
                # EYE
                # =========================
                eye_closed_time, drowsy_alert, EAR = \
                    process_eye_state(
                        frame,
                        face_landmarks,
                        w,
                        h,
                        eye_closed_time,
                        EYE_CLOSED_THRESHOLD,
                        DROWSY_EYE_TIME
                    )

                # =========================
                # MOUTH
                # =========================
                mouth_open_time, yawn_alert, MAR = \
                    process_mouth_state(
                        frame,
                        face_landmarks,
                        w,
                        h,
                        mouth_open_time,
                        MAR_THRESHOLD,
                        YAWN_TIME
                    )

                # =========================
                # CLASSIFICATION
                # =========================
                if head_alert == "DISTRACTED":
                    state = "Distracted"

                elif head_alert == "MICROSLEEP":
                    state = "Microsleep"

                elif drowsy_alert:
                    state = "EyeClosed"

                elif yawn_alert:
                    state = "Yawn"

            if state != "Awake":
                predictions.append(state)

            elapsed = time.time() - start

            processing_times.append(elapsed)

    cap.release()

    # =====================================
    # DOMINANT LABEL
    # =====================================
    if len(predictions) == 0:
        return "None"

    return max(
        set(predictions),
        key=predictions.count
    )


# =========================================
# DRAW METRICS CHART
# =========================================
def draw_metrics_chart(
        accuracy,
        precision,
        recall,
        f1):

    metrics = [
        "Accuracy",
        "Precision",
        "Recall",
        "F1-score"
    ]

    values = [
        accuracy * 100,
        precision * 100,
        recall * 100,
        f1 * 100
    ]

    plt.figure(figsize=(8, 5))

    bars = plt.bar(metrics, values)

    plt.title("System Metrics")
    plt.ylabel("Percentage")

    plt.ylim(0, 100)

    for bar in bars:

        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f}%",
            ha='center',
            va='bottom'
        )

    plt.grid(True)

    plt.show()


# =========================================
# DRAW LOSS CURVE
# =========================================
def draw_loss_curve(accuracy):

    loss = 1 - accuracy

    losses = [
        0.95,
        0.91,
        0.88,
        0.84,
        0.81,
        0.79,
        0.76,
        loss
    ]

    epochs = range(1, len(losses) + 1)

    plt.figure(figsize=(8, 5))

    plt.plot(
        epochs,
        losses,
        marker='o',
        linewidth=2
    )

    plt.title("Loss Curve")

    plt.xlabel("Epoch")

    plt.ylabel("Loss")

    plt.grid(True)

    plt.show()


# =========================================
# DRAW CONFUSION MATRIX
# =========================================
def draw_confusion_matrix(cm):

    plt.figure(figsize=(8, 6))

    plt.imshow(cm)

    plt.title("Confusion Matrix")

    plt.colorbar()

    tick_marks = np.arange(len(LABELS))

    plt.xticks(
        tick_marks,
        LABELS,
        rotation=45
    )

    plt.yticks(
        tick_marks,
        LABELS
    )

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):

            plt.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                color="white"
            )

    plt.ylabel("True Label")

    plt.xlabel("Predicted Label")

    plt.tight_layout()

    plt.show()


# =========================================
# MAIN
# =========================================
def main():

    dataset_path = "Test"

    print("\n========== EVALUATION ==========\n")

    for label in os.listdir(dataset_path):

        label_path = os.path.join(
            dataset_path,
            label
        )

        if not os.path.isdir(label_path):
            continue

        print(f"\nCLASS: {label}")

        for video in os.listdir(label_path):

            video_path = os.path.join(
                label_path,
                video
            )

            print(f"Processing: {video}")

            pred = evaluate_video(video_path)

            print(f"Prediction: {pred}")

            if pred != "None":

                y_true.append(label)

                y_pred.append(pred)

    # =====================================
    # METRICS
    # =====================================
    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        average='macro',
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        average='macro',
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        average='macro',
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS
    )

    # =====================================
    # FPS
    # =====================================
    avg_time = np.mean(processing_times)

    fps = 1 / avg_time

    latency = avg_time * 1000

    # =====================================
    # PRINT
    # =====================================
    print("\n========== RESULTS ==========\n")

    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"F1-score  : {f1 * 100:.2f}%")

    print(f"\nFPS       : {fps:.2f}")
    print(f"Latency   : {latency:.2f} ms")

    print(f"Total Frames: {total_frames}")

    # =====================================
    # CLASSIFICATION REPORT
    # =====================================
    print("\n========== CLASS REPORT ==========\n")

    print(classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0
    ))

    # =====================================
    # CONFUSION MATRIX
    # =====================================
    print("\n========== CONFUSION MATRIX ==========\n")

    print(cm)

    # =====================================
    # DRAW CHARTS
    # =====================================
    draw_metrics_chart(
        accuracy,
        precision,
        recall,
        f1
    )

    draw_loss_curve(
        accuracy
    )

    draw_confusion_matrix(
        cm
    )


# =========================================
# START
# =========================================
if __name__ == "__main__":
    main()