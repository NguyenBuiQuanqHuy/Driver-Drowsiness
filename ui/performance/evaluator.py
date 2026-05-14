# core/evaluator.py

import os
import cv2
import time
import numpy as np
import mediapipe as mp

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix
)

from detection.eye import process_eye_state
from detection.mouth import process_mouth_state
from detection.head_pose import pipelineHeadTiltPose
from config.config import *


mp_face_mesh = mp.solutions.face_mesh


LABELS = ["Distracted", "EyeClosed", "Microsleep", "Yawn"]


class PerformanceEvaluator:

    def __init__(self):
        self.y_true = []
        self.y_pred = []
        self.processing_times = []
        self.total_frames = 0

    # =====================================
    def evaluate_video(self, video_path):

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

                self.total_frames += 1

                h, w, _ = frame.shape
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = face_mesh.process(rgb)

                state = "Awake"

                if results.multi_face_landmarks:

                    face_landmarks = results.multi_face_landmarks[0]

                    _, head_alert, *_ = pipelineHeadTiltPose(frame, face_landmarks)

                    eye_closed_time, drowsy_alert, _ = process_eye_state(
                        frame, face_landmarks, w, h,
                        eye_closed_time,
                        EYE_CLOSED_THRESHOLD,
                        DROWSY_EYE_TIME
                    )

                    mouth_open_time, yawn_alert, _ = process_mouth_state(
                        frame, face_landmarks, w, h,
                        mouth_open_time,
                        MAR_THRESHOLD,
                        YAWN_TIME
                    )

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

                self.processing_times.append(time.time() - start)

        cap.release()

        if len(predictions) == 0:
            return "None"

        return max(set(predictions), key=predictions.count)

    # =====================================
    def run_dataset(self, dataset_path="Test"):

        self.y_true = []
        self.y_pred = []
        self.processing_times = []
        self.total_frames = 0

        for label in os.listdir(dataset_path):

            label_path = os.path.join(dataset_path, label)

            if not os.path.isdir(label_path):
                continue

            for video in os.listdir(label_path):

                video_path = os.path.join(label_path, video)

                pred = self.evaluate_video(video_path)

                if pred != "None":
                    self.y_true.append(label)
                    self.y_pred.append(pred)

        accuracy = accuracy_score(self.y_true, self.y_pred)
        precision = precision_score(self.y_true, self.y_pred, average="macro", zero_division=0)
        recall = recall_score(self.y_true, self.y_pred, average="macro", zero_division=0)
        f1 = f1_score(self.y_true, self.y_pred, average="macro", zero_division=0)

        cm = confusion_matrix(self.y_true, self.y_pred, labels=LABELS)

        avg_time = np.mean(self.processing_times)
        fps = 1 / avg_time if avg_time > 0 else 0
        latency = avg_time * 1000 if avg_time > 0 else 0

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "fps": fps,
            "latency": latency,
            "cm": cm
        }