import cv2
import time
import numpy as np
from config.config import *
from PyQt5.QtCore import *
import mediapipe as mp

from utils.g_helper import bgr2rgb, mirrorImage
from detection.head_pose import pipelineHeadTiltPose, draw_face_bbox_fp
from detection.eye import process_eye_state
from detection.mouth import process_mouth_state
from config.config import *

mp_face_mesh = mp.solutions.face_mesh

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._run_flag = False
        self._pause = False
        self.cap = None

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self._run_flag = True
        self.start()

    def start_video(self, path):
        self.cap = cv2.VideoCapture(path)
        self._run_flag = True
        self.start()

    def stop(self):
        self._run_flag = False
        if self.cap:
            self.cap.release()

    def pause(self):
        self._pause = True

    def resume(self):
        self._pause = False

    def run(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 25

        frame_time = 1.0 / fps  # giây mỗi frame

        eye_closed_time = 0
        mouth_open_time = 0

        with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:

            while self._run_flag:
                if self._pause:
                    QThread.msleep(50)
                    continue

                start_time = time.time()  # Bắt đầu đo thời gian xử lý

                ret, frame = self.cap.read()
                if not ret:
                    break

                frame = mirrorImage(frame)
                results = face_mesh.process(bgr2rgb(frame))

                drowsy_alert = False
                yawn_alert = False

                EAR = 0
                MAR = 0
                head_pose = "-"
                head_alert = ""
                x = y = z = 0
                head_time = 0
                distract_time = 0

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        h, w, _ = frame.shape

                        draw_face_bbox_fp(frame, face_landmarks, w, h)

                        head_pose, head_alert, x, y, z, head_time, distract_time = pipelineHeadTiltPose(
                            frame, face_landmarks
                        )

                        eye_closed_time, drowsy_alert, EAR = process_eye_state(
                            frame, face_landmarks, w, h,
                            eye_closed_time,
                            EYE_CLOSED_THRESHOLD, DROWSY_EYE_TIME
                        )

                        mouth_open_time, yawn_alert, MAR = process_mouth_state(
                            frame, face_landmarks, w, h,
                            mouth_open_time,
                            MAR_THRESHOLD, YAWN_TIME
                        )

                    if drowsy_alert:
                        status = "EYES CLOSED"
                    elif yawn_alert:
                        status = "YAWN"
                    else:
                        status = "AWAKE"
                else:
                    status = "NO FACE"
                    eye_closed_time = 0
                    mouth_open_time = 0
                    head_time = 0
                    distract_time = 0

                self.data_signal.emit({
                    "ear": round(EAR, 2),
                    "ear_time": round(eye_closed_time, 2),

                    "eye_time": round(eye_closed_time, 2),

                    "mar": round(MAR, 2),
                    "mar_time": round(mouth_open_time, 2),

                    "yawn_alert": yawn_alert,
                    "status": status,

                    "head": head_pose,
                    "head_alert": head_alert,
                    "head_time": round(head_time, 2),
                    "focus_time": distract_time,

                    "x": round(x, 2),
                    "y": round(y, 2),
                    "z": round(z, 2)
                })

                self.change_pixmap_signal.emit(frame)

                # Tính thời gian còn lại cần sleep để đúng FPS
                elapsed = time.time() - start_time
                remaining = frame_time - elapsed

                if remaining > 0:
                    QThread.msleep(int(remaining * 1000))
                # Nếu remaining <= 0: xử lý quá lâu, đọc frame tiếp luôn