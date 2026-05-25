import cv2
import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import mediapipe as mp

from utils.g_helper import bgr2rgb, mirrorImage
from detection.head_pose import pipelineHeadTiltPose, draw_face_bbox_fp
from detection.eye import EyeTracker
from detection.mouth import MouthTracker
from config.config import load_config
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont

# Tải cấu hình từ hệ thống
config = load_config()

DROWSY_EYE_TIME = config["eye"]["drowsy_time"]
MAR_THRESHOLD = config["mouth"]["mar_threshold"]
YAWN_TIME = config["mouth"]["yawn_time"]
MICROSLEEP_TIME = config["time"]["microsleep_time"]
DISTRACTED_TIME = config["time"]["distracted_time"]

mp_face_mesh = mp.solutions.face_mesh


class VideoThread(QThread):

    change_pixmap_signal = pyqtSignal(np.ndarray)
    data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._run_flag = False
        self._pause = False
        self.cap = None
        self.is_webcam = False

        # =========================
        # FPS
        # =========================
        self.fps = 0.0
        self.prev_frame_time = time.time()

        # =========================
        # TRACKERS
        # =========================
        self.eye = EyeTracker()
        self.mouth = MouthTracker()

    def _reset_trackers_for_calibration(self):
        """Reset toàn bộ calibration"""

        # Reset eye
        self.eye.calibrated = False

        if hasattr(self.eye, 'ear_buffer'):
            self.eye.ear_buffer.clear()

        elif hasattr(self.eye, 'buffer'):
            self.eye.buffer.clear()

        # Reset mouth
        self.mouth.calibrated = False

        if hasattr(self.mouth, 'mar_buffer'):
            self.mouth.mar_buffer.clear()

        elif hasattr(self.mouth, 'buffer'):
            self.mouth.buffer.clear()

        # Reset timers
        self.eye.eye_closed_time = 0.0
        self.mouth.mouth_open_time = 0.0

    # =========================
    # START CAMERA
    # =========================
    def start_camera(self):

        self._reset_trackers_for_calibration()

        self.cap = cv2.VideoCapture(0)

        self.is_webcam = True
        self._run_flag = True

        self.start()

    # =========================
    # START VIDEO
    # =========================
    def start_video(self, path):

        self._reset_trackers_for_calibration()

        self.cap = cv2.VideoCapture(path)

        self.is_webcam = False
        self._run_flag = True

        self.start()

    # =========================
    # STOP
    # =========================
    def stop(self):

        self._run_flag = False

        if self.cap:
            self.cap.release()

    # =========================
    # PAUSE
    # =========================
    def pause(self):
        self._pause = True

    def resume(self):
        self._pause = False

    # =========================
    # MAIN LOOP
    # =========================
    def run(self):

        fps_limit = self.cap.get(cv2.CAP_PROP_FPS)

        if fps_limit <= 0:
            fps_limit = 25

        frame_time = 1.0 / fps_limit

        with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:

            while self._run_flag:

                if self._pause:
                    QThread.msleep(50)
                    continue

                # =========================
                # FRAME TIMER
                # =========================
                start_time = time.time()

                ret, frame = self.cap.read()

                if not ret:
                    break

                if self.is_webcam:
                    frame = mirrorImage(frame)

                # =========================
                # FPS REALTIME
                # =========================
                current_time = time.time()

                delta = current_time - self.prev_frame_time

                self.prev_frame_time = current_time

                if delta > 0:

                    current_fps = 1.0 / delta

                    # Smooth FPS
                    self.fps = (
                        0.9 * self.fps
                        + 0.1 * current_fps
                    )

                # =========================
                # FACE MESH
                # =========================
                results = face_mesh.process(bgr2rgb(frame))

                drowsy_alert = False
                yawn_alert = False

                EAR = 0.0
                MAR = 0.0

                eye_closed_time = 0.0
                mouth_open_time = 0.0

                eye_threshold_display = "N/A"
                mouth_threshold_display = "N/A"

                head_pose = "-"
                head_alert = ""

                x = y = z = 0.0

                head_time = 0.0
                distract_time = 0.0

                # =========================
                # FACE DETECTED
                # =========================
                if results.multi_face_landmarks:

                    face_landmarks = results.multi_face_landmarks[0]

                    h, w, _ = frame.shape

                    # =========================
                    # FACE BOX
                    # =========================
                    draw_face_bbox_fp(
                        frame,
                        face_landmarks,
                        w,
                        h
                    )

                    # =========================
                    # HEAD POSE
                    # =========================
                    head_pose, head_alert, x, y, z, head_time, distract_time = pipelineHeadTiltPose(
                        frame,
                        face_landmarks
                    )

                    # =========================
                    # EYE TRACKING
                    # =========================
                    eye_data = self.eye.process(
                        frame,
                        face_landmarks,
                        w,
                        h
                    )

                    eye_closed_time = eye_data["eye_closed_time"]
                    drowsy_alert = eye_data["drowsy_alert"]
                    EAR = eye_data["ear"]
                    eye_threshold_display = eye_data["threshold"]

                    # =========================
                    # MOUTH TRACKING
                    # =========================
                    mouth_data = self.mouth.process(
                        frame,
                        face_landmarks,
                        w,
                        h
                    )

                    mouth_open_time = mouth_data["mouth_open_time"]
                    yawn_alert = mouth_data["yawn_alert"]
                    MAR = mouth_data["mar"]
                    mouth_threshold_display = mouth_data["threshold"]

                    # =========================
                    # CALIBRATION
                    # =========================
                    if not self.eye.calibrated or not self.mouth.calibrated:

                        status = "CALIBRATING..."

                        progress = int(
                            (len(self.eye.ear_buffer) / 45) * 100
                        )

                        cv2.rectangle(
                            frame,
                            (10, 10),
                            (460, 50),
                            (0, 0, 0),
                            -1
                        )

                        cv2.putText(
                            frame,
                            f"CALIBRATING SYSTEM: {progress}%",
                            (20, 38),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.65,
                            (0, 255, 255),
                            2
                        )

                        cv2.putText(
                            frame,
                            "Please look straight and keep a neutral face",
                            (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            1
                        )

                    else:

                        if drowsy_alert:
                            status = "EYES CLOSED"

                        elif yawn_alert:
                            status = "YAWN"

                        else:
                            status = "AWAKE"

                        cv2.putText(
                            frame,
                            "SYSTEM: READY",
                            (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 0, 255),
                            1
                        )

                # =========================
                # NO FACE
                # =========================
                else:

                    status = "NO FACE"

                    current_ts = time.time()

                    self.eye.prev_time = current_ts
                    self.mouth.prev_time = current_ts

                    self.eye.eye_closed_time = 0.0
                    self.mouth.mouth_open_time = 0.0

                # =========================
                # DRAW FPS (TOP RIGHT)
                # =========================
                fps_text = f"FPS: {self.fps:.1f}"

                # Lấy kích thước text
                (text_w, text_h), _ = cv2.getTextSize(
                    fps_text,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    2
                )

                # Vị trí góc phải
                x_pos = frame.shape[1] - text_w - 20
                y_pos = 35

                cv2.putText(
                    frame,
                    fps_text,
                    (x_pos, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

                # =========================
                # SEND DATA
                # =========================
                self.data_signal.emit({

                    "ear": round(EAR, 2),
                    "ear_time": round(eye_closed_time, 2),
                    "eye_time": round(eye_closed_time, 2),
                    "eye_threshold": eye_threshold_display,

                    "mar": round(MAR, 2),
                    "mar_time": round(mouth_open_time, 2),
                    "mouth_threshold": mouth_threshold_display,

                    "yawn_alert": yawn_alert,
                    "status": status,

                    "head": head_pose,
                    "head_alert": head_alert,
                    "head_time": round(head_time, 2),
                    "focus_time": distract_time,

                    "x": round(x, 2),
                    "y": round(y, 2),
                    "z": round(z, 2),

                    "fps": round(self.fps, 1)
                })

                # =========================
                # UPDATE FRAME
                # =========================
                self.change_pixmap_signal.emit(frame)

                # =========================
                # FPS LIMIT
                # =========================
                elapsed = time.time() - start_time

                remaining = frame_time - elapsed

                if remaining > 0:
                    QThread.msleep(int(remaining * 1000))