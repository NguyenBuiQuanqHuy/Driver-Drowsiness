import os
import cv2
import time
import numpy as np
from collections import Counter

import mediapipe as mp

from detection.eye import process_eye_state
from detection.mouth import process_mouth_state
from detection.head_pose import pipelineHeadTiltPose

from config.config import *


class PerformanceEvaluator:

    def __init__(self):

        self.labels = [
            "AWAKE",
            "YAWN",
            "EYES CLOSED",
            "MICROSLEEP",
            "DISTRACTED"
        ]

    # =============================================
    # RUN WHOLE DATASET
    # =============================================

    def evaluate_dataset(self, dataset_path):

        results = []

        folder_map = {
            "Awake": "AWAKE",
            "Yawn": "YAWN",
            "EyeClosed": "EYES CLOSED",
            "Microsleep": "MICROSLEEP",
            "Distracted": "DISTRACTED"
        }

        for folder_name in os.listdir(dataset_path):

            folder_path = os.path.join(dataset_path, folder_name)

            if not os.path.isdir(folder_path):
                continue

            ground_truth = folder_map.get(folder_name)

            if ground_truth is None:
                continue

            for file in os.listdir(folder_path):

                if not file.lower().endswith((".mp4", ".avi", ".mov")):
                    continue

                video_path = os.path.join(folder_path, file)

                result = self.evaluate_video(
                    video_path,
                    ground_truth
                )

                results.append(result)

        return results

    # =============================================
    # EVALUATE SINGLE VIDEO
    # =============================================

    def evaluate_video(self, video_path, ground_truth):

        cap = cv2.VideoCapture(video_path)

        fps_list = []
        process_times = []

        eye_closed_time = 0
        mouth_open_time = 0

        prediction_history = []

        total_frames = 0

        mp_face_mesh = mp.solutions.face_mesh

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

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = face_mesh.process(rgb)

                status = "AWAKE"

                if results.multi_face_landmarks:

                    face_landmarks = results.multi_face_landmarks[0]

                    h, w, _ = frame.shape

                    # =========================
                    # HEAD POSE
                    # =========================

                    head_pose, head_alert, _, _, _, _, _ = \
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
                    # FINAL STATUS
                    # =========================

                    if head_alert == "MICROSLEEP":
                        status = "MICROSLEEP"

                    elif head_alert == "DISTRACTED":
                        status = "DISTRACTED"

                    elif drowsy_alert:
                        status = "EYES CLOSED"

                    elif yawn_alert:
                        status = "YAWN"

                    else:
                        status = "AWAKE"

                prediction_history.append(status)

                elapsed = time.time() - start

                process_times.append(elapsed)

                if elapsed > 0:
                    fps_list.append(1 / elapsed)

        cap.release()

        # =========================================
        # DOMINANT PREDICTION
        # =========================================

        if len(prediction_history) > 0:
            prediction = Counter(prediction_history).most_common(1)[0][0]
        else:
            prediction = "AWAKE"

        avg_fps = np.mean(fps_list) if fps_list else 0

        avg_process_time = np.mean(process_times) if process_times else 0

        max_process_time = np.max(process_times) if process_times else 0

        return {
            "video": os.path.basename(video_path),
            "ground_truth": ground_truth,
            "prediction": prediction,
            "avg_fps": round(avg_fps, 2),
            "avg_process_time": round(avg_process_time * 1000, 2),
            "max_process_time": round(max_process_time * 1000, 2),
            "total_frames": total_frames
        }